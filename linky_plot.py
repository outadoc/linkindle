#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Linkindle - Linky energy consumption curves on a Kindle display.
# Copyright (C) 2016 Baptiste Candellier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import linky
import os
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plot

username = os.environ['LINKY_USERNAME']
password = os.environ['LINKY_PASSWORD']

OUTPUT_DIR = 'out'

GRAPH_WIDTH_IN = 4.8
GRAPH_HEIGHT_IN = 3.6
GRAPH_DPI = 167

def generate_y_axis(res):
    y_values = []

    # Extract data points from the source dictionary into a list
    for ordre, datapoint in enumerate(res['graphe']['data']):
        value = datapoint['valeur']

        # Remove any invalid values
        # (they're error codes on the API side, but useless here)
        if value < 0:
            value = 0

        y_values.insert(ordre, value)

    return y_values

def generate_x_axis(res, time_delta_unit, time_format, inc):
    x_values = []

    # Extract start date and parse it
    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()

    # Calculate final start date using the "offset" attribute returned by the API
    kwargs = {}
    kwargs[time_delta_unit] = res['graphe']['decalage'] * inc
    start_date = start_date_queried - relativedelta(**kwargs)

    # Generate X axis time labels for every data point
    for ordre, datapoint in enumerate(res['graphe']['data']):
        kwargs = {}
        kwargs[time_delta_unit] = ordre * inc
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

def generate_graph_from_data(res, title, time_delta_unit, time_format, ylegend, inc = 1):
    """Generates a graph from the given data.

    Parameters
    ----------
    res : dictionary
        The data to display in a graph.
    title : str
        The title of the graph.
    time_delta_unit : str
        The time unit that will be increased on the X axis.
    time_format : str
        The strftime format string for the X axis.
    ylegend : str
        The Y axis' legend.
    inc : number
        The amount by which the X axis will be increased with every step.
        See time_delta_unit.
    """
    # Generate the values to be plotted
    y_values = generate_y_axis(res)
    x_values = generate_x_axis(res, time_delta_unit, time_format, inc)

    width = .55
    max_power = res['graphe']['puissanceSouscrite']

    # Create the graph
    fig = plot.figure(num=None, figsize=(GRAPH_WIDTH_IN, GRAPH_HEIGHT_IN), dpi=GRAPH_DPI, facecolor='w', edgecolor='k')
    ind = np.arange(len(x_values))
    ax = fig.add_subplot(111)

    mpl.rcParams.update({'font.size': 10})

    # Draw the graph
    plot.bar(ind, y_values, width=width, color='k')
    plot.xticks(ind + width / 2, x_values)
    plot.ylabel(ylegend)
    plot.grid(True)
    plot.xlim([-width, len(x_values)])
    plot.title(title)

    # If we know the maximum power level that can be used by the user,
    # set the Y limit to that value. This way, the user will easily see
    # if they are close to their limit.
    if max_power > 0:
        plot.ylim([0, max_power])

    # If there are too many elements on the X axis, make it more compact
    if len(x_values) > 20:
        # Rotate labels
        fig.autofmt_xdate()

        if len(x_values) > 40:
            # If there are waaaaay too many elements, hide all labels
            # and only keep on out of four visible (plus the last one)
            for label in ax.xaxis.get_ticklabels():
                label.set_visible(False)
            for label in ax.xaxis.get_ticklabels()[::4]:
                label.set_visible(True)
            ax.xaxis.get_ticklabels()[-1].set_visible(True)
        else:
            # Hide every other label
            for label in ax.xaxis.get_ticklabels()[::2]:
                label.set_visible(False)

    return plot

def generate_graph_hours(res):
    """Generate and save the hourly energy consumption graph.
    """
    plot = generate_graph_from_data(res, "Puissance atteinte par demi-heure", 'hours', "%H:%M", "kW", 0.5)
    plot.savefig(OUTPUT_DIR + "/linky_hours.png", dpi=GRAPH_DPI)

def generate_graph_days(res):
    """Generate and save the daily energy consumption graph.
    """
    plot = generate_graph_from_data(res, "Consommation d'électricité par jour", 'days', "%d %b", "kWh")
    plot.savefig(OUTPUT_DIR + "/linky_days.png", dpi=GRAPH_DPI)

def generate_graph_months(res):
    """Generate and save the monthly energy consumption graph.
    """
    plot = generate_graph_from_data(res, "Consommation d'électricité par mois",'months', "%b", "kWh")
    plot.savefig(OUTPUT_DIR + "/linky_months.png", dpi=GRAPH_DPI)

def generate_graph_years(res):
    """Generate and save the yearly energy consumption graph.
    """
    plot = generate_graph_from_data(res, "Consommation d'électricité par année",'years', "%Y", "kWh")
    plot.savefig(OUTPUT_DIR + "/linky_years.png", dpi=GRAPH_DPI)

def dtostr(date):
    return date.strftime("%d/%m/%Y")

def main():
    today = datetime.date.today()

    try:
        print("logging in as " + username + "...")
        token = linky.login(username, password)
        print("logged in successfully!")

        print("retreiving data...")
        res_year = linky.get_data_per_year(token)

        # 6 months ago - today
        res_month = linky.get_data_per_month(token, dtostr(today - relativedelta(months=6)), dtostr(today))

        # One month ago - yesterday
        res_day = linky.get_data_per_day(token, dtostr(today - relativedelta(days=1, months=1)), dtostr(today - relativedelta(days=1)))

        # Yesterday - today
        res_hour = linky.get_data_per_hour(token, dtostr(today - relativedelta(days=2)), dtostr(today))
        print("got data!")

        print("generating graphs...")
        generate_graph_months(res_month)
        generate_graph_years(res_year)
        generate_graph_days(res_day)
        generate_graph_hours(res_hour)
        print("successfully generated graphs!")

    except linky.LinkyLoginException as e:
        print(e)

if __name__ == "__main__":
    main()
