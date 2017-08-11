import datetime
import os

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


#Path of datasets
DATASET_PATH = "./dataset/core"


"""
Functions used in the baseball notebook
"""

def rename_countries(country):
    """
    Rename country.
    
    Removes abreviations in country names.
    
    - country: country to be renamed
    + return: renamed country
    """
    if country == "CAN":
        return "Canada"
    elif country == "D.R.":
        return "Dominican Republic"
    elif country == "P.R.":
        return "Puerto Rico"
    elif country == "V.I.":
        return "British Virgin Islands"
    else:
        return country
        

def convert_units(column):
    """
    Convert units in given column.
    
    Inches are converted into centimeters and pounds are converted into 
    kilograms.
    
    - column: series to be converted
    - return: series with converted units
    """
    if column.name == "weight":
        return column *0.453592
    elif column.name == "height":
        return column * 2.54
    else:
        return column
        
        
def convert_dates(column):
    """
    Convert dates from string to date time objects.
    
    The dates format are YYYY-MM-DD in the input data.
    
    - column: series to be converted
    - return: series with datetime data type
    """
    def _convert_date(date):
        try:
            return datetime.datetime.strptime(date, "%Y-%m-%d")
        except TypeError:
            return date
    
    if column.name in ["debut", "finalGame"]:
        return column.apply(_convert_date)
    else:
        return column


def read_master():
    """
    Read the master dataset and clean it.
    
    - return: master data frame
    """
    return clean_master(pd.read_csv(os.path.join(DATASET_PATH, "Master.csv")))
    

def clean_master(df):
    """
    Clean the master data frame
    
    Drop unused columns, drop any row with a null player ID and uses playerID
    as index. Convert height and weight units, create a new column with birth 
    date as datetime object and convert debut and finalGame dates into datetime
    objects.
    
    - df: master data frame
    - return: cleaned data frame
    """
    #Drop rows where player ID is null
    df.dropna(axis=0, subset=['playerID'], inplace=True)

    #Set player ID as index    
    df.set_index("playerID", inplace=True)
    
    #Create a datetime object for birth date (not sure if this can be vectorized)
    birth_year = df["birthYear"]
    birth_month = df["birthMonth"]
    birth_day = df["birthDay"]
    birth_date = [ ]
    for (year, month, day) in zip(birth_year, birth_month, birth_day):
        try:
            birth_date.append(datetime.datetime(int(year), int(month), int(day)))
        except ValueError:
            birth_date.append(None)
    df = df.assign(birthDate=birth_date)
    
    #Drop unused columns
    df.drop(["birthMonth", "birthDay", "birthState", "birthCity", "deathYear", 
             "deathMonth", "deathDay", "deathCountry", "deathCity", 
             "deathState", "bats", "throws", "bbrefID", "retroID"], 
             axis=1, inplace=True)
 
    #Rename countries (element-wise operation)
    df = df.applymap(rename_countries)
    
    #Convert units (column-wise operation)
    df = df.apply(convert_units)
    
    #Convert dates
    df = df.apply(convert_dates)

    return df


def convert_bool(column):
    """
    Convert text into bool in given column.
    
    - column: series to be converted
    - return: converted column
    """
    def _convert_bool(text):
        if text in ["Y", "y", "1"]:
            return True
        else:
            return False
    
    if column.name in ["active"]:
        return column.apply(_convert_bool)
    else:
        return column


def read_teams():
    """
    Read the teams dataset and clean it.
    
    - return: teams data frame
    """
    df = pd.read_csv(os.path.join(DATASET_PATH, "Teams.csv"))
    return clean_teams(df)

    
def clean_teams(df):
    """
    Clean the teams data frame.
    
    Unused columns are dropped. Data frame is merged with the one from 
    franchises. Only National League and American League are kept in data 
    frame.
    
    - df: teams data frame
    - df: cleaned data frame
    """
    #Merge with teams franchises
    franchise_df = pd.read_csv(os.path.join(DATASET_PATH, "TeamsFranchises.csv"))
    df = pd.merge(left=df, right=franchise_df, on=['franchID'], suffixes=('_l', '_r'))
    
    #Drop unused columns
    df.drop(["teamIDBR", "teamIDlahman45", "teamIDretro", "franchID", 
             "NAassoc"], inplace=True, axis=1)
            
    #Convert active column to bool
    df = df.apply(convert_bool)
    
    #Only keep National League and American League teams:
    df = df[(df["lgID"] == "NL") | (df["lgID"] == "AL")]
    
    return df


def scatter_plot(x, y, size=None, xlabel=None, ylabel=None, figsize=(12, 9)):
    """
    Create a scatter plot.
    
    - x: array of x positions of markers
    - y: array of y positions of markers
    - size: scalar/array of size of markers
    - xlabel: label of x axis
    - ylabel: label of y axis
    - figsize: (width, height) of figure
    """
    figure = plt.figure(figsize=figsize)
    axes = figure.add_subplot(111)
    axes.scatter(x, y, size)
    if xlabel:
        axes.set_xlabel(xlabel)
    if ylabel:
        axes.set_ylabel(ylabel)
    
        
def hist_plot(x, bins=None, xlabel=None, ylabel=None, figsize=(12, 9)):
    """
    Create a histogram plot.
    
    - x: array to be plotted
    - bins: configuration of bins (see numpy.histogram documentation)
    - xlabel: label of x axis
    - ylabel: label of y axis
    - figsize: (width, height) of figure
    """
    figure = plt.figure(figsize=figsize)
    axes = figure.add_subplot(111)
    hist, bin_edges, patches = axes.hist(x, bins=bins)
    axes.set_xticks(bin_edges)
    if xlabel:
        axes.set_xlabel(xlabel)
    if ylabel:
        axes.set_ylabel(ylabel)
        

def line_plot(xs, ys, labels=None, xlabel=None, ylabel=None, 
              title=None, figsize=(12,9)):
    """
    Create a line plot.
    
    - xs: sequence of x-arrays
    - ys: sequence of y-arrays
    - labels: labels of lines
    - xlabel: label of x axis
    - ylabel: label of y axis
    - title: plot title
    - figsize: (width, height) of figure
    """
    figure = plt.figure(figsize=figsize)
    axes = figure.add_subplot(111)
    for i, (x, y) in enumerate(zip(xs, ys)):
        if labels:
            axes.plot(x, y, label=labels[i])
        else:
            axes.plot(x, y)
    axes.legend()
    if xlabel:
        axes.set_xlabel(xlabel)
    if ylabel:
        axes.set_ylabel(ylabel)
    if title:
        axes.set_title(title)

