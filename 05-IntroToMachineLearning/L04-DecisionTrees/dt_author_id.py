#!/usr/bin/python

""" 
    This is the code to accompany the Lesson 3 (decision tree) mini-project.

    Use a Decision Tree to identify emails from the Enron corpus by author:    
    Sara has label 0
    Chris has label 1
"""
    
import sys
from time import time
from email_preprocess import preprocess


### features_train and features_test are the features for the training
### and testing datasets, respectively
### labels_train and labels_test are the corresponding item labels
features_train, features_test, labels_train, labels_test = preprocess()




#########################################################
### your code goes here ###
print "Number of features: ", features_train.shape[1]

from sklearn import tree
#default classifier (without argument takes 44.5s to fit, 
#0.048s to predict with an accuracy of 0.991
#clf = tree.DecisionTreeClassifier()
#With min_samples_split set to 40, fitting and predicting times
#are 42.5s and 0.062. Accuracy is 0.977
clf = tree.DecisionTreeClassifier(min_samples_split=40)
t0 = time()
clf.fit(features_train, labels_train)
print "training time:", round(time()-t0, 3), "s"

from sklearn.metrics import accuracy_score
t0 = time()
y_pred = clf.predict(features_test)
print "predicting time:", round(time()-t0, 3), "s"
y_true = labels_test
score = accuracy_score(y_true, y_pred)
print "Accuracy score: ", score


#########################################################


