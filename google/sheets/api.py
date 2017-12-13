'''
Created on May 2, 2017

@author: wjgallag
'''

from google.api import Api
# from google.sheets.spreadsheet import Spreadsheet

class SheetsApi(Api):
    
    _name = 'sheets'
    _version = 'v4'
    
#     def get_spreadsheet(self, ssid):
#         return Spreadsheet(self.spreadsheets().get(spreadsheetId=ssid).execute())