#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import base64
import os
from enum import Enum

LOGIN_BASE_URI = 'https://espace-client-connexion.erdf.fr'
API_BASE_URI = 'https://espace-client-particuliers.erdf.fr/group/espace-particuliers'

API_ENDPOINT_LOGIN = '/auth/UI/Login'
API_ENDPOINT_DATA = '/jeconsultetelechargemesdonneesdeconsommation'

username = os.environ['LINKY_USERNAME']
password = os.environ['LINKY_PASSWORD']

class LinkyLoginException(Exception):
    pass

def login(username, password):
    payload = {'IDToken1': username,
                'IDToken2': password,
                'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
                'encoded': 'true',
                'gx_charset': 'UTF-8'}

    r = requests.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)
    session_cookie = r.cookies.get('iPlanetDirectoryPro')

    if session_cookie == None:
        raise LinkyLoginException("Login unsuccessful. Check your credentials.")

    return session_cookie

def get_data_hour(token, start_date, end_date):
    return get_data(token, 'urlCdcHeure', start_date, end_date)

def get_data_day(token, start_date, end_date):
    return get_data(token, 'urlCdcJour', start_date, end_date)

def get_data_month(token, start_date, end_date):
    return get_data(token, 'urlCdcMois', start_date, end_date)

def get_data_year(token):
    return get_data(token, 'urlCdcAn')

def get_data(token, resource_id, start_date = None, end_date = None):
    cookies = {'iPlanetDirectoryPro': token}
    payload = {
        '_lincspartdisplaycdc_WAR_lincspartcdcportlet_INSTANCE_partlincspartcdcportlet_dateDebut': start_date,
        '_lincspartdisplaycdc_WAR_lincspartcdcportlet_INSTANCE_partlincspartcdcportlet_dateFin': end_date
    }
    params = {
        'p_p_id': 'lincspartdisplaycdc_WAR_lincspartcdcportlet_INSTANCE_partlincspartcdcportlet',
        'p_p_lifecycle': 2,
        'p_p_state': 'normal',
        'p_p_mode': 'view',
        'p_p_resource_id': resource_id,
        'p_p_cacheability': 'cacheLevelPage',
        'p_p_col_id': 'column-1',
        'p_p_col_pos': 1,
        'p_p_col_count': 3
    }

    r = requests.post(API_BASE_URI + API_ENDPOINT_DATA, allow_redirects=False, cookies=cookies, data=payload, params=params)
    return r.json()

try:
    print("logging in as " + username + "...")
    token = login(username, password)
    print("logged in successfully")
    res = get_data_day(token, '27/10/2016', '30/10/2016')
    print(res)
except LinkyLoginException as e:
    print(e)
