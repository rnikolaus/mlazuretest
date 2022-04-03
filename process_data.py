# The script MUST contain a function named azureml_main
# which is the entry point for this module.

# imports up here can be used to
import pandas as pd

# The entry point function MUST have two input arguments.
# If the input port is not connected, the corresponding
# dataframe argument will be None.
#   Param<dataframe1>: a pandas.DataFrame
#   Param<dataframe2>: a pandas.DataFrame
def azureml_main(dataframe1 = None, dataframe2 = None):

    # Execution logic goes here
    print(f'Input pandas.DataFrame #1: {dataframe1}')

    from azureml.core import Dataset
    from azureml.core import Workspace
    import datetime

    #ws = Workspace.from_config()
    #dataset = Dataset.get_by_name(ws, name='btc-raw')
    
    #df = dataset.to_pandas_dataframe()
    df = dataframe1.rename(columns={"Timestamp": "dateid", "Close": "price","Volume_(BTC)":"volume"})
    df = df.drop([2349652,38526,45313,672665])
    dateparse = lambda x: datetime.datetime.utcfromtimestamp(float(x))
    df['date'] = [dateparse(x) for x in df['dateid']]
    df = df.set_index('date')
    df = df.sort_index()
    del df['dateid']
    df['ask'] = df['price']*1.005
    df['bid'] = df['price']*0.995
    df = df.reindex(columns=['price','ask','bid','volume','High','Low'])
    
    def delta(timeseriesShort, timeseriesLong):
        return ((timeseriesShort/timeseriesLong)-1).clip(-3,3)

    def addMa(timeframe):
        p=df['price']
        df['ma'+timeframe] = delta(p,p.rolling(timeframe).mean())

    def add2Ma(timeframeshort, timeframelong):
        p=df['price']
        df['ma'+timeframeshort+'_'+timeframelong] =delta(p.rolling(timeframeshort).mean(),p.rolling(timeframelong).mean())


    def addMinMax(timeframe,periods,freq):
        p=df['price']
        dfs = df.shift(periods=periods, freq=freq)
        mins = dfs['Low'].rolling(timeframe).min()
        df['maxmin'+timeframe]=((p - mins)/(dfs['High'].rolling(timeframe).max() - mins)).clip(-3,3)
    

    def addBol(timeframe):
        p=df['price']
        df['bol'+timeframe] = (delta(p,p.rolling(timeframe).mean())/p.rolling(timeframe).std()).clip(-3,3)

    def addStdDir(timeframe,periods,freq):
        p=df['price']
        val=p.rolling(timeframe).std()
        df['stddir'+timeframe] = delta(val,val.shift(periods=periods, freq=freq))

    def addMaDir(timeframe,periods,freq):
        p=df['price']
        val = p.rolling(timeframe).mean()
        df['madir'+timeframe] = delta(val,val.shift(periods=periods, freq=freq))

    def zigzag(df,percent):
        from collections import deque
        import numpy as np
        import pandas as pd

        res = deque([np.nan]*5,maxlen=5)
        val= None
        up=True
        factor = percent/100.0
        result = {}
        for row in df.itertuples(index=True):
            if val == None: 
                val=row.price
            if up:
                if val < row.ask:
                    val=row.ask
                elif val*(1-factor) > row.bid:
                    res.appendleft(val)
                    up=False
                    val = row.bid
            else:
                if val > row.bid:
                    val=row.bid
                elif val*(1+factor) < row.ask:
                    res.appendleft(val)
                    up=True
                    val = row.ask
            result[row.Index]=[(row.price/res[0])-1,(row.price/res[1])-1,(row.price/res[2])-1,(row.price/res[3])-1,(row.price/res[4])-1]
        df2=pd.DataFrame.from_dict(result, orient='index',columns=['Zigzag_'+str(percent)+'_0', 'Zigzag_'+str(percent)+'_1', 'Zigzag_'+str(percent)+'_2', 'Zigzag_'+str(percent)+'_3', 'Zigzag_'+str(percent)+'_4']).clip(-3,3)
        return df.join(df2,how='left')



    addMa('5min')
    addMa('15min')
    addMa('1h')
    addMa('5D')
    addMa('20D')
    addBol('5D')
    addBol('20D')
    addMinMax('50h',1,"h")
    addMinMax('10D',1,"D")
    add2Ma('6min','13min')
    add2Ma('6h','13h')
    add2Ma('30h','65h')
    addMaDir('15min',5,"min")
    addMaDir('5D',5,"min")
    addStdDir('1D',5,"min")
    addStdDir('10D',5,"min")
    addStdDir('20D',5,"min")


    df = zigzag(df,5)
    df = zigzag(df,10)
    df = zigzag(df,15)
   
   
    df = df.dropna()
    
    del df['High']
    del df['Low']

    return df