#!/usr/bin/python

import pickle
import sys
import matplotlib.pyplot
from feature_format import featureFormat, targetFeatureSplit


### read in data dictionary, convert to numpy array
data_dict = pickle.load( open("./dataset/final_project_dataset.pkl", "r") )

#Who is the outlier ?

for key, features in data_dict.iteritems():
    if features["salary"] == 'NaN' or features["bonus"] == 'NaN':
        continue
    if features["salary"] >= 2.5e7 and features["bonus"] > 0.8e8:
        break
        
print key
print data_dict[key]

# Remove outlier
data_dict.pop(key)

# find other outliers (salary over 1 million and bonus over 5 millions
for key, features in data_dict.iteritems():
    if features["salary"] == 'NaN' or features["bonus"] == 'NaN':
        continue
    if features["salary"] >= 1.e6 and features["bonus"] > 5.e6:
        print key

features = ["salary", "bonus"]
data = featureFormat(data_dict, features)


# Plot

for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus)

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.tight_layout(True)
matplotlib.pyplot.show()





