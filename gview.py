# standard modules
from dataclasses import dataclass
import base64
import getpass
import os
from typing import Dict, List
from logging import Logger
import argparse
from datetime import datetime

# custom modules
from request import get
from base_logger import get_logger

logger: Logger = get_logger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description="Tool to get user activities on GitHub")
    parser.add_argument("-u", required=True, dest="user", type=str,
                        help="User name on GitHub to get info")
    return parser.parse_args()


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
        return {"Accept": "application/vnd.github.v3+json",
                "Authorization": f"Basic {self.credentials.base64}"}


class GitHubInstance:
    def __init__(self, instance: GitHubInstanceInfo):
        self.instance = instance

    def get_user(self, user: str):
        url = self.instance.base_url + f"/users/{user}"

        data = get(url, headers=self.instance.headers)

        return data

    def get_user_events(self, user: str):
        url = self.instance.base_url + f"/users/{user}/events/public"

        data = get(url, headers=self.instance.headers)

        return data


@dataclass
class Commit:
    author: str
    date: datetime

    def __str__(self):
        return f"{self.author}; {str(self.date)}"


class GitHubEvents:
    instance: GitHubInstance
    commits: List[Commit]

    def __init__(self, gh_instance: GitHubInstance):
        self.instance = gh_instance
        self.commits = []

    def filter_events(self, user: str, event_type: str):
        data = self.instance.get_user_events(user)

        if data:
            for item in data:
                if item["type"] == event_type:
                    commit = Commit(author=item["actor"]["login"],
                                    date=datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%S%z')
                                   )
                    self.commits.append(commit)
            for c in self.commits:
                print(c)
            contribution_dict = self.build_contribution_dict()
            for item in contribution_dict:
                print(item, contribution_dict[item])

    def build_contribution_dict(self) -> Dict:
        cdict = {}
        for commit in self.commits:
            day = str(commit.date.date())
            if day in cdict:
                cdict[day] += 1
            else:
                cdict[day] = 1
        return cdict


def main():
    args = get_args()

    # Get GitHub instance to work with
    login_bundle = LoginBundle.non_interactive_login()
    gh_instance_info = GitHubInstanceInfo("https://api.github.com", login_bundle)
    gh_instance = GitHubInstance(gh_instance_info)

    # Get Events tools and get filtered event list
    gh_events = GitHubEvents(gh_instance)
    gh_events.filter_events(args.user, "PushEvent")


if __name__ == '__main__':
    main()
