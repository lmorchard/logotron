import mastodon.streaming
from bs4 import BeautifulSoup
import pprint


class StreamListener(mastodon.streaming.StreamListener):
    def __init__(self, bot, client, logger):
        self.bot = bot
        self.client = client
        self.logger = logger

    def on_notification(self, notification):
        self.logger.info(
            f"NOTIFICATION RAW {pprint.PrettyPrinter(depth=4).pformat(notification)}")

        type = notification["type"]
        if type != "mention":
            return

        account = notification["account"]
        bot = account["bot"]            
        acct = account["acct"]
        
        status = notification["status"]
        visibility = status["visibility"]
        if visibility != "public":
            return

        content_html = status["content"]
        soup = BeautifulSoup(content_html, "html5lib")
        content = soup.text

        self.logger.info(f"NOTIFICATION {acct} {content}")
