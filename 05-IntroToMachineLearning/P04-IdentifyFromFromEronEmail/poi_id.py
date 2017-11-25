#!/usr/bin/python
# -*- coding: utf-8 -*-

from tester import dump_classifier_and_data
from tester import dump_classifier_and_data

"""
import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)
"""

"""
Main script for Identify Fraud from Enron Email project.
Udacity Data Analysis Nanodegree.

This script is based on starter code provided by Udacity for project.

Author: Cédric Campguilhem
Date: November 2017
"""

from sklearn.feature_selection import RFE
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.cross_validation import train_test_split
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold


from download_datasets import downloadDatasets, loadProjectData
from explore_datasets import *


def main():
    """
    Main function.

    Executes in sequence all functions required to generate results for project 
    submission:

    - my_classifier.pkl
    - my_dataset.pkl
    - my_feature_list.pkl
    """
    #First download all datasets required for analysis
    downloadDatasets()
    
    #Load project data
    data_dict = loadProjectData()
    
    #Convert to a dataframe
    df = convertProjectDictToDataFrame(data_dict)
    
    #Get financial data
    financial_data = df.loc[:, ['salary', 'bonus', 'long_term_incentive', 'deferral_payments', 'other', 'expenses', 
                     'exercised_stock_options', 'restricted_stock', 'poi']]
    financial_data.reset_index(inplace=True)
    financial_data.rename(columns={'names': 'name'}, inplace=True)
    financial_data = financial_data.applymap(convert_to_numeric)
    financial_data = financial_data.apply(scale)
    financial_data = financial_data[financial_data['name'] != "TOTAL"]
    
    #Get email data
    email_data = df.loc[:, ["email_address", "from_messages", "from_poi_to_this_person", "from_this_person_to_poi", "to_messages", 
                 "poi"]]
    email_data.reset_index(inplace=True)
    email_data.rename(columns={'names': 'name'}, inplace=True)
    email_data = email_data[email_data['name'] != "TOTAL"]
    email_data = email_data.applymap(convert_to_numeric)    
    email_data = email_data.assign(**{'from_poi': email_data['from_poi_to_this_person']/email_data['to_messages'],
                                  'to_poi': email_data['from_this_person_to_poi']/email_data['from_messages']})

    #Combine datasets
    email_data_condensed = email_data[["name", "from_poi", "to_poi", "from_poi_to_this_person", "from_this_person_to_poi"]]
    dataset = financial_data.merge(email_data_condensed, left_on="name", right_on="name")
    
    #List features
    features = [column for column in dataset.columns if column not in ["name", "poi"]]
    
    #Final clean
    dataset_cleaned = dataset.apply(FillNaNWithMedianValues(dataset.loc[:, "poi"], features))
    dataset_cleaned = dataset_cleaned.apply(scale)
    
    #Machine learning
    slt = RFE(estimator=DecisionTreeClassifier(), n_features_to_select=8)
    clf = AdaBoostClassifier(DecisionTreeClassifier(max_depth=2), n_estimators=25)
    cv = StratifiedKFold(n_splits=8, shuffle=True, random_state=1234)
    
    pipeline = Pipeline([('select', slt), ('classify', clf)])
    grid = GridSearchCV(pipeline, {}, cv=cv, scoring=['accuracy', 'f1', 'precision', 'recall'], refit='f1', n_jobs=6, verbose=0)
    grid.fit(dataset_cleaned[features], dataset_cleaned['poi'])
    
    print grid.best_score_
    clf = grid.best_estimator_.named_steps["classify"]
    
    features_list = ['poi']
    for i, mask in enumerate(grid.best_estimator_.named_steps["select"].support_):
        if mask:
            features_list.append(features[i])
    print features_list
    
    #Convert dataset back to a dictionary
    my_dataset = { }
    for row in dataset_cleaned.iterrows():
        series = row[1]
        name = series.loc['name']
        data = { }
        for key in series.index:
            if key != "name":
                data[key] = series.loc[key]
        my_dataset[name] = data
    
    #Save for tester.py
    dump_classifier_and_data(clf, my_dataset, features_list)
    
    
    
if __name__ == '__main__':
    main()
    


