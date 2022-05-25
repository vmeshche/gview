from dataclasses import dataclass
import base64
import getpass
import os
from typing import Dict, Tuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json


def request(method: str, url: str, headers: dict = None, body=None) -> Tuple[int, bytes]:
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req) as open_request:
            status = open_request.status
            response = open_request.read()
    except HTTPError as e:
        return e.code, str(e).encode()

    return status, response


def get(*args, **kwargs):
    return request("GET", *args, **kwargs)


@dataclass
class LoginBundle:
    username: str
    password: str

    @property
    def base64(self) -> str:
        return base64.b64encode(f"{self.username}:{self.password}".encode()).decode()

    @staticmethod
    def non_interactive_login() -> "LoginBundle":
        username = getpass.getuser()
        if "GITHUB_PAT" in os.environ:
            password = os.getenv('GITHUB_PAT')
        else:
            print("To hide interactive login put the GitHub PAT to env variable 'GITHUB_PAT'")
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

        data = json.loads(data)
        print(data)


def main():
    print(f'We are starting')
    login_bundle = LoginBundle.non_interactive_login()
    gh_instance_info = GitHubInstanceInfo("https://api.github.com", login_bundle)

    print(gh_instance_info.headers)

    gh_instance = GitHubInstance(gh_instance_info)

    gh_instance.get_user("vmeshche")


if __name__ == '__main__':
    main()
