'''
Created on May 4, 2017

@author: wjgallag
'''

import re
import unicodedata  # @UnresolvedImport

from google import Client, ServiceAccount
import itertools

def sheet_cells(sheet, cellrange):
    return sheet + '!' + cellrange

def cells(start, end, sheet=None):
    return (sheet + '!' if sheet is not None else '') + str(start) + ':' + str(end)

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
    
    _rsvp_id = '1MB5M2RURsmlPGdwL1dKMDIFLQg1pyuu5LoS8cClUt5g'
    
    _header_rows = 2
    
    _headers = {}
    _types = {}
    
    _data_sheet = 'Data'
    _data_range = col_range('A', 'I')
    _data_id_col = 'A'
    _data_code_col = 'B'
    _data_last_name = 'last_names'
    
    _response_sheet = 'RSVP'
    _response_range = col_range('A', 'F')
    _response_id_col = 'A'

    def __init__(self):
        Client.__init__(self, ServiceAccount('bandb-google.json', 'https://www.googleapis.com/auth/spreadsheets'))
        self.connect()
    
    def connect(self):
        self.login().build('sheets', 'v4')
        
    def _get_values(self, sheet, crange):
#         try:
            return self.spreadsheets().values().get(spreadsheetId=self._rsvp_id, range=sheet_cells(sheet, crange)).execute()['values']
#         except:
#             return None
    
    def _format_data(self, data, sheet):
        if (sheet not in self._types or sheet not in self._headers):
                headers = self._get_values(sheet, cells(1, 2))
                self._headers[sheet] = [re.sub('[^0-9a-zA-Z]+', '_', normalize(s.strip())) for s in headers[0]]
                self._types[sheet] = [t.strip() for t in headers[1]]
        return [self._to_dict([self._convert(c, t) for c, t in itertools.zip_longest(r, self._types[sheet])], self._headers[sheet]) for r in data]
    
    def _convert(self, data, datatype):
        if (data is None or data is ''):
            return None
        if (datatype == 'int'):
            f = lambda x: int(x.strip())
        elif (datatype == 'bool'):
            f = lambda x: normalize(x) in normalize(['true', 't', '1', 'y', 'yes'])
        else:
            f = lambda x: x
        if (';' in data):
            return [f(d.strip()) for d in self._split_list_col(data)]
        else:
            return f(data.strip())
    
    def _to_dict(self, data, headers):
        return dict(itertools.zip_longest(headers, data))
    
    def _col_index(self, col):
        return [c for c in self._data_range].index(col)
    
    def _split_list_col(self, col_data):
        for l in col_data.split(';'):
            yield l.strip()
    
    def get_invitee(self, **kwargs):
#         try:
            if ('rsvp_id' in kwargs and isinstance(kwargs['rsvp_id'], int)):
                return self._get_invitee_by_rsvp_id(kwargs['rsvp_id'])
            elif ('invite_code' in kwargs and isinstance(kwargs['invite_code'], str) and 'last_name' in kwargs and isinstance(kwargs['last_name'], str)):
                return self._get_invitee_by_code_and_last_name(kwargs['invite_code'], kwargs['last_name'])
            else:
                raise ValueError('Cannot get invitee from the provided arguments: ' + str(kwargs))
#         except:
#             return None
       
    def _get_invitee_by_rsvp_id(self, rsvp_id):
        rownum = self._get_values(self._data_sheet, col(self._data_id_col)).index([str(rsvp_id)]) + 1
        data = self._format_data(self._get_values(self._data_sheet, row(rownum)), self._data_sheet)[0]
        return data
    
    def _get_invitee_by_code_and_last_name(self, invite_code, last_name):
#         try:
            rownum = self._get_values(self._data_sheet, col(self._data_code_col)).index([invite_code]) + 1
            data = self._format_data(self._get_values(self._data_sheet, row(rownum)), self._data_sheet)[0]
            if (normalize(last_name) not in normalize(data[self._data_last_name])):
                return None
            return data
#         except:
#             return None

    def has_rsvp(self, rsvp_id):
        try:
            return (self.get_rsvp(rsvp_id) is not None)
        except:
            return False
        
    def get_rsvp(self, rsvp_id):
        rownum = self._get_values(self._response_sheet, col(self._response_id_col)).index([rsvp_id]) + 1
        return None



