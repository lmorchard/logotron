import datetime
import pprint
import mastodon.streaming
from bs4 import BeautifulSoup
import pprint

from .client import Client


class Bot:

    def __init__(self, config, logger):
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
        #self.logger.info(
        #    f"NOTIFICATION RAW {pprint.PrettyPrinter(depth=4).pformat(notification)}")

        type = notification["type"]
        if type != "mention":
            return

        id = notification["id"]
        account = notification["account"]
        bot = account["bot"]
        acct = account["acct"]

        status = notification["status"]
        visibility = status["visibility"]
        if visibility != "public":
            return

        content_html = status["content"]
        soup = BeautifulSoup(content_html, "html5lib")

        h_cards = soup.find_all(attrs={"class": "h-card"})
        for h_card in h_cards:
            h_card.extract()
        
        content = soup.text

        self.logger.info(f"NOTIFICATION id={id} acct={acct} content={content}")


class StreamListener(mastodon.streaming.StreamListener):
    def __init__(self, bot, client, logger):
        self.bot = bot
        self.client = client
        self.logger = logger

    def on_notification(self, notification):
        self.bot.handle_notification(notification)
