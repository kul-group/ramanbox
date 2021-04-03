# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 08:26:33 2020

@author: dexte
"""

# the purpose of this script is to create an object that can aid in visualization
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_curve, \
    precision_recall_curve, roc_auc_score
import seaborn as sn
import pandas as pd
import os 
sn.reset_orig()



class FittingVisualizer():

    def __init__(self, X_true, y_true, y_pred, y_scores=None, save_data=False):
        self.X_true = X_true
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_scores = y_scores
        self.result_strs = [['True Negative', 'False Positive'], ['False Negative', 'True Positive']]
        self.plot_title = True
        self.scale = 0.75
        self.ROC_curve = None
        self.PR_curve = None
        self.save_data = save_data
        directory = '../xgb_results_out_of_sample/' # fix this after Friday 
        
        if self.save_data:
            def save_data_fun(filename):
                plt.savefig(os.path.join(directory, filename))
        else:
            def save_data_fun(filename):
                pass
            
        self.save_data_fun = save_data_fun
                

    def plot_data(self, nrows=4, ncols=5):

        # print("X first 20 @ point 1: ", X_first20[:,1],"\ny first 20: ", y_first20)
        s = self.scale
        if (len(self.y_true) < (nrows * ncols)):
            nrows = int(len(self.y_true) / ncols - 1)
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20 * s, 16 * s), dpi=72)
        result_strs = self.result_strs
        result_colors = [['blue', 'red'], ['orangered', 'green']]
        indices = np.random.RandomState(42).choice(len(self.y_true), nrows * ncols, replace=False)
        # range(0,nrows*ncols)
        for i, a in zip(indices, ax.flatten()):
            true_class = "GOOD" if self.y_true[i] else "BAD"
            predict_class = "GOOD" if self.y_pred[i] else "BAD"

            result_str = result_strs[int(self.y_true[i])][
                             int(self.y_pred[i])] + "\n True: " + true_class + "\n Prediction: " + predict_class
            result_color = result_colors[int(self.y_true[i])][int(self.y_pred[i])]
            title = "Index: " + str(i)
            a.plot(self.X_true[i])  # ,marker = ms(marker='_'))
            a.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelright=False,
                          labelleft=False, labelbottom=False)  # removes tick marks
            a.set_title(title)
            a.annotate(result_str, xy=(0.5, 0.5), xycoords="axes fraction", size=16, color=result_color,
                       horizontalalignment='center', weight='heavy')
            a.set_ylim([-5, 25])
        self.save_data_fun('good_bad_samples.svg')

    def confusion_matrix(self):
        s = self.scale
        plt.figure(2, figsize=(5 * s+2, 5 * s+2))
        result = confusion_matrix(self.y_true, self.y_pred)
        df_cm = pd.DataFrame(result, ["Bad", "Good"], ["Bad", "Good"], )
        sn.set(font_scale=2)  # for label size
        sn.heatmap(df_cm, annot=True, annot_kws={"size": 30}, fmt='g', cbar=False, cmap='Blues')  # font size
        plt.xlabel("Algorithm Classification")
        plt.ylabel("Human Classification")
        self.save_data_fun('confusion_matrix.svg')
        plt.show()
        sn.reset_orig()
        # plt.imshow(result)

    def show_stats(self):
        stats_dict = {}
        stats_dict['Accuracy'] = [accuracy_score(self.y_true, self.y_pred)]
        stats_dict['Precision'] = [precision_score(self.y_true, self.y_pred)]
        stats_dict['Recall'] = [recall_score(self.y_true, self.y_pred)]
        stats_dict['F1'] = [f1_score(self.y_true, self.y_pred)]
        if self.y_scores is not None:
            stats_dict['AUC_ROC'] = [roc_auc_score(self.y_true, self.y_scores)]
        else:
            stats_dict['AUC_ROC'] = 0 
            
        stats_df = pd.DataFrame.from_dict(stats_dict)
        print(stats_df)
    
    def get_stats_df(self):
        stats_dict = {}
        stats_dict['Accuracy'] = [accuracy_score(self.y_true, self.y_pred)]
        stats_dict['Precision'] = [precision_score(self.y_true, self.y_pred)]
        stats_dict['Recall'] = [recall_score(self.y_true, self.y_pred)]
        stats_dict['F1'] = [f1_score(self.y_true, self.y_pred)]
        
        if self.y_scores is not None:
            stats_dict['AUC_ROC'] = [roc_auc_score(self.y_true, self.y_scores)]
        else:
            stats_dict['AUC_ROC'] = 0    
            
        stats_df = pd.DataFrame.from_dict(stats_dict)
        return stats_df

    def plot_curves(self):
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
        ax1 = axes[0]
        ax2 = axes[1]

        # ROC Curve
        fpr, tpr, thresholds = self.ROC_curve = roc_curve(self.y_true, self.y_scores)

        if (self.plot_title): ax1.set_title("ROC Curve", fontsize=18)
        ax1.plot(fpr, tpr, linewidth=2)
        ax1.plot([0, 1], [0, 1], 'k--')  # dashed diagonal
        ax1.axis([0, 1, 0, 1])  # Not shown in the book
        ax1.set_xlabel('False Positive Rate (Fall-Out)', fontsize=16)  # Not shown
        ax1.set_ylabel('True Positive Rate (Recall)', fontsize=16)  # Not shown

        # Precision Recall Curve
        if (self.plot_title): ax2.set_title("Precision Recall Curve", fontsize=18)
        precisions, recalls, thresholds = self.PR_curve = precision_recall_curve(self.y_true, self.y_scores)
        ax2.plot(thresholds, precisions[:-1], "b--", label=r"$precision = \frac{TP}{TP+FP}$")
        ax2.plot(thresholds, recalls[:-1], "g-", label=r"$recall = \frac{TP}{TP+FN}$")
        ax2.legend(fontsize=16)
        ax2.set_xlabel("Threshold", fontsize=16)
        ax2.set_ylabel("Value", fontsize=16)
        self.save_data_fun('ROC_curves.svg')

        # ax1.axis[]

    def show_all(self):
        self.show_stats()
        self.plot_data()
        self.confusion_matrix()
        self.plot_curves()

