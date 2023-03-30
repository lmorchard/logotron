import docker


class LogoRunner:
    def __init__(self, base_path, logger, config):
        self.base_path = base_path
        self.logger = logger
        self.config = config
        self.docker = docker.from_env()

    def run(self):
        self.logger.info(
            f"Launching container from {self.config.logo_runner_image}")

        container = self.docker.containers.run(
            image=self.config.logo_runner_image,
            mem_limit=self.config.logo_runner_mem_limit,
            network_mode="none",
            detach=True,
            auto_remove=True,
            volumes={
                f'{self.base_path}/input': {'bind': '/input', 'mode': 'ro'},
                f'{self.base_path}/output': {'bind': '/output', 'mode': 'rw'},
            }
        )
        self.logger.info(f"Launched container {container.id}")

        container_logs = container.logs(
            timestamps=True,
            stream=True,
            follow=True
        )
        for message in container_logs:
            self.logger.info(f"log {message}")
            pass
