# standard modules
from dataclasses import dataclass
import base64
import getpass
import os
from typing import Dict, List
from logging import Logger
import argparse
from datetime import datetime
from datetime import timedelta
from math import ceil
import calendar

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


@dataclass
class Day:
    date: datetime
    contributions: int = 0

    def __str__(self):
        return str(self.date) + ' ' + str(self.contributions)

    def __eq__(self, other):
        return True if self.date == other.date else False

    def __add__(self, other):
        return Day(self.date, self.contributions + other.contributions)


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
                                    date=datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%S%z').date()
                                    )
                    self.commits.append(commit)
            contributions = self.build_contribution_map()
            for c in contributions:
                print(c)
            drawer = Drawer(contributions)
            drawer.draw()

    def build_contribution_map(self) -> List[Day]:
        day_map = []
        for commit in self.commits:
            new_day = Day(date=commit.date, contributions=1)
            if new_day in day_map:
                for i, day in enumerate(day_map):
                    if day == new_day:
                        day_map[i] = day + new_day
            else:
                day_map.append(new_day)
        return day_map


class Drawer:
    def __init__(self, contrib_data: Dict):
        self.contributions = contrib_data
        self.week_days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    def check_date_contribution(self, date) -> str:
        contrib_this_day = "-"
        for day in self.contributions:
            if day.date == date:
                contrib_this_day = str(day.contributions)
        return contrib_this_day

    def draw(self):
        w = 3
        weeks = 13
        days_interval = 7 * weeks  # 91 day; about 3 months
        now = datetime.now().date()
        start = now - timedelta(days=days_interval)
        start = start + timedelta(days=(7 - start.weekday()))  # calculate monday on start week
        print(f"Interval from {start} to {now}")

        # Prepare first line
        m_interval = 17
        last_months = []
        for i in range(start.month, now.month + 1):
            last_months.append(f"{str(calendar.month_name[i]):{m_interval}}")
        months_line = "".join(last_months)

        days_counter = start
        lines = []
        for week in range(0, weeks):
            line = []
            for day in range(0, 7):
                text = f'{str(self.check_date_contribution(days_counter)):{w}}'
                line.append(text)
                days_counter += timedelta(days=1)
            lines.append(line)

        print(months_line)
        for day in range(0, 7):  # iterate week days (Rows)
            line = [f'{str(self.week_days[day]):{w}}']
            for week in range(0, weeks):  # iterate weeks (Columns)
                text = lines[week][day]
                line.append(text)
                days_counter += timedelta(days=1)
            print(" ".join(line))


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
