#!/usr/bin/env python3
# Find (Almost) Any GitHub User's Email Address using GitHub Events API
# Repo: https://github.com/bearlike/find-fix-git-email-leak

import requests
import tabulate
from os import environ
from dotenv import load_dotenv
from colorama import Style, Fore

load_dotenv()

# GitHub Secrets
username = environ["GH_USERNAME"]
token = environ["GH_TOKEN"]
orgs = environ["ORGS"].split(",")


def print_table(object):
    header = ["Email Address", "Committer Name", "Repository (user/repo)"]
    rows = [x.values() for x in object]
    print(tabulate.tabulate(rows, header), "\n")


def main():
    all_emails = []
    leaked_emails = []
    gh_emails = []
    print(Fore.YELLOW, "\nSearching in", orgs, "\n", Style.RESET_ALL)
    for org in orgs:
        org = org.strip()
        query_url = f"https://api.github.com/users/{org}/events?per_page=100".format(
            org)
        headers = {'Authorization': f'token {token}'}
        r = requests.get(query_url, headers=headers)
        objects = r.json()
        for obj in objects:
            var = obj.get("payload").get("commits")
            if var is not None:
                for v in var:
                    t_d = {
                        "name":  v.get("author").get("name"),
                        "email": v.get("author").get("email"),
                        "repo":  v.get("url").replace(
                            "https://api.github.com/repos/", ""
                            ).split("/commits")[0]
                    }
                    all_emails.append(t_d)

    all_emails = list(map(dict, set(tuple(sorted(d.items()))
                      for d in all_emails)))
    all_emails = sorted(all_emails, key=lambda k: k['name'])

    for em in all_emails:
        if not em["email"].endswith("@users.noreply.github.com"):
            leaked_emails.append(em)
        else:
            gh_emails.append(em)

    print(Fore.YELLOW, "\n!! Leaked Emails !!\n", Style.RESET_ALL)
    print_table(leaked_emails)
    print(Fore.YELLOW, "\n!! GitHub Emails !!\n", Style.RESET_ALL)
    print_table(gh_emails)


if __name__ == '__main__':
    main()
