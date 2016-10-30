#!/usr/bin/env python
# -*- coding: utf-8 -*-

import linky
import os
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plot

username = os.environ['LINKY_USERNAME']
password = os.environ['LINKY_PASSWORD']

try:
    print("logging in as " + username + "...")
    token = linky.login(username, password)
    print("logged in successfully")
    res = linky.get_data_month(token, '01/05/2016', '30/10/2016')

    y_values = []
    x_values = []

    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()
    start_date = start_date_queried - relativedelta(months=res['graphe']['decalage'])

    print(start_date)

    for datapoint in res['graphe']['data']:
        y_values.insert(datapoint['ordre'], datapoint['valeur'])
        x_values.insert(datapoint['ordre'], (start_date + relativedelta(months=datapoint['ordre']-1)).strftime("%b %Y"))

    print(y_values)
    print(x_values)

    width = .35
    graph = plot.figure()
    ind = np.arange(len(y_values))

    plot.bar(ind, y_values, width=width)
    plot.xticks(ind + width / 2, x_values)

    graph.autofmt_xdate()
    plot.savefig("figure.pdf")
except linky.LinkyLoginException as e:
    print(e)
