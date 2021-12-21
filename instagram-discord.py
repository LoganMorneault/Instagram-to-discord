#!/usr/bin/python

'''
Code taken largely from fernandod1 on GitHub. I'm altering things slightly to hopefully work for multiple accounts.
'''

# Copyright (c) 2020 Fernando
# Url: https://github.com/fernandod1/
# License: MIT

# DESCRIPTION:
# This script executes 2 actions:
# 1.) Monitors for new image posted in a instagram account.
# 2.) If found new image, a bot posts new instagram image in a discord channel.
# 3.) Repeat after set interval.

# REQUIREMENTS:
# - Python v3
# - Python module json, requests
import json
import requests
import os
import time

# USAGE:
# Change elements in INSTAGRAM_ACCOUNTS to the names of the accounts you want to copy. 
# Because I'm running my webhook directly from this repository, mine are already specified. Please do not judge.

INSTAGRAM_ACCOUNTS = ["pipesbuffet", "kookyfonts", "boomer.jim", "imshively", "worst.buy", "chrissimpsonsartist"]
WEBHOOK_URL = "https://discord.com/api/webhooks/922646420270510130/u2yGGmeqnWnegaOuaSR6SH1sSJaaklv6SX1vv-U2Lzhs931P_7rI2btmtOHukay8rJHf"

# ----------------------- Do not modify under this line ----------------------- #
# Sorry!


def get_user_fullname(html):
    return html.json()["graphql"]["user"]["full_name"]


def get_total_photos(html):
    return int(html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["count"])


def get_last_publication_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]


def get_last_photo_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["display_url"]


def get_last_thumb_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["thumbnail_src"]


def get_description_photo(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]


def webhook(webhook_url, html, user):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data = {}
    data["embeds"] = []
    embed = {}
    embed["color"] = 15467852
    embed["title"] = "New post from @{0}".format(user)
    embed["url"] = "https://www.instagram.com/p/" + \
        get_last_publication_url(html)+"/"
    embed["description"] = get_description_photo(html)
    # embed["image"] = {"url":get_last_thumb_url(html)} # unmark to post bigger image
    embed["thumbnail"] = {"url": get_last_thumb_url(html)}
    data["embeds"].append(embed)
    result = requests.post(webhook_url, data=json.dumps(
        data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Image successfully posted in Discord, code {}.\n".format(
            result.status_code))


def get_instagram_html(user):
    headers = {
        "Host": "www.instagram.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    html = requests.get("https://www.instagram.com/" +
                        user + "/feed/?__a=1", headers=headers)
    return html


def main():
    for user in INSTAGRAM_ACCOUNTS:
        try:
            html = get_instagram_html(user)
            if(os.environ.get("LAST_IMAGE_ID") == get_last_publication_url(html)):
                print("No new image from {0}.".format(user))
            else:
                os.environ["LAST_IMAGE_ID"] = get_last_publication_url(html)
                print("New image from {0} to post in discord.".format(user))
                webhook(WEBHOOK_URL,
                        get_instagram_html(user), user)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    if WEBHOOK_URL != None:
        while True:
            main()
            time.sleep(600) # 600 = 10 minutes
    else:
        print('Please configure environment variables properly!')
