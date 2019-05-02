#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieves energy consumption data from your Enedis (ERDF) account."""

# Linkpy - Fetch Linky energy consumption curves from an Enedis account.
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

import base64
import html
import requests

LOGIN_BASE_URI = 'https://espace-client-connexion.enedis.fr'
API_BASE_URI = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers'

API_ENDPOINT_LOGIN = '/auth/UI/Login'
API_ENDPOINT_HOME = '/home'
API_ENDPOINT_DATA = '/suivi-de-consommation'

DATA_NOT_REQUESTED = -1
DATA_NOT_AVAILABLE = -2

CUSTOM_HEADERS = {
    'User-Agent': 'Linkindle/1.0.0'
}


class LinkyLoginException(Exception):
    """Thrown if an error was encountered while retrieving energy consumption data."""


class LinkyServiceException(Exception):
    """Thrown when the webservice threw an exception."""


class Linky:
    """Handles calls to the Enedis website, allowing to retrieve Linky info."""

    def __init__(self):
        self.session = None

    def login(self, username, password):
        """Logs the user into the Linky API.
        """
        session = requests.Session()

        payload = {'IDToken1': username,
                   'IDToken2': password,
                   'goto': base64.b64encode('{}/accueil'.format(API_BASE_URI).encode()),
                   'gotoOnFail': '',
                   'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
                   'encoded': 'true',
                   'gx_charset': 'UTF-8'}

        session.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload,
                     headers=CUSTOM_HEADERS, allow_redirects=False)

        if 'iPlanetDirectoryPro' not in session.cookies:
            raise LinkyLoginException(
                "Login unsuccessful. Check your credentials.")

        self.session = session

    def get_data_per_hour(self, start_date, end_date):
        """Retrieves hourly energy consumption data."""
        return self._get_data('urlCdcHeure', start_date, end_date)

    def get_data_per_day(self, start_date, end_date):
        """Retrieves daily energy consumption data."""
        return self._get_data('urlCdcJour', start_date, end_date)

    def get_data_per_month(self, start_date, end_date):
        """Retrieves monthly energy consumption data."""
        return self._get_data('urlCdcMois', start_date, end_date)

    def get_data_per_year(self):
        """Retrieves yearly energy consumption data."""
        return self._get_data('urlCdcAn')

    def _get_data(self, resource_id, start_date=None, end_date=None):
        req_part = 'lincspartdisplaycdc_WAR_lincspartcdcportlet'

        # We send the session token so that the server knows who we are
        payload = {
            '_' + req_part + '_dateDebut': start_date,
            '_' + req_part + '_dateFin': end_date
        }

        params = {
            'p_p_id': req_part,
            'p_p_lifecycle': 2,
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_resource_id': resource_id,
            'p_p_cacheability': 'cacheLevelPage',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': 1,
            'p_p_col_count': 3
        }

        req = self.session.post(API_BASE_URI + API_ENDPOINT_DATA, allow_redirects=False,
                                headers=CUSTOM_HEADERS, data=payload, params=params)

        if 300 <= req.status_code < 400:
            # So... apparently, we may need to do that once again if we hit a 302
            # ¯\_(ツ)_/¯
            req = self.session.post(API_BASE_URI + API_ENDPOINT_DATA, allow_redirects=False,
                                    headers=CUSTOM_HEADERS, data=payload, params=params)

        if req.status_code == 200 \
                and req.text is not None \
                and "Conditions d'utilisation" in req.text:
            raise LinkyLoginException("You need to accept the latest Terms of Use. "
                                      "Please manually log into the website, "
                                      "then come back.")

        res = req.json()

        if res['etat'] and res['etat']['valeur'] == 'erreur' and res['etat']['erreurText']:
            raise LinkyServiceException(
                html.unescape(res['etat']['erreurText']))

        return res
