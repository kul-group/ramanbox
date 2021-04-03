import os
import git
import copy
root_dir = git.Repo('.', search_parent_directories=True).working_tree_dir  # get git root dir 
os.chdir(root_dir)  # set cwd to root_dir

import pandas as pd 
import numpy as np
from ramanbox.raman.constants import Label
from fit_visualization import FittingVisualizer

def make_df(sample_list):
    df = pd.DataFrame()
    for sample in sample_list:
        df = df.append(sample.to_pandas(), ignore_index=True)

    return df

def normalize_X(X):
    X = copy.copy(X)
    for i in range(0, X.shape[0]):
        X[i, :] = (X[i, :] - np.mean(X[i, :]))/np.std(X[i, :])
    return X

def make_Xy(df, remove_maybe_uncat=True):
    if remove_maybe_uncat:
        df = df[(df['label'] == Label.GOOD ) | (df['label'] == Label.BAD)]        
    X = np.stack(df['spectrum'].to_numpy())
    Y_obj = df['label'].to_numpy()
    Y = np.array([y.value for y in Y_obj])
    return X, Y


class ModelFitting:
    def __init__(self, model_class, name, X_train, Y_train, X_val, Y_val, *args, **kwargs):
        self.model = model_class()
        self.name = name
        self.X_train = X_train
        self.Y_train = Y_train 
        self.X_val = X_val
        self.Y_val = Y_val 
        self.Y_val_pred = None
        self.Y_val_scores = None
        self.val_acc_score = None
        self.y_probs_cv = None
        self.result_cv = None
        
    def run(self):
        self.fit()
        self.cv_stats()
        self.val_stats()
    
    def visualize(self):
        if self.y_probs_cv is None:
            self.run()
        self.fit_vis()

    def fit(self):
        self.model.fit(self.X_train, self.Y_train)
        
    def cv_stats(self, cv=3, method="predict_proba", scoring="accuracy"):
        assert (self.X_train is not None and self.Y_train is not None), 'fit before doing CV'
        self.y_probs_cv = cross_val_predict(self.model ,self.X_train, self.Y_train, cv=cv, method=method)
        self.result_cv = cross_val_score(self.model, self.X_train, self.Y_train, cv=cv, scoring=scoring)
    
    def val_stats(self):
        self.Y_val_pred = self.model.predict(self.X_val)
        scores_2d = self.model.predict_proba(self.X_val)
        self.Y_val_scores = scores_2d[:, 1]  # only pick positive class probs 
        self.val_acc_score = accuracy_score(self.Y_val, self.Y_val_pred)
    
    def fit_vis(self):
        self.fit_vis = FittingVisualizer(self.X_val, self.Y_val, self.Y_val_pred, y_scores=self.Y_val_scores)
        self.fit_vis.show_all()