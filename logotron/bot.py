import os
import os.path
import mastodon.streaming
from bs4 import BeautifulSoup
import pprint

# from multiprocessing import Pool

from .client import Client
from .logo_runner import LogoRunner


class Bot:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.client = Client(
            user_agent=config.user_agent,
            api_base_url=config.api_base_url,
            client_id=config.client_key,
            client_secret=config.client_secret,
            access_token=config.access_token,
            debug_requests=config.debug_requests,
        )
        self.listener = StreamListener(
            bot=self, client=self.client, logger=logger)

    def run_streaming(self):
        # self.client.status_post(
        #    status=f"hello there, I have awoken at {datetime.datetime.now().isoformat()}")
        self.logger.info("Listening to notifications stream...")
        self.client.stream_user(listener=self.listener)

    def poll_notifications(self):
        notifications = self.client.notifications(
            mentions_only=True
        )
        for notification in notifications:
            self.handle_notification(notification)

    def handle_notification(self, notification):
        # self.logger.info(
        #    f"NOTIFICATION RAW {pprint.PrettyPrinter(depth=4).pformat(notification)}")

        type = notification["type"]
        if type != "mention":
            return

        account = notification["account"]
        bot = account["bot"]
        acct = account["acct"]

        status = notification["status"]
        status_id = status["id"]
        visibility = status["visibility"]
        if visibility != "public":
            return

        # Parse the status HTML for cleanup and source extraction
        content_html = status["content"]
        soup = BeautifulSoup(content_html, "html5lib")

        # Remove the h-cards from the mention
        h_cards = soup.find_all(attrs={"class": "h-card"})
        for h_card in h_cards:
            h_card.extract()
            
        # Convert <br>s to line breaks
        for br in soup.find_all("br"):
            br.replace_with("\n")

        program_source = soup.text

        self.logger.debug(
            f"Notification id={id} acct={acct} content={program_source} raw={content_html}")

        runner = LogoRunner(
            id=status_id,
            source=program_source,
            config=self.config,
            logger=self.logger
        )
        runner.run()

        self.logger.debug(f"Posting media from {runner.output_video_filename} with {program_source}")
        media_result = self.client.media_post(
            runner.output_video_filename,
            "video/mp4",
            synchronous=True,
            description=program_source,
            focus=(0, 0),
        )

        status_result = self.client.status_post(
            f"@{acct} I ran your program, and here's what happened!",
            in_reply_to_id=status_id,
            media_ids=[media_result["id"]],
            idempotency_key=None,
        )

        self.logger.debug(f"Posted status id={status_result['id']}")

        self.logger.debug(f"Dismissing notification {notification['id']}")
        self.client.notifications_dismiss(notification["id"])


class StreamListener(mastodon.streaming.StreamListener):
    def __init__(self, bot, client, logger):
        self.bot = bot
        self.client = client
        self.logger = logger

    def on_notification(self, notification):
        self.bot.handle_notification(notification)
