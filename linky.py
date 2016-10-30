#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import base64
import os

API_BASE_URI = 'https://espace-client-connexion.erdf.fr'

username = os.environ['LINKY_USERNAME']
password = os.environ['LINKY_PASSWORD']

def login(username, password):
    payload = {'IDToken1': username,
                'IDToken2': password,
                'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
                'encoded': 'true',
                'gx_charset': 'UTF-8'}

    try:
        r = requests.post(API_BASE_URI + '/auth/UI/Login', data=payload, allow_redirects=False)
        session_cookie = r.cookies.get('iPlanetDirectoryPro')
        return session_cookie
    except RequestException:
        return None

token = login(username, password)
print(token)
