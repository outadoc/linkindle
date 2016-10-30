#!/usr/bin/env python
# -*- coding: utf-8 -*-

import linky
import os

username = os.environ['LINKY_USERNAME']
password = os.environ['LINKY_PASSWORD']

try:
    print("logging in as " + username + "...")
    token = linky.login(username, password)
    print("logged in successfully")
    res = linky.get_data_per_day(token, '27/10/2016', '30/10/2016')
    print(res)
except LinkyLoginException as e:
    print(e)
