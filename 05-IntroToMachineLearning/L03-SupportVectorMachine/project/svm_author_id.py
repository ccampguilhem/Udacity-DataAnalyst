#!/usr/bin/python

""" 
    This is the code to accompany the Lesson 2 (SVM) mini-project.

    Use a SVM to identify emails from the Enron corpus by their authors:    
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

from sklearn.svm import SVC
#clf = SVC(kernel='linear')
clf = SVC(C=10000., kernel='rbf')
t0 = time()
#This is slow with all dataset
#fitting time is 109s and predicting time is 11s
clf.fit(features_train, labels_train)
#With reduced dataset (only one percent), fitting time is 0.061s
#and predicting time is 0.653s
#With rbf kerbel fitting time is 0.069s and predicting time is 0.746s
#With rbf kernel and C=10000 with full dataset fitting time is 72s
#end predicting time is 7.2s.
#clf.fit(features_train[:len(features_train)/100], labels_train[:len(labels_train)/100])
#clf.fit(features_train[:len(features_train)/10], labels_train[:len(labels_train)/10])
print "fitting time:", round(time()-t0, 3), "s"

from sklearn.metrics import accuracy_score
t0 = time()
y_pred = clf.predict(features_test)
print "predicting time:", round(time()-t0, 3), "s"
y_true = labels_test
#Accuracy is 0.984 with full dataset
#Accuracy is 0.884 with 1% dataset
#Accuracy drops to 0.616 with rbf kernel
#Accuracy with rbf kernel and C=10000 with full dataset raises to 0.991
score = accuracy_score(y_true, y_pred)
print "Accuracy score: ", score
#Predicting classes for few items
print y_pred[[10, 26, 50]]
#Number of Chris emails
print y_pred[y_pred ==1].shape[0]


#########################################################


