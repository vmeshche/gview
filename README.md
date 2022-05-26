# gview
Project to view personal activities on GitHub in command line.

# Prework
This project operate with GitHub API. [You need to configure authentication on GitHub](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#authentication) to be able to work with it.

# Limitations
Tool is based on work with events on GitHub API. Unfortunately events history is limited by GitHub, [limit is last 90 days](https://docs.github.com/en/rest/activity/events).

# Usage
```
python gview.py -u <username_on_github>
```
