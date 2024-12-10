import json
from urllib.parse import urlparse

import requests
from lxml import html

import config


def login(username: str, password):
    """https://www.backroomswiki.ru/-/login"""
    session = requests.Session()

    headers = {
        "User-Agent": config.values.get('requests.user_agent'),
        "Referer": config.LOGIN_URL
    }
    response = session.get(config.LOGIN_URL)

    tree = html.fromstring(response.content)
    csrf_token = tree.xpath('//input[@name="csrfmiddlewaretoken"]/@value')[0]

    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "username": username,
        "password": password
    }

    response = session.post(config.LOGIN_URL, data=payload, headers=headers)
    with open('.session.json' "w") as file_session:
        file_session.write(json.dumps(session.cookies.get_dict()))


def get_article(page_name: str) -> dict:
    """Like level-0 name or another, without url"""
    return requests.get(f'https://{url_path.hostname}/api/articles/{page_name}').json()



