import os
import os.path
import logging
import re
import sys
import mastodon.streaming
from collections import defaultdict
import pprint

# from multiprocessing import Pool

from .client import Client
from .logo_runner import LogoRunner

from html.parser import HTMLParser


class Bot:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("bot")
        self.client = Client(
            user_agent=config.user_agent,
            api_base_url=config.api_base_url,
            client_id=config.client_key,
            client_secret=config.client_secret,
            access_token=config.access_token,
            debug_requests=config.debug_requests,
        )
        self.listener = StreamListener(bot=self, client=self.client)

    def run_streaming(self):
        self.logger.info("Listening to notifications stream...")
        self.client.stream_user(listener=self.listener)

    def poll_notifications(self):
        notifications = self.client.notifications(
            mentions_only=True
        )
        for notification in notifications:
            try:
                self.handle_notification(notification)
                self.logger.debug(f"Dismissing notification {notification['id']}")
                self.client.notifications_dismiss(notification["id"])
            except:
                e = sys.exc_info()[0]
                self.logger.error(f"Failed to handle notification: {e}")

    def handle_notification(self, notification):
        # Only handle mentions from notifications
        type = notification["type"]
        if type != "mention":
            return

        # Don't respond to accounts marked as bots
        account = notification["account"]
        bot = account["bot"]
        if bot:
            return

        status = notification["status"]
        status_id = status["id"]

        # Ignore mentions without s content warning
        spoiler_text = status["spoiler_text"]
        if spoiler_text == "":
            return
        
        # Ignore non-public mentions
        visibility = status["visibility"]
        if visibility != "public":
            return

        # Parse the status HTML for cleanup and source extraction
        content_html = status["content"]
        parser = ProgramSourceHTMLParser(logger=self.logger)
        parser.feed(content_html)
        if not parser.found_logo_hashtag:
            return
        
        acct = account["acct"]
        
        program_source = parser.get_text()
        if program_source == "":
            status_result = self.client.status_post(
                f"@{acct} Sorry, I couldn't find a program in your toot! 😔",
                in_reply_to_id=status_id,
            )
            self.logger.debug(f"Posted status id={status_result['id']}")
            return

        self.logger.debug(
            f"Notification id={id} acct={acct} content={program_source} spoiler={spoiler_text} raw={content_html}")

        runner = LogoRunner(
            id=status_id,
            source=program_source,
            config=self.config,
            logger=self.logger
        )
        runner.run()

        self.logger.debug(
            f"Posting media from {runner.output_video_filename} with {program_source}")
        media_result = self.client.media_post(
            runner.output_video_filename,
            "video/mp4",
            synchronous=True,
            description=program_source,
            focus=(0, 0),
        )

        status_result = self.client.status_post(
            f"@{acct} I ran your #logo program, {spoiler_text}, and here's what happened!",
            in_reply_to_id=status_id,
            media_ids=[media_result["id"]],
            idempotency_key=None,
        )

        self.logger.debug(f"Posted status id={status_result['id']}")


class StreamListener(mastodon.streaming.StreamListener):
    def __init__(self, bot, client):
        self.bot = bot
        self.client = client
        self.logger = logging.getLogger("bot")

    def on_notification(self, notification):
        try:
            self.bot.handle_notification(notification)
            self.logger.debug(f"Dismissing notification {notification['id']}")
            self.client.notifications_dismiss(notification["id"])
        except:
            e = sys.exc_info()[0]
            self.logger.error(f"Failed to handle notification: {e}")



class ProgramSourceHTMLParser(HTMLParser):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.in_hashtag = 0
        self.captured_hashtag = ""
        self.capture_text = False
        self.found_logo_hashtag = False
        self.text = ""

    def get_text(self):
        return self.text.strip()

    def handle_starttag(self, tag, attrs):
        attrs_dict = defaultdict(lambda: None, attrs)
        if attrs_dict["class"] == "mention hashtag":
            self.in_hashtag = 1
            self.captured_hashtag = ""
        elif self.in_hashtag > 0:
            self.in_hashtag += 1
        elif tag == "br":
            if self.capture_text:
                self.text += "\n"

    def handle_data(self, data):
        if self.in_hashtag:
            self.captured_hashtag += data
        elif self.capture_text:
            self.text += data

    def handle_endtag(self, tag):
        if self.in_hashtag > 0:
            self.in_hashtag -= 1
            if self.in_hashtag == 0:
                if self.captured_hashtag == "#logo":
                    self.capture_text = True
                    self.found_logo_hashtag = True
        elif tag == "p":
            if self.capture_text:
                self.text += "\n\n"
