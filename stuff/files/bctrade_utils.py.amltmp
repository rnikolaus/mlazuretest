import gym
from gym import spaces
import random
import numpy as np
import pandas as pd
import datetime

def getData(): 
    dateparse = lambda x: datetime.datetime.utcfromtimestamp(float(x))
    df = pd.read_csv('bitbayEUR.csv',names=['date','price','volume'], parse_dates=['date'], date_parser=dateparse,index_col=0)

    df['ask'] = df['price']*1.0
    df['bid'] = df['price']*1.0
    df = df.reindex(columns=['price','ask','bid','volume'])
    return df
def getDataFromDs(name):
   
    from azureml.core import Run, Dataset
    run = Run.get_context()
    dataset = Dataset.get_by_name(run.experiment.workspace, name=name)
    df = dataset.to_pandas_dataframe()
    return df 



def registerBCTrade(name,singlerun=True,spreadfactor=1.0):
    from ray.tune.registry import register_env
    
    def env_creator(env_config):
        return BCTrade(getDataFromDs(name),singlerun,spreadfactor)
    
    envname="BCTrade-"+name

    register_env(envname, env_creator)
    return envname


class tradeclass:
    
    def __init__(self,initial=1000.0):
        self.currentval = initial
        self.prevval = initial
        self.state = 'out'
        self.validactions={'out':{'buy':self.buy,'ignore':self.nothing},
                           'in':{'sell':self.sell,'hold':self.nothing}}
        self.amount=0.0
        
        self.ask = 0.0
        self.bid = 0.0
        
        self.max =0
        self.maxvalue=initial
        self.initial= initial
        
    
        
    def getactions(self):
        return list(self.validactions[self.state].keys())
    def act(self,choice,ask,bid):
        self.prevval = self.getvalue()
        self.ask= ask
        self.bid=bid
        if self.ask>self.max:
            self.max = self.ask
        if choice in self.getactions():
            self.validactions[self.state][choice]()
        else:
            self.nothing()
        maxval = self.getvalue()
        if maxval> self.maxvalue:
            self.maxvalue=maxval
        
    
        
    def getvalue(self):
        return self.currentval + self.amount* self.bid
    
    def isIn(self):
        return self.state != 'out'
        
    
    def getreward(self):
        #if not self.isIn():
        #    return 0.0
        #return (self.bid/self.buyprice)-1
        return self.getvalue()-self.prevval
    
    def getdrawdown(self):
        if not self.isIn():
            return 0.0
        val = (self.bid/self.max)-1
        if val > 0.0:
            return 0.0
        return val


    def getglobaldrawdown(self):
        return (self.getvalue()/self.maxvalue)-1
    
    def getperformance(self):
        return (self.getvalue()/self.initial)-1

    


    def buy(self):
        if self.isIn():
            return self.nothing()
        self.state = 'in'
        self.amount = self.currentval /self.ask
        self.currentval=0.0
        self.buyprice = self.ask
        self.max=self.ask
        #print('buy',self.state,self.getvalue(),self.getreward())
        
    def sell(self):
        if not self.isIn():
            return self.nothing()
        self.state = 'out'
        self.currentval = self.amount* self.bid
        self.amount = 0.0
        #self.max =0
        #print('sell',self.state,self.getvalue(),self.getreward())
    def nothing(self):
        pass
        #print('nothing',self.state,self.getvalue(),self.getreward())
        

        
        
        
class BCTrade(gym.Env):
    metadata = {"render.modes": ["human","ascii"]}
    def __init__(self,df,singlerun=True,spreadfactor=1.0):
        
        self.df = df
        self.spreadfactor = spreadfactor
        self.singlerun = singlerun
        self.high = [1,0]
        self.low = [0,-1]
        for _ in range(4,len(df.columns)):
            self.high.append(3)
            self.low.append(-3)
        self.action_space = spaces.Discrete(4)
        self.setSpace()
        self.reset()
        pass
    def setSpace(self):
        self.observation_space = spaces.Box(high=np.array(self.high),
                                            low=np.array(self.low), 
                                           dtype=np.float64)
    def setState(self):
        inmarket=0.0
        if self.tc.isIn():
            inmarket=1.0
        statelist = [inmarket,self.tc.getdrawdown()]
        for i in range(4,len(self.df.columns)):
            statelist.append(self.df.iloc[self.row,i])
        self.state= tuple(statelist)
        #print(self.state)
        
    def isdone(self):
        return self.row ==(len(self.df.index)-1) 
    
    def getprices(self):
        bid = self.df.iloc[self.row,1]
        ask = self.df.iloc[self.row,2]  
        price = (bid+ask)/2.0
        diff = price-ask

        return (price+diff*self.spreadfactor,price-diff*self.spreadfactor)
        
        
    def step(self, action):
        action_names=["buy","hold","sell","nothing"]
        action_name = action_names[action]
        #print (action)
        #prevval=self.tc.getvalue()
        done = self.isdone()
        reward =0
        if action_name not in self.tc.getactions():
            reward -=1
        if not done:
            self.row+=1
            bid,ask = self.getprices()
            #action_name = self.tc.getactions()[action]
            self.tc.act(action_name,bid,ask)
            #print(action_name)
            reward += self.tc.getreward()
            
            if action_name == 'sell' and self.singlerun:
                pass
                done = True 
        self.setState()
        #reward = self.tc.getreward()
        #reward = self.tc.getvalue()-prevval
        #if reward > 0 and done and self.stepnum > 10:
        #    reward +=1
        if self.tc.getdrawdown() < -0.1:
            reward = -1000
            done = True
        self.stepnum+=1
        return np.array(self.state),reward, done, {}
    def reset(self):
        self.row =random.randrange(len(self.df.index))
        _, self.initialprice = self.getprices()
        self.tc =tradeclass()
        self.setState()
        self.stepnum=0
        return np.array(self.state)
    def initialize(self):
        self.row =0
        self.tc =tradeclass()
        self.setState()
        self.stepnum=0
        return np.array(self.state)
    def render(self, mode='human'):
        if mode=='ascii':
             return 'Portfolio Value'+str(self.tc.getvalue())
        print(self.tc.getvalue())
