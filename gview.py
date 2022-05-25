# standard modules
from dataclasses import dataclass
import base64
import getpass
import os
from typing import Dict
import json
from logging import Logger

# custom modules
from request import get
from base_logger import get_logger

logger: Logger = get_logger(__name__)

@dataclass
class LoginBundle:
    username: str
    password: str

    @property
    def base64(self) -> str:
        return base64.b64encode(f"{self.username}:{self.password}".encode()).decode()

    @staticmethod
    def non_interactive_login() -> "LoginBundle":
        pass_env_var = 'GITHUB_PAT'
        username = getpass.getuser()
        if f"{pass_env_var}" in os.environ:
            logger.debug(f"Found {pass_env_var} environment variable. Getting password from it.")
            password = os.getenv(f'{pass_env_var}')
        else:
            logger.info(f"To hide interactive login put the GitHub PAT to env variable '{pass_env_var}'")
            password = getpass.getpass(f"Password for {username}: ")
        return LoginBundle(username, password)


@dataclass
class GitHubInstanceInfo:
    base_url: str
    credentials: LoginBundle

    @property
    def headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "Authorization": f"Basic {self.credentials.base64}"}


class GitHubInstance:
    def __init__(self, instance: GitHubInstanceInfo):
        self.instance = instance

    def get_user(self, user: str):
        url = self.instance.base_url + f"/users/{user}"

        status, data = get(url, headers=self.instance.headers)

        if status != 200:
            logger.info(f"Failed to perform request of {url}, status is {status}")
            return

        data = json.loads(data)
        print(data)

    def get_user_activities(self, user: str):
        logger.info("Will be implemented next")


def main():
    # Put arg parse here. something like "user"

    login_bundle = LoginBundle.non_interactive_login()
    gh_instance_info = GitHubInstanceInfo("https://api.github.com", login_bundle)

    gh_instance = GitHubInstance(gh_instance_info)

    gh_instance.get_user("vmeshche")
    gh_instance.get_user_activities("vmeshche")


if __name__ == '__main__':
    main()
