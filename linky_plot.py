#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates energy consumption graphs from Enedis (ERDF) consumption data
collected via their infrastructure.
"""

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

import os
import datetime
import argparse
import logging
import sys

import linky

import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt

USERNAME = os.environ['LINKY_USERNAME']
PASSWORD = os.environ['LINKY_PASSWORD']

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
    for ordre, _ in enumerate(res['graphe']['data']):
        kwargs = {}
        kwargs[time_delta_unit] = ordre * inc
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

def generate_graph_from_data(res, title, time_delta_unit, time_format, ylegend, inc=1):
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
    logging.info("generating '%s' graph", title)

    # Generate the values to be plotted
    y_values = generate_y_axis(res)
    x_values = generate_x_axis(res, time_delta_unit, time_format, inc)

    width = .55
    max_power = res['graphe']['puissanceSouscrite']

    # Create the graph
    fig = plt.figure(num=None, figsize=(GRAPH_WIDTH_IN, GRAPH_HEIGHT_IN), dpi=GRAPH_DPI, \
                     facecolor='w', edgecolor='k')
    ind = np.arange(len(x_values))
    ax = fig.add_subplot(111)

    mpl.rcParams.update({'font.size': 10})
    mpl.rcParams.update({'font.family': 'serif'})
    mpl.rcParams.update({'text.usetex': True})
    mpl.rcParams.update({'text.latex.unicode': True})

    # Draw the graph
    plt.title(title, y=1.02)
    plt.grid(True)

    plt.bar(ind, y_values, width=width, color='k')
    plt.xticks(ind + width / 2, x_values)
    plt.xlim([-width, len(x_values)])
    plt.ylabel(ylegend)

    # If we know the maximum power level that can be used by the user,
    # set the Y limit to that value. This way, the user will easily see
    # if they are close to their limit.
    if max_power > 0:
        plt.ylim([0, max_power])

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
            for label in ax.xaxis.get_ticklabels()[(len(x_values)%2)::2]:
                label.set_visible(False)

    return plt

def generate_graph_hours(outdir, res):
    """Generate and save the hourly energy consumption graph."""
    plot = generate_graph_from_data(res, "Puissance atteinte par demi-heure", \
                                    'hours', "%H:%M", "\\textit{puissance} (kW)", 0.5)
    plot.savefig(outdir + "/linky_hours.png", dpi=GRAPH_DPI)

def generate_graph_days(outdir, res):
    """Generate and save the daily energy consumption graph."""
    plot = generate_graph_from_data(res, "Consommation d'électricité par jour", \
                                    'days', "%d %b", "\\textit{énergie} (kWh)")
    plot.savefig(outdir + "/linky_days.png", dpi=GRAPH_DPI)

def generate_graph_months(outdir, res):
    """Generate and save the monthly energy consumption graph."""
    plot = generate_graph_from_data(res, "Consommation d'électricité par mois", \
                                    'months', "%b", "\\textit{énergie} (kWh)")
    plot.savefig(outdir + "/linky_months.png", dpi=GRAPH_DPI)

def generate_graph_years(outdir, res):
    """Generate and save the yearly energy consumption graph."""
    plot = generate_graph_from_data(res, "Consommation d'électricité par année", \
                                    'years', "%Y", "\\textit{énergie} (kWh)")
    plot.savefig(outdir + "/linky_years.png", dpi=GRAPH_DPI)

def dtostr(date):
    return date.strftime("%d/%m/%Y")

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output-dir", type=str, default="out",
                        help="the directory in which the graphs will be placed")
    args = parser.parse_args()
    outdir = args.output_dir

    try:
        logging.info("logging in as %s...", USERNAME)
        token = linky.login(USERNAME, PASSWORD)
        logging.info("logged in successfully!")

        logging.info("retreiving data...")
        today = datetime.date.today()
        res_year = linky.get_data_per_year(token)

        # 6 months ago - today
        res_month = linky.get_data_per_month(token, dtostr(today - relativedelta(months=6)), \
                                             dtostr(today))

        # One month ago - yesterday
        res_day = linky.get_data_per_day(token, dtostr(today - relativedelta(days=1, months=1)), \
                                         dtostr(today - relativedelta(days=1)))

        # Yesterday - today
        res_hour = linky.get_data_per_hour(token, dtostr(today - relativedelta(days=1)), \
                                           dtostr(today))
        logging.info("got data!")

        logging.info("generating graphs...")
        generate_graph_months(outdir, res_month)
        generate_graph_years(outdir, res_year)
        generate_graph_days(outdir, res_day)
        generate_graph_hours(outdir, res_hour)
        logging.info("successfully generated graphs!")

    except linky.LinkyLoginException as exc:
        logging.error(exc)
        sys.exit(1)

if __name__ == "__main__":
    main()
