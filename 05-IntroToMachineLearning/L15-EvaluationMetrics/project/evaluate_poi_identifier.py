#!/usr/bin/python


"""
    Starter code for the validation mini-project.
    The first step toward building your POI identifier!

    Start by loading/formatting the data

    After that, it's not our code anymore--it's yours!
"""

import pickle
from feature_format import featureFormat, targetFeatureSplit

data_dict = pickle.load(open("../../L10-FeatureScaling/project/dataset/final_project_dataset.pkl", "r") )

### first element is our labels, any added elements are predictor
### features. Keep this the same for the mini-project, but you'll
### have a different feature list when you do the final project.
features_list = ["poi", "salary"]

data = featureFormat(data_dict, features_list)
labels, features = targetFeatureSplit(data)



### it's all yours from here forward!  

from sklearn import tree

#Training with all data

features_train = features_test = features
labels_train = labels_test = labels

clf = tree.DecisionTreeClassifier()
clf.fit(features_train, labels_train)

from sklearn.metrics import accuracy_score
y_pred = clf.predict(features_test)
y_true = labels_test
score = accuracy_score(y_true, y_pred)
print "Accuracy score: ", score

#Spliting training and testing

from sklearn.cross_validation import train_test_split

features_train, features_test, labels_train, labels_test = train_test_split(
        features, labels, test_size=0.3, random_state=42)
        
clf.fit(features_train, labels_train)
y_pred = clf.predict(features_test)
y_true = labels_test
score = accuracy_score(y_true, y_pred)
print "Accuracy score: ", score

#Evaluation metrics

print "Number of POI's in testing set: ", labels_test.count(1)
print "Total number of person in testing set: ", len(labels_test)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

print classification_report(y_true, y_pred, labels=[0, 1])
print confusion_matrix(y_true, y_pred)

predictions = [0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1]
true_labels = [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0]

print classification_report(true_labels, predictions, labels=[0, 1])
print confusion_matrix(true_labels, predictions)



