import datetime

from .client import Client
from .streaming import StreamListener

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
        self.listener = StreamListener(bot=self, client=self.client, logger=logger)

    def run_streaming(self):
        #self.client.status_post(
        #    status=f"hello there, I have awoken at {datetime.datetime.now().isoformat()}")
        self.logger.info("Listening to notifications stream...")
        self.client.stream_user(listener=self.listener)
