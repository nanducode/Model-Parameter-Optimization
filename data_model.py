#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 22:57:47 2018

@author: akommaraju
"""

import glob
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error,mean_absolute_error, r2_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report

import seaborn as sns
def plot_data():
    """ Read data into pandas dataframes and visualize """
    df=pd.read_csv("out.csv")
    df['KH'].replace({'/lus/snx11254/akommaraju/Ocean/Model-Parameter-Optimization/data/':''},inplace=True,regex=True)
    df1=df.apply(pd.to_numeric)
    df1=df1.rename(columns={'Unnamed: 0': 'index'})
    return df1
def fit_model(dataframe):
    """Model fitting routines. Explore different techniques"""
    Y=dataframe['KH']
    X=dataframe.drop(['KH','index'],axis=1)
    X=PCA(n_components=10).fit_transform(X)
    (pd.DataFrame(X)).to_csv("X.csv")
    (pd.DataFrame(Y)).to_csv("Y.csv")
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)
    nn = MLPRegressor(hidden_layer_sizes=(100,),  activation='relu', solver='adam',max_iter=5000)
    nn.fit(x_train, y_train)
    y_pred=nn.predict(x_test)
    (pd.DataFrame(y_pred)).to_csv("pred_nn.csv")
    (pd.DataFrame(y_test)).to_csv("truth_nn.csv")
    print("Mean absolute error: %.2f" % mean_absolute_error(y_test, y_pred))
    
def read_data(files):
    frames=[]
    col_names=[]
    for l in (['layer1','layer2']):
            for f in (range(1,6)):
                for p in (range(1,1761)):
                    feature=l+"_feature"+str(f)+"_point"+str(p)
                    col_names.append(feature)
    count=0
    for file in files:
        print(file)
        count+=1
        inames=str(count)
        df=pd.read_csv(file,header=0)

        print(df.shape[0]*df.shape[1])
        df=df.values.reshape(1,(df.shape[0]*df.shape[1]))
        pdf=pd.DataFrame(df,index=[inames],columns=col_names)  
        khval=str(file).split("_")
        pdf['KH']=khval[0]
        frames.append(pdf)
    
    fdf=pd.concat(frames)
    
    fdf.to_csv("out.csv",float_format='%.3f')
        #np.savetxt("out.csv",df,delimiter=',')
    
    
    
if __name__== "__main__":
    os.chdir("/lus/snx11254/akommaraju/Ocean/Model-Parameter-Optimization")
    files=glob.glob('/lus/snx11254/akommaraju/Ocean/Model-Parameter-Optimization/data/*.csv')
    #print(files)
    df=plot_data()
    fit_model(df)
    #read_data(files)
