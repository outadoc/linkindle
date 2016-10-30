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

    for ordre, datapoint in enumerate(res['graphe']['data']):
        value = datapoint['valeur']

        if value < 0:
            value = 0

        y_values.insert(ordre, value)

    return y_values

def generate_x_axis(res, time_delta_unit, time_format):
    x_values = []

    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()

    kwargs = {}
    kwargs[time_delta_unit] = res['graphe']['decalage']
    start_date = start_date_queried - relativedelta(**kwargs)

    for ordre, datapoint in enumerate(res['graphe']['data']):
        kwargs = {}
        kwargs[time_delta_unit] = ordre
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

def generate_graph_from_data(res, time_delta_unit, time_format, ylegend):
    y_values = generate_y_axis(res)
    x_values = generate_x_axis(res, time_delta_unit, time_format)

    print(y_values)
    print(x_values)

    width = .55

    fig, ax = plot.subplots()
    ind = np.arange(len(x_values))

    plot.bar(ind, y_values, width=width, color='k')
    plot.xticks(ind + width / 2, x_values)
    plot.ylabel(ylegend)
    plot.grid(True)
    plot.xlim([-width, len(x_values)])

    # If there are too many elements on the X axis, make it more compact
    if len(x_values) > 20:
        # Rotate labels
        fig.autofmt_xdate()
        for label in ax.xaxis.get_ticklabels()[::2]:
            # Hide every other label
            label.set_visible(False)

    return plot

def generate_graph_days(res):
    plot = generate_graph_from_data(res, 'days', "%d %b", "kWh")
    plot.savefig(output_dir + "/linky_days.png")

def generate_graph_months(res):
    plot = generate_graph_from_data(res, 'months', "%b", "kWh")
    plot.savefig(output_dir + "/linky_months.png")

def generate_graph_years(res):
    plot = generate_graph_from_data(res, 'years', "%Y", "kWh")
    plot.savefig(output_dir + "/linky_years.png")

try:
    print("logging in as " + username + "...")
    token = linky.login(username, password)
    print("logged in successfully!")

    print("retreiving data...")
    res_month = linky.get_data_per_month(token, '01/05/2016', '30/10/2016')
    res_year = linky.get_data_per_year(token)
    res_day = linky.get_data_per_day(token, '29/09/2016', '29/10/2016')
    print("got data!")

    print("generating graphs...")
    generate_graph_months(res_month)
    generate_graph_years(res_year)
    generate_graph_days(res_day)
    print("successfully generated graphs!")

except linky.LinkyLoginException as e:
    print(e)
