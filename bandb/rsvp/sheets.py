'''
Created on May 4, 2017

@author: wjgallag
'''

import json
import re
import unicodedata  # @UnresolvedImport

from datetime import datetime
from pytz import timezone

from google import Client, ServiceAccount
import itertools

def cells(start=None, end=None, sheet=None, crange=None, cell=None):
    if (start is not None):
        crange = str(start)
        if (end is not None):
            crange += ':' + str(end)
    elif (cell is not None):
        crange = cell
    return (sheet if sheet is not None else '') + ('!' if sheet is not None and crange is not None else '') + (crange if crange is not None else '')

def row(row, sheet=None):
    return cells(str(row), str(row), sheet)

def col(col, sheet=None):
    return row(str(col), sheet)

def col_range(start, end):
    col = start.upper()
    while (not col == end.upper()):
        yield col
        col = next_col(col)

def next_col(col):
    if (not len(col)):
        return 'A'
    elif (col[-1] == 'Z'):
        return (next_col(col[:-1]) + 'A')
    else:
        return (col[:-1] + chr(ord(col[-1])+1))

#TODO: Some of these functions seem more appropriate to be in a string utility module
def normalize(text):
    if (isinstance(text, str)):
        return unicodedata.normalize('NFKD', text.casefold())
    elif (isinstance(text, dict)):
        return {k: normalize(i) for k, i in text.items()}
    elif (isinstance(text, tuple)):
        return tuple(normalize(t) for t in text)
    elif (isinstance(text, set)):
        return set(normalize(t) for t in text)
    return [normalize(t) for t in text]

def caseless_equal(left, right):
    return normalize(left) == normalize(right)

class RsvpSheet(Client):

    _error = None

    _rsvp_id = '1MB5M2RURsmlPGdwL1dKMDIFLQg1pyuu5LoS8cClUt5g'

    _header_rows = 1

    _headers = {}
#     _types = {}

    _data_sheet = 'Data'
    _data_range = col_range('A', 'J')
    _data_id_col = 'A'
    _data_code_col = 'B'
    _data_last_name = 'last_names'

    _response_sheet = 'RSVP'
    _response_range = col_range('A', 'J')
    _response_id_col = 'A'

    def __init__(self):
        key = {
          "type": "service_account",
          "project_id": "studious-matrix-166415",
          "private_key_id": "4e674b9645ec8d9df3bd972ab79e7290692afc70",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCizVpjH2ibF/eZ\nFVUurERyJvOFF5mGCwf/n0fNSZvuRWuu0J0sMVHqBJ8o23o/PxHzoj2QeFfa+hFe\nHzaYVchxoC2rbPwrJ3NtwESwuWpreH+iXMedERfbbF3x3C6JL0SSF/C2acrKFOUs\niODLvxaigYd9fpPtKpSMSmTnbOrtD0lzwQh9LmFlxOE0jMoGxUOCua7CsPc3/ecq\nK+8acW6W0GjiVxucHBj0r/UOMhlweS5b3nR0GsVnVFGuE5g0VgnSAl9/wj47fhbr\nvTcQH1GBRZcRgdupCWOjQTAEtR7JdKOnPPE4ruz0tgrhiazgLi3BFbkGYHLFKfPe\nWat8zWczAgMBAAECggEAfs1delkLW8l2IzjXaQvqH9Mw11gDTsEm0LXZ8g5EMnjF\nn5qC4NnlSFWjNeqEs+BG9jFGrFDfdQJTJrE/D7W48q9lAuFXI7GNmU0o81Dnj5+C\nIg8Lts2KfHBSV8A8SsOTMAsPhLSvq2hM+7v9AxTp51bmFhvR0ebZXs/O+eX+sPZ3\n3fTlIaaHUlGJV1ofwVEdoIF09ZJ1qmZ7s6ide+W7HPiA8xQuIvP3LPGFOtb+azcN\nxNn9NIGqDCyKbRRopbql4gLhAuYFmWxLFMg09SSxKsZCI2Co/0v66fxtu3IcKMQB\nOvmRTtwhFeto915YqlbuEW/kriUe/yfG6bNwitzbsQKBgQDmGipo4uzHwrk4po0E\nAbhUI8TJ1Ev+ruEjUcediZY7qHolpvlfoQraPDd4ptjP6jSori4RGdOPxN6b46SU\njDuemBbT1NFHm/vpfAkF+gHc0j5gs8UPXwG1vDa/uTH1LMZwldGbLQonFsil/hIZ\nO4q+uGYEPpexhzt/mVyBVoPeKwKBgQC1IBm8JCfJgfDndKZplnOLxCrny3TguB0p\nJCeWzEFHJhFN5ClYORrLE3FMXxpKSm8lc+ANVvvdF6WJcstOF1+ipU5vUWpCEbrW\nJEYqOpedMvNOu1Oq+Tm5ibOVBZOQbc1/z3sNYiSwwLOMr2SUPIpQzjrFhqIJdEMX\nDg5M4NCfGQKBgGBCIeuuwo7ujr18LxG2Bn5sWC52eTQZxGUaGP92Rzq9yBtoNnoi\nzH9vIWV/psOTnmPSOcM9optKKDXejUL3RxmZVjNXnBTw0/lgwgWWCKFv8lhR2+YK\nQJTeH6kkuBlwmbMPeZgIx26CwX1vQ/L6TZhrW4H7DUpe4C0I4wHYR2HxAoGAN4Xh\nnbUPpUv6B1nQ8ak3Pm8iH/BUodaOyd/VavquQBtBTrlUm0DWH86T+q9kpcVvkPGW\ni0BQ8ROgoSPZgtTTck5uXt18T0iUF7UC9UsE0yGdSFNQcKb5tRCrRlFxTOL8DeQS\neqXNTYmlAMl7cZ2lYOP3TDnbTj6fml+qrpJ0IXECgYB9q0qvBkWx9Chua3jsy62s\nwdK9klUf85TjVFc5VBbP7aBd1+b59NhllcgE98o+ioPP+UE0Arcru5ba9Ejs0FZ5\nwwWguKohX6NqUeEEDNjDLwkI3pV8IKQ7q4lRhg38v3DR3ysftfoQxEYpppF85Hao\n8aHPmCI+8YWrFY09D0Yn0g==\n-----END PRIVATE KEY-----\n",
          "client_email": "wedding-rsvp@studious-matrix-166415.iam.gserviceaccount.com",
          "client_id": "110168558618337623485",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://accounts.google.com/o/oauth2/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/wedding-rsvp%40studious-matrix-166415.iam.gserviceaccount.com"
        }
        Client.__init__(self, ServiceAccount(key, 'https://www.googleapis.com/auth/spreadsheets'))
        try:
            self.connect()
        except Exception as exc:
            _error = exc

    def connect(self):
        self.login().build('sheets', 'v4')

    def has_error(self):
        return self._error is not None

    def get_error(self):
        return self._error

    def _get_values(self, crange):
        if (self.has_error()):
            return None
#         try:
        return self.spreadsheets().values().get(spreadsheetId=self._rsvp_id, range=crange, valueRenderOption='UNFORMATTED_VALUE').execute()['values']
#         except Exception as exc:
#             self._error = exc
#             return None

    def _append_values(self, data, crange, raw=False):
        if (self.has_error()):
            return False
#         try:
        return self.spreadsheets().values().append(spreadsheetId=self._rsvp_id, range=crange, valueInputOption=('RAW' if raw else 'USER_ENTERED'), body={'values': data}).execute()['updates']['updatedRange']
#         except Exception as exc:
#             self._error = exc
#         return False

    def _format_data(self, data, sheet):
        if (sheet not in self._headers):
            headers = self._get_values(cells(sheet=sheet, start=1, end=2))
            self._headers[sheet] = [re.sub('[^0-9a-zA-Z]+', '_', normalize(s.strip())) for s in headers[0]]
        return [dict(itertools.zip_longest(self._headers[sheet], [self._clean(d) for d in r])) for r in data]

    def _clean(self, data):
        if (not isinstance(data, str)):
            return data
        if (data is ''):
            return None
        if (';' in data):
            return [d.strip() for d in data.split(';')]
        else:
            return data.strip()

    def _col_index(self, col):
        return [c for c in self._data_range].index(col)

    def get_invitee(self, **kwargs):
        if ('rsvp_id' in kwargs and isinstance(kwargs['rsvp_id'], int)):
            return self._get_invitee_by_rsvp_id(kwargs['rsvp_id'])
        elif ('invite_code' in kwargs and isinstance(kwargs['invite_code'], str) and 'last_name' in kwargs and isinstance(kwargs['last_name'], str)):
            return self._get_invitee_by_code_and_last_name(kwargs['invite_code'], kwargs['last_name'])
        else:
            raise ValueError('Cannot get invitee from the provided arguments: ' + str(kwargs))

    def _get_invitee_by_rsvp_id(self, rsvp_id):
        try:
            rownum = self._get_values(col(self._data_id_col, self._data_sheet)).index([rsvp_id]) + 1
        except ValueError:
            return None
        data = self._format_data(self._get_values(row(rownum, self._data_sheet)), self._data_sheet)[0]
        return data

    def _get_invitee_by_code_and_last_name(self, invite_code, last_name):
        try:
            rownum = self._get_values(col(self._data_code_col, self._data_sheet)).index([invite_code]) + 1
        except ValueError:
            return None
        data = self._format_data(self._get_values(row(rownum, self._data_sheet)), self._data_sheet)[0]
        if (normalize(last_name) not in normalize(data[self._data_last_name])):
            return None
        return data

    def has_rsvp(self, rsvp_id):
        try:
            return (self.get_rsvp(rsvp_id) is not None)
        except:
            return False

    def get_rsvp(self, rsvp_id):
        try:
            rownum = self._get_values(col(self._response_id_col, self._response_sheet)).index([rsvp_id]) + 1
        except ValueError:
            return None
        data = self._format_data(self._get_values(row(rownum, self._response_sheet)), self._response_sheet)[0]
        return data

    def save_rsvp(self, rsvp_id, addressee, people=None, guest=False, email=None, lodging=None, songs=None, diet=None, extras=None):
        if (guest):
            people[-1] = people[-1] + '(Guest of ' + addressee + ')'
        row = [
            rsvp_id,
            datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
            addressee,
            ';'.join(people) if people else '',
            len(people) if people else 0,
            email if email else '',
            lodging if lodging else '',
            ';'.join(songs) if songs else '',
            diet if diet else '',
            ';'.join(extras) if extras else ''
        ]
        return self._append_values([row], self._response_sheet)

