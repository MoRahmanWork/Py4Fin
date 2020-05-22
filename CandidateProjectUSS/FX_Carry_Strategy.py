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
        self.rebalancedates = pd.DataFrame()
        self.vix = pd.DataFrame()

    def getcurrencies(self):
        # grab currency, quotation styles, fxmult
        currdf = pd.read_csv(self.path + '/currency.csv', index_col=0)
        # currency dictionary
        self.currdict = currdf.to_dict(orient="index")

    def getspot(self):
        # grab spots
        # identify format of every date in csvs & change to datetime
        for currency in self.currdict.keys():
            spotdf = pd.read_csv(self.path + '/data/' + currency + '_spot.csv',
                                 parse_dates=['Date'], date_parser=lambda x: dateutil.parser.parse(x, dayfirst=True),
                                 index_col='Date')
            spotdf = spotdf.rename(lambda x: 'Spot' if currency in x else x, axis=1)
            self.currdict[currency]['Spotdata'] = spotdf

    def getforward(self):
        # grab forwards
        # dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        for currency in self.currdict.keys():
            fwddf = pd.read_csv(self.path + '/data/' + currency + '_fwdp.csv',
                                parse_dates=['Date'], date_parser=lambda x: dateutil.parser.parse(x, dayfirst=True),
                                index_col='Date')
            fwddf = fwddf.rename(lambda x: 'Fwdp' if currency in x else x, axis=1)
            self.currdict[currency]['Fwdpdata'] = fwddf

    def getrebalancedates(self):
        # grab rebalance dates
        # dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        rebaldf = pd.read_csv(self.path + '/data/RebalanceDates.csv',
                              parse_dates=['Date'], date_parser=lambda x: dateutil.parser.parse(x, dayfirst=True),
                              index_col='Date')
        self.rebalancedates = rebaldf

    def getvix(self):
        # grab vix
        # dateparse = lambda x: dateutil.parser.parse(x, dayfirst=True)
        vixdf = pd.read_csv(self.path + '/data/VIX.csv',
                            parse_dates=['Date'], date_parser=lambda x: dateutil.parser.parse(x, dayfirst=True),
                            index_col='Date')
        vixdf = vixdf.rename(lambda x: 'VIX' if 'VIX' in x else x, axis=1)
        self.vix = vixdf

    def calcmarkets(self):
        # calculate forward rates
        for currency in self.currdict.keys():
            currdata = pd.merge(self.currdict[currency]['Spotdata'], self.currdict[currency]['Fwdpdata'], on='Date')
            currdata['Fwdrates'] = currdata['Spot'] + (self.currdict[currency]['fxMult'] * currdata['Fwdp'])

            if self.currdict[currency]['Quotation Style'] == 'American':
                self.markets[currency]['Spot'] = currdata[['Spot']].rename(
                    lambda x: currency if 'Spot' in x else x, axis=1)
                self.markets[currency]['Fwdrates'] = currdata[['Fwdrates']].rename(
                    lambda x: currency if 'Fwdrates' in x else x, axis=1)
            if self.currdict[currency]['Quotation Style'] == 'European':
                self.markets[currency]['Spot'] = 1 / currdata[['Spot']].rename(
                    lambda x: currency if 'Spot' in x else x, axis=1)
                self.markets[currency]['Fwdrates'] = 1 / currdata[['Fwdrates']].rename(
                    lambda x: currency if 'Fwdrates' in x else x, axis=1)

        masterspot = pd.DataFrame()
        masterfwdrates = pd.DataFrame()
        for currency in self.markets.keys():
            masterspot = pd.concat([masterspot, self.markets[currency]['Spot']], axis=1, join='outer').ffill()
            masterfwdrates = pd.concat([masterfwdrates, self.markets[currency]['Fwdrates']], axis=1,
                                       join='outer').ffill()

        datesrange = pd.DataFrame(index=pd.bdate_range(start='1/1/2000', end=dt.datetime.today()))
        self.markets['Spotdf'] = pd.concat([datesrange, masterspot], axis=1, join='inner')
        self.markets['Fwdratesdf'] = pd.concat([datesrange, masterfwdrates], axis=1, join='inner')

    def runclass(self):
        self.getcurrencies()
        self.getspot()
        self.getforward()
        self.getrebalancedates()
        self.getvix()
        self.calcmarkets()


class Backtest(CurrencyMarkets):

    def __init__(self, path='', notional=0, startdt='1/1/2000'):
        super().__init__(path=path)
        self.notional = notional
        self.mins = pd.DataFrame()
        self.maxs = pd.DataFrame()
        self.startdt = startdt
        self.enddt = dt.datetime.today()
        self.allres = []

    def runcurrencymarkets(self):
        self.runclass()

    def maxmin(self):
        rebalrates = pd.concat([self.rebalancedates, self.markets['Fwdratesdf']], axis=1, join='inner')
        self.mins = rebalrates.idxmin(axis=1, skipna=True)
        self.maxs = rebalrates.idxmax(axis=1, skipna=True)

    def calcweightscarry(self, date, method):
        rebalancedrate = pd.concat([self.rebalancedates, self.markets['Fwdratesdf']], axis=1, join='inner')
        rebalancedrate = rebalancedrate.loc[[date]]
        longcur, longwei, shortcur, shortwei, longcar, shortcar = 0
        if method == 1:
            rankedrates = rebalancedrate.loc[[date]].rank(1, ascending=True, method='first')
            longcur = rankedrates.loc[date].idxmax()
            longwei = 1 / rankedrates.loc[date].max()
            shortcur = rankedrates.loc[date].idxmin()
            shortwei = -1 / rankedrates.loc[date].max()
        elif method == 2:
            test = ''
        elif method == 3:
            test = ''
        elif method == 4:
            test = ''

        longcar = np.log(np.divide(self.markets['Spotdf'].loc[date, longcur],
                                   self.markets['Fwdratesdf'].loc[date, longcur]))
        shortcar = np.log(np.divide(self.markets['Spotdf'].loc[date, shortcur],
                                   self.markets['Fwdratesdf'].loc[date, shortcur]))

        return longcur, longwei, shortcur, shortwei, longcar, shortcar

    def runbacktest(self):
        datesrange = pd.bdate_range(start=self.startdt, end=self.enddt)

        for dts in datesrange:
            date = dts.date()
            r = weightL*CarryL + weightS*CarryS
            idxlvl = rebalidxlvl * (1 + r)
            if date in self.rebalancedates.index:
                emptylist = []
                method = 1
                longcurr, longweight, shortcurr, shortweight, longcarry, shortcarry = self.calcweightscarry(date, method)


            print(dts)


dirpath = r'C:\Users\44794\PycharmProjects\Py4Fin\CandidateProjectUSS'
notionals = 10000
startdate = '1/1/2000'
t = Backtest(dirpath, notionals, startdate)
t.runclass()
t.maxmin()
t.runbacktest()
