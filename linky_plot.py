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

output_dir = 'out'

def generate_y_axis(res):
    y_values = []

    for datapoint in res['graphe']['data']:
        ordre = datapoint['ordre']
        value = datapoint['valeur']
        y_values.insert(ordre, value)

    return y_values

def generate_x_axis(res, time_delta_unit, time_format):
    x_values = []

    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()

    kwargs = {}
    kwargs[time_delta_unit] = res['graphe']['decalage']
    start_date = start_date_queried - relativedelta(**kwargs)

    for datapoint in res['graphe']['data']:
        ordre = datapoint['ordre']
        kwargs = {}
        kwargs[time_delta_unit] = ordre-1
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

def generate_graph_from_data(res, time_delta_unit, time_format):
    y_values = generate_y_axis(res)
    x_values = generate_x_axis(res, time_delta_unit, time_format)

    width = .35
    graph = plot.figure()
    ind = np.arange(len(y_values))

    plot.bar(ind, y_values, width=width)
    plot.xticks(ind + width / 2, x_values)

    graph.autofmt_xdate()
    return plot

def generate_graph_months():
    plot = generate_graph_from_data(res, 'months', "%b %Y")
    plot.savefig(output_dir + "/linky_months.png")

try:
    print("logging in as " + username + "...")
    token = linky.login(username, password)
    print("logged in successfully")

    res = linky.get_data_month(token, '01/05/2016', '30/10/2016')
    generate_graph_months()

except linky.LinkyLoginException as e:
    print(e)
