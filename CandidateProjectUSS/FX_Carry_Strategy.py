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
        self.rebalancedates = dict()
        self.vix = dict()

    def getcurrencies(self):
        # grab currency, quotation styles, fxmult
        currdf = pd.read_csv(self.path + '/currency.csv', index_col=0)
        # currency dictionary
        self.currdict = currdf.to_dict(orient="index")

    def getspot(self):
        # grab spots
        # identify format of every date in csvs & change to datetime
        dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        for currency in self.currdict.keys():
            spotdf = pd.read_csv(self.path + '/data/' + currency + '_spot.csv',
                                 parse_dates=['Date'], date_parser=dateparse, index_col='Date')
            spotdf = spotdf.rename(lambda x: 'Spot' if currency in x else x, axis=1)
            self.currdict[currency]['Spotdata'] = spotdf

    def getforward(self):
        # grab forwards
        dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        for currency in self.currdict.keys():
            fwddf = pd.read_csv(self.path + '/data/' + currency + '_fwdp.csv',
                                parse_dates=['Date'], date_parser=dateparse, index_col='Date')
            fwddf = fwddf.rename(lambda x: 'Fwdp' if currency in x else x, axis=1)
            self.currdict[currency]['Fwdpdata'] = fwddf

    def getrebalancedates(self):
        # grab rebalance dates
        dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        rebaldf = pd.read_csv(self.path + '/data/RebalanceDates.csv',
                              parse_dates=['Date'], date_parser=dateparse, index_col='Date')
        self.rebalancedates = rebaldf.to_dict(orient="index")

    def getvix(self):
        # grab vix
        dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        vixdf = pd.read_csv(self.path + '/data/VIX.csv',
                            parse_dates=['Date'], date_parser=dateparse, index_col='Date')
        vixdf = vixdf.rename(lambda x: 'VIX' if 'VIX' in x else x, axis=1)
        self.vix = vixdf.to_dict(orient="index")

    def calcmarkets(self):
        # calculate forward rates
        for currency in self.currdict.keys():
            currdata = pd.merge(self.currdict[currency]['Spotdata'], self.currdict[currency]['Fwdpdata'], on='Date')
            currdata['Fwdrates'] = currdata['Spot'] + (self.currdict[currency]['fxMult'] * currdata['Fwdp'])
            if self.currdict[currency]['Quotation Style'] == 'American':
                self.markets[currency]['Spot'] = currdata[['Spot']].to_dict(orient="index")
                self.markets[currency]['Fwdrates'] = currdata[['Fwdrates']].to_dict(orient="index")
            if self.currdict[currency]['Quotation Style'] == 'European':
                self.markets[currency]['Spot'] = (1/currdata[['Spot']]).to_dict(orient="Index")
                self.markets[currency]['Fwdrates'] = (1/currdata[['Fwdrates']]).to_dict(orient="index")

    def runclass(self):
        self.getcurrencies()
        self.getspot()
        self.getforward()
        self.getrebalancedates()
        self.getvix()
        self.calcmarkets()




dirpath = r'C:\Users\44794\PycharmProjects\Py4Fin\CandidateProjectUSS'
markets = CurrencyMarkets(dirpath)
markets.runclass()

