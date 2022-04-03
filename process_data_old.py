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
    df = dataframe1.rename(columns={"Column1": "dateid", "Column2": "price","Column3":"volume"})

    dateparse = lambda x: datetime.datetime.utcfromtimestamp(float(x))
    df['date'] = [dateparse(x) for x in df['dateid']]
    df = df.set_index('date')
    del df['dateid']
    df['ask'] = df['price']*1.005
    df['bid'] = df['price']*0.995
    df = df.reindex(columns=['price','ask','bid','volume'])
    
    #df['prev'] = df['price'].rolling(2).apply(lambda x: (x[1]/x[0])-1 ,raw=True)
    
    #df['ma100']=df['price']/df['price'].rolling(10).mean()-1
    df['ma10001']=df['price']/df['price'].rolling('15min').mean()-1
    #df['ma10002']=df['price']/df['price'].rolling('15min').max()-1
    #df['ma10003']=df['price']/df['price'].rolling('15min').min()-1

    df['ma1000x1']=df['price']/df['price'].rolling('1h').mean()-1
    df['ma1000x2']=df['price']/df['price'].rolling('1h').max()-1
    df['ma1000x3']=df['price']/df['price'].rolling('1h').min()-1
    #df['ma1000x4'] = df['ma1000x1'] / df['price'].rolling('1h').std()

    df['ma1000y1']=df['price']/df['price'].rolling('10h').mean()-1
    #df['ma1000y2']=df['price']/df['price'].rolling('10h').max()-1
    #df['ma1000y3']=df['price']/df['price'].rolling('10h').min()-1

    df['ma100001']=df['price']/df['price'].rolling('1D').mean()-1
    #df['ma100002']=df['price']/df['price'].rolling('1D').max()-1
    #df['ma100003']=df['price']/df['price'].rolling('1D').min()-1
    #df['ma100004'] = df['ma100001'] / df['price'].rolling('1D').std()
    df['ma1']=df['price']/df['price'].rolling('10D').mean()-1
    #df['ma2']=df['price']/df['price'].rolling('10D').max()-1
    #df['ma3']=df['price']/df['price'].rolling('10D').min()-1
    df['ma4'] = df['ma1'] / df['price'].rolling('10D').std()
    df['mafff1']=df['price']/df['price'].rolling('20D').mean()-1
    df['mafff2']=df['price']/df['price'].rolling('20D').max()-1
    df['mafff3']=df['price']/df['price'].rolling('20D').min()-1
    df['mafff4'] = df['mafff1'] / df['price'].rolling('20D').std()
    df = df.dropna()
    
    
    
    return df