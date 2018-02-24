'''
Created on May 4, 2017

@author: wjgallag
'''

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
    _data_range = col_range('A', 'I')
    _data_id_col = 'A'
    _data_code_col = 'B'
    _data_last_name = 'last_names'

    _response_sheet = 'RSVP'
    _response_range = col_range('A', 'I')
    _response_id_col = 'A'

    def __init__(self):
        Client.__init__(self, ServiceAccount('bandb-google.json', 'https://www.googleapis.com/auth/spreadsheets'))
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

    def save_rsvp(self, rsvp_id, addressee, people=None, guest=False, email=None, lodging=None, songs=None, diet=None):
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
            diet if diet else ''
        ]
        return self._append_values([row], self._response_sheet)

