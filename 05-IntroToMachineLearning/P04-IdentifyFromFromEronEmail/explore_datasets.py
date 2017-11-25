"""
Exploration of datasets.
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


sns.set_style('whitegrid')
sns.despine()


def convertProjectDictToDataFrame(data_dict):
    """
    Convert project data dictionnary into a pandas dataframe.
    
    - data_dict: project data dictionary
    - returns: pandas data frame
    """
    #Create an intermediate dictionnary that will be converted to data frame
    tmp = { }
    for name, info in data_dict.iteritems():
        names = tmp.setdefault('names', [])
        names.append(name)
        for key, value in info.iteritems():
            series = tmp.setdefault(key, [])            
            series.append(value)
     
    #Create data frame from dictionnary
    df = pd.DataFrame.from_dict(tmp)
    df = df.set_index('names')
    return df
    

def convert_to_numeric(value):
    """
    Convert provided value to a numeric value.
    If not possible, the value is left unchanged.
    
    - value: value to be converted
    - return: converted value
    """
    if value == 'NaN':
        return np.nan
    elif value is False:
        return False
    elif value is True:
        return True
    else:
        try:
            return float(value)
        except ValueError:
            return value


def scale(series):
    """
    Scale specified series in the range [0-1]
    
    - series: series to be scaled
    - return: scaled series
    """
    #Skip if name or poi
    if series.name in ['name', 'poi']:
        return series
    #Get min and max values:
    try:
        minvalue = series.min()
        maxvalue = series.max()
        return (series - minvalue)/(maxvalue - minvalue)
    except TypeError:
        return series
        
        
def plot_distribution(data):
    """
    Plot distribution of features in given data frame.
    
    - data: data frame to be visualized
    """
    figure = plt.figure(figsize=(12, 8))
    ax = figure.add_subplot(111)
    plt.setp(ax.get_yticklabels(), fontsize=14)
    plt.setp(ax.get_xticklabels(), fontsize=14)
    ax = sns.swarmplot(y="variable", x="value", hue="poi", data=data, dodge=True, orient='h', ax=ax)
    texts = ax.set(ylabel='Financial features', xlabel='Amount (min/max scaled)', title='Distribution of financial features')
    texts[0].set_fontsize(16)
    texts[1].set_fontsize(16)
    texts[2].set_fontsize(20)
    
    
def plot_email_data(data):
    """
    Plot distribution of email features in given data frame.
    
    - data: data frame to be visualized
    """
    email_data_poi = data[data["poi"] == True]
    email_data_nonpoi = data[data["poi"] == False]
    figure = plt.figure(figsize=(12,6))
    ax = figure.add_subplot(111)
    ax.scatter(x=email_data_nonpoi["from_poi"], y=email_data_nonpoi["to_poi"], label="non-POI", s=100)
    ax.scatter(x=email_data_poi["from_poi"], y=email_data_poi["to_poi"], label="POI", s=100)
    ax.legend()
    texts = ax.set(xlabel='Emails from POI\'s', ylabel='Emails to POI\'s', title='Fraction of emails exchanged with POI\'s')
    texts[0].set_fontsize(16)
    texts[1].set_fontsize(16)
    texts[2].set_fontsize(20)
    ymin = email_data_poi["to_poi"].min()
    xmin = email_data_poi["from_poi"].min()
    ymax = data["to_poi"].max()
    xmax = data["from_poi"].max()
    ax.hlines(y=ymin, xmin=xmin, xmax=xmax, linestyle='dashed')
    ax.vlines(x=xmin, ymin=ymin, ymax=ymax, linestyle='dashed')


def plot_classes(data):
    """
    Plot a pie with classes.
    
    - data: data frame to be visualized
    - returns: a dataframe grouped by poi/non-poi
    """
    grouped = data.groupby("poi", as_index=True).count()
    figure = plt.figure(figsize=(12, 6))
    ax = figure.add_subplot(111)
    ax.pie(grouped["name"], labels=["non-POI", "POI"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title("Proportion of persons of interest in dataset", fontsize=20)
    legend = ax.legend() 
    return grouped  


def plot_select(data):
    """
    Plot a comparison of selection algorithms.
    
    - data: data frame with selection algorithms results
    """
    figure = plt.figure(figsize=(14, 6))
    ax = figure.add_subplot(111)
    sns.barplot(x="param_select__n_features", y=("mean_test_f1", "max"), hue="select", data=data, ax=ax)
    legend = ax.legend()
    texts = ax.set(ylabel='Max F1 score\n(higher is better)', xlabel='Number of features', title='Performance of feature selection algorithms')
    texts[0].set_fontsize(16)
    texts[1].set_fontsize(16)
    texts[2].set_fontsize(24)
    
    
def plot_classify(data):
    """
    Plot a comparison of classification algorithms.
    
    - data: data frame with classification algorithms results
    """
    figure = plt.figure(figsize=(14, 18))
    figure.suptitle('Performance of classification algorithms', fontsize=24)
    for conf in [({'loc': (1, 0)}, "mean_test_f1", "F1 score\n(higher is better)", "Comparison of F1 scores"),
                 ({'loc': (0, 0)}, "mean_test_precision", "Precision\n(higher is better)", "Comparision of precision score"),
                 ({'loc': (0, 1)}, "mean_test_recall", "Recall\n(higher is better)", "Comparision of recall score"),
                 ({'loc': (1, 1)}, "mean_test_accuracy", "Accuracy\n(higher is better)", "Comparision of accuracy score"),
                 ({'loc': (2, 0), 'colspan': 3}, "mean_fit_time", "Fit time (s)\n(lower is better)", "Comparision of fit time")]:
        ax = plt.subplot2grid(shape=(3, 2), **conf[0])
        if conf[1] == "mean_fit_time":
            ax.set_yscale("log", nonposy='clip')
        sns.boxplot(x="classify", y=conf[1], data=data, ax=ax)
        texts = ax.set(ylabel=conf[2], xlabel="", title=conf[3])
        texts[0].set_fontsize(16)
        texts[1].set_fontsize(16)
        texts[2].set_fontsize(20)
    figure.subplots_adjust(top=0.92)    


def plot_validate(data):
    """
    Plot a comparison of validation algorithms.
    
    - data: data frame with classification algorithms results
    """
    figure = plt.figure(figsize=(14, 6))
    ax = figure.add_subplot(111)
    sns.boxplot(x="validate", y="mean_test_f1", hue='classify', data=data, ax=ax)
    legend = ax.legend()
    texts = ax.set(ylabel='Mean F1 score\n(higher is better)', xlabel='Cross-validation', title='Performance of validation algorithms')
    texts[0].set_fontsize(16)
    texts[1].set_fontsize(16)
    texts[2].set_fontsize(24)


class FillNaNWithMedianValues(object):
    """
    Objects of this class may be used as argument of pandas DataFrame.apply.
    This function replace NaN values with median values of the relevant group (poi / non-poi).
    """
    def __init__(self, poi, features):
        """
        Constructor
        
        - poi: series with poi / non-poi group
        - features: list of features to be processed
        """
        self._poi = poi
        self._non_poi = ~poi
        self._features = features
        
    def __call__(self, series):
        """
        If series is a feature, the NaN values are placed with median values.
        
        - series: series to be modified
        - return: modified series
        """
        if series.name in self._features:
            #Replace with median values
            series = series.copy() #This is to prevent bug with views or copy, we make an explicit copy
            series.loc[self._poi & series.isnull()] = series[self._poi].median()
            series.loc[self._non_poi & series.isnull()] = series[self._non_poi].median()
            return series
        else:
            #Do not apply any change to non-feature columns
            return series
            

