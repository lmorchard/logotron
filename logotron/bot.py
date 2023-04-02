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

    def run_streaming(self):
        self.logger.info("Listening to notifications stream...")
        self.client.stream_user(
            listener=BotStreamListener(bot=self, client=self.client))

    def poll_notifications(self):
        notifications = self.client.notifications(mentions_only=True)
        for notification in notifications:
            self.handle_notification(notification)

    def handle_notification(self, notification):
        try:
            # Only handle mentions from notifications
            type = notification["type"]
            if type != "mention":
                return

            # Don't respond to accounts marked as bots
            account = notification["account"]
            bot = account["bot"]
            if bot:
                return

            # Ignore mentions without a valid program title from content warning
            status = notification["status"]
            program_title = self.sanitize_program_title(status["spoiler_text"])
            if program_title == "":
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

            # Get ready to reply...
            acct = account["acct"]
            status_id = status["id"]

            # Try to get the program source, give a warning if we come up empty
            program_source = parser.get_text()
            if program_source == "":
                status_result = self.client.status_post(
                    f"@{acct} 🐢 Sorry, I couldn't find a program in your toot! 😔",
                    in_reply_to_id=status_id,
                )
                self.logger.debug(f"Posted status id={status_result['id']}")
                return

            self.logger.debug(
                f"Handling notification id={id} acct={acct} title={program_title} program_source={program_source}")

            # Finally, take a crack at running the program source
            runner = LogoRunner(
                id=status_id,
                source=program_source,
                config=self.config,
                logger=self.logger
            )
            runner.run()

            # TODO: check whether the program run was actually successful and produced a video

            # Upload the video that should have been produced from the run
            self.logger.debug(
                f"Posting media from {runner.output_video_filename} with {program_source}")
            media_result = self.client.media_post(
                runner.output_video_filename,
                "video/mp4",
                synchronous=True,
                description=program_source,
                focus=(0, 0),
            )

            # Post a reply with the video result, once it's been uploaded
            status_result = self.client.status_post(
                f"@{acct} 🐢 I ran your #logo program, ✨ {program_title} ✨! Here's what happened...",
                in_reply_to_id=status_id,
                media_ids=[media_result["id"]],
                idempotency_key=None,
            )
            self.logger.debug(f"Posted status id={status_result['id']}")

            # Dismiss the notification so we don't handle it over again, next poll
            self.logger.debug(f"Dismissing notification {notification['id']}")
            self.client.notifications_dismiss(notification["id"])

        except:
            e = sys.exc_info()[0]
            self.logger.error(f"Failed to handle notification: {e}")
            # TODO: send an apology to the user?

    def sanitize_program_title(self, raw_title):
        """
        Strip undesirable characters from the content warning used as
        program title, since it's repeated in the bot's reply.
        """
        # TODO: think this through a bit more
        return re.sub(r'[^\w\s,.!\u263a-\U0001f645]+', '', raw_title)


class BotStreamListener(mastodon.streaming.StreamListener):
    def __init__(self, bot, client):
        self.bot = bot
        self.client = client
        self.logger = logging.getLogger("bot")

    def on_notification(self, notification):
        self.bot.handle_notification(notification)


class ProgramSourceHTMLParser(HTMLParser):
    """
    Quick & dirty parser to find and extract Logo program source expected
    after a #logo hashtag in a toot formatted as HTML
    """

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
            if self.in_hashtag == 0 and self.captured_hashtag == "#logo":
                self.capture_text = True
                self.found_logo_hashtag = True
        elif tag == "p" and self.capture_text:
            self.text += "\n\n"
