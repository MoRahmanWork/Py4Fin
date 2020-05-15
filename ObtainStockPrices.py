import bs4 as bs
import pickle
import requests
import datetime as dt
import os 
import pandas as pd 
import pandas_datareader.data as web
# we want to find all the comapnies in SP500
def save_sp500_tickers():
    #the website
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #Web scrapping library called beautifulsoup
    soup = bs.BeautifulSoup(resp.text,'lxml')
    #find the table on the page
    table = soup.find('table', {'class':'wikitable sortable'})
    #empty tickers list. 
    tickers = []
    #for each table row
    for row in table.findAll('tr')[1:]: # skip the header of table
        ticker = row.findAll('td')[0].text # it is the first column
        tickers.append(ticker)
    #save it, write
    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers, f)
    print(tickers)
    return tickers
##save_sp500_tickers() 
# now we want to get all the stock prices
def get_data_from_yahoo(reload_sp500=False):
    # reload tickers
    if reload_sp500:
        # get tickers
        tickers = save_sp500_tickers()
    else: # read tickers
        with open("sp500tickers.pickle","rb") as f:
            tickers = pickle.load(f)
    # create directory to store stock prices locally
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    # We will look at stock prices over the past 5 year, starting at January 1, 2014
    start = dt.datetime(2014,1,1)
    end = dt.date.today()
    #get stock prices
    for ticker in tickers: #[:2]
        #show the stock currenrently being stored
        print(ticker)
        # create csv for each comapny stock price  and store in stocks folder
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            #information is from yahoo
            df = web.DataReader(ticker, 'yahoo', start, end)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print('Already have {}',format(ticker))
##get_data_from_yahoo()
# lets combine all the companies all together
def compile_data():
    #read
    with open("sp500tickers.pickle","rb") as f:
        tickers = pickle.load(f)
    main_df = pd.DataFrame() #empty dataframe
    #grab the close price information from each comapny. 
    for count,ticker in enumerate(tickers): #[:2]
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        #make the columns in df company names with prices in each day. 
        df.set_index('Date', inplace=True)
        df.rename(columns = {'Adj Close':ticker}, inplace=True)
        #drop infomration we dont need
        df.drop(['Open','High','Low','Volume', 'Close' ], 1, inplace=True)
        #adding the all the information into 1 df.
        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
        #if we are combining lots of data, count can be used to see how many are done
        if count % 10 == 0:
            print(count)
    print(main_df.head())
    #save this
    main_df.to_csv('sp500_joined_closes.csv')
#compile_data()
