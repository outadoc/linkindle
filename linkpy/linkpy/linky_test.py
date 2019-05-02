#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Linkindle - Linky energy consumption curves on a Kindle display.
# Copyright (C) 2016-2019 Baptiste Candellier
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
from . import Linky, LinkyLoginException


def test():
    """Runs a quick test, logging into the Enedis website and getting some data."""
    username = os.environ['LINKY_USERNAME']
    password = os.environ['LINKY_PASSWORD']

    linky = Linky()

    try:
        print("logging in as " + username + "...")
        linky.login(username, password)
        print("logged in successfully")
        res = linky.get_data_per_day('27/10/2016', '30/10/2016')
        print(res)
    except LinkyLoginException as ex:
        print(ex)


if __name__ == "__main__":
    test()
