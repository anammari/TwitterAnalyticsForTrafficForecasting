# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 22:13:08 2016

@author: Ahmad
"""
try:
   import cPickle as pickle
except:
   import pickle
import pandas as pd
import numpy as np

def load_df(df_filename):
    f = open(df_filename, 'rb')
    df = pickle.load(f)
    f.close()
    return df

df = load_df("relevance_values_df_Apr_ratio_good.pickle")
df.head()

'Negative' in df.columns


