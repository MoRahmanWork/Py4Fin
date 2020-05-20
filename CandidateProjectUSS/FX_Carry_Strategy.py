import pandas as pd
import numpy as np
import datetime as dt
import dateutil.parser

class dict(dict):
    """create missing dictionary keys"""
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class CurrencyMarkets:
    """get market data"""

    def __init__(self, path=''):
        self.path = path
        self.currdict = dict()
        self.markets = dict()

    def getcurrencies(self):
        # grab currency, quotation styles, fxmult
        currdf = pd.read_csv(self.path + '/currency.csv', index_col=0)
        # currency dictionary
        self.currdict = currdf.to_dict(orient="index")

    def getspot(self):
        # grab spots
        # identify format of every date in csvs & change to datetime
        dateparse = lambda x: dateutil.parser.parse(x)
        for currency in self.currdict.keys():
            spotdf = pd.read_csv(self.path + '/data/' + currency + '_spot.csv',
                                 parse_dates=['Date'], date_parser=dateparse, index_col='Date')
            self.currdict[currency]['Spot'] = spotdf.to_dict(orient="index")

    def getforward(self):
        # grab forwards
        dateparse = lambda x: dateutil.parser.parse(x)
        for currency in self.currdict.keys():
            spotdf = pd.read_csv(self.path + '/data/' + currency + '_fwdp.csv',
                                 parse_dates=['Date'], date_parser=dateparse, index_col='Date')
            self.currdict[currency]['Spot'] = pd.read_csv(self.path + '/data/' + currency + '_spot.csv',
                                                          parse_dates=['Date'], date_parser=dateparse, index_col=0)




dirname = r'C:\Users\44794\PycharmProjects\Py4Fin\CandidateProjectUSS'
