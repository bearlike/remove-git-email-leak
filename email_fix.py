#!/usr/bin/env python3
# Fix GitHub User's Email Address leak through commits
# Repo: https://github.com/bearlike/find-fix-git-email-leak
import requests
from os import system, environ, chdir
from colorama import Back, Style, Fore
from shutil import rmtree
from dotenv import load_dotenv

load_dotenv()

# GitHub Secrets
username = environ["GH_USERNAME"]
token = environ["GH_TOKEN"]
orgs = environ["ORGS"].split(",")

# Fixes
old_email = environ["OLD_EMAIL"]
correct_name = environ["CORRECT_NAME"]
correct_email = environ["CORRECT_EMAIL"]

# To supress git fliter warning
environ["FILTER_BRANCH_SQUELCH_WARNING"] = "1"

git_fix = """
git filter-branch --env-filter '
if [ "$GIT_COMMITTER_EMAIL" = "{old_email}" ]
then
    export GIT_COMMITTER_NAME="{correct_name}"
    export GIT_COMMITTER_EMAIL="{correct_email}"
fi
if [ "$GIT_AUTHOR_EMAIL" = "{old_email}" ]
then
    export GIT_AUTHOR_NAME="{correct_name}"
    export GIT_AUTHOR_EMAIL="{correct_email}"
fi
' --tag-name-filter cat -- --branches --tags
git push --force --tags origin HEAD:{default_branch}"""


def main():
    repos = []
    print(Fore.YELLOW, "!! User must have write permissions for the \
        repositories !!", Style.RESET_ALL)
    print(Fore.YELLOW, "!! Works only on parent branch !!", Style.RESET_ALL)
    print(Fore.YELLOW, "!! Commit hashes can be changed !!", Style.RESET_ALL)
    for org in orgs:
        org = org.strip()
        query_url = f"https://api.github.com/users/{org}/repos".format(org)
        headers = {'Authorization': f'token {token}'}
        r = requests.get(query_url, headers=headers)
        objects = r.json()
        for obj in objects:
            repos.append([
                obj["html_url"].replace("https://github.com/", ""),
                obj["default_branch"]
            ])
    count = 1
    tot = len(repos)
    for repo in repos:
        progress_str = "{count} out of {tot} ({repo}) ....".format(
            count=count, tot=tot, repo=repo[0])
        print(Fore.RED+Back.BLACK, progress_str, Style.RESET_ALL)
        cln = f"git clone https://{username}:{token}@github.com/{repo[0]}.git"
        system(cln)
        email_fix = git_fix.format(
            old_email=old_email,
            correct_name=correct_name,
            correct_email=correct_email,
            default_branch=repo[1]
        )
        chdir(repo[0].split("/")[1])
        system(email_fix)
        count += 1
        chdir("../")
        rmtree(repo[0].split("/")[1])
        print(Style.RESET_ALL)


if __name__ == '__main__':
    main()
