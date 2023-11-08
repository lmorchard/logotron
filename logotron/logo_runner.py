import os.path
from pathlib import Path

import docker


class LogoRunner:
    def __init__(
        self,
        id,
        source,
        logger,
        config,
        input_dir="input",
        output_dir="output",
        output_video_filename="output.mp4",
        program_name="program.logo"
    ):
        self.id = id
        self.logger = logger
        self.config = config
        self.base_path = os.path.abspath(os.path.join(self.config.data_base_dir, str(id)))
        self.input_path = os.path.join(self.base_path, input_dir)
        self.output_path = os.path.join(self.base_path, output_dir)
        self.output_video_filename = os.path.join(self.output_path, output_video_filename)
        self.source = source
        self.program_name = program_name
        self.docker = docker.from_env()
        self.container = None

    def run(self):
        self.logger.debug(f"Preparing container files at {self.base_path}")

        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        Path(self.input_path).mkdir(parents=True, exist_ok=True)
        Path(self.output_path).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(self.input_path, self.program_name), 'w') as f:
            f.write(self.source)

        self.logger.debug(
            f"Launching container from {self.config.logo_runner_image}")

        try:
            self.container = self.docker.containers.run(
                name=f"logo-runner-{self.id}",
                image=self.config.logo_runner_image,
                mem_limit=self.config.logo_runner_mem_limit,
                network_mode="none",
                detach=True,
                auto_remove=True,
                volumes={
                    self.input_path: {'bind': '/input', 'mode': 'ro'},
                    self.output_path: {'bind': '/output', 'mode': 'rw'},
                }
                # env
            )
            self.logger.debug(f"Launched container {self.container.id}")

            container_logs = self.container.logs(
                timestamps=True,
                stream=True,
                follow=True
            )
            for message in container_logs:
                self.logger.info(f"log {message}")
        except docker.errors.APIError as e:
            e_msg = str(e)
            self.logger.error(f"Failed to launch container {e_msg}")
            
