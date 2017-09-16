#!/usr/bin/python

""" 
    Starter code for exploring the Enron dataset (emails + finances);
    loads up the dataset (pickled dict of dicts).

    The dataset has the form:
    enron_data["LASTNAME FIRSTNAME MIDDLEINITIAL"] = { features_dict }

    {features_dict} is a dictionary of features associated with that person.
    You should explore features_dict as part of the mini-project,
    but here's an example to get you started:

    enron_data["SKILLING JEFFREY K"]["bonus"] = 5600000
    
"""

import pickle
from pprint import pprint

enron_data = pickle.load(open("./dataset/final_project_dataset.pkl", "r"))

print len(enron_data)

pprint(enron_data["SKILLING JEFFREY K"])

count = 0
for name, features in enron_data.iteritems():
    if features["poi"]:
        count += 1
        
print "Number of persons of interest: {}".format(count)

#Read poi names files
names = [ ]
with open("./dataset/poi_names.txt", "r") as fobj:
    for line in fobj:
        if line.startswith('(y)') or line.startswith('(n)'):
            fields = line[4:].split(",")
            names.append(fields)
print len(names)

pprint(enron_data["PRENTICE JAMES"])
print enron_data["PRENTICE JAMES"]["total_stock_value"]

pprint(enron_data["COLWELL WESLEY"])
print enron_data["COLWELL WESLEY"]["from_this_person_to_poi"]

pprint(enron_data["SKILLING JEFFREY K"])
print enron_data["SKILLING JEFFREY K"]["exercised_stock_options"]

poi = [ ]
for lastname in ["SKILLING", "LAY", "FASTOW"]:
    for name, features in enron_data.iteritems():
        if lastname in name:
            d = {"name": name}
            d.update(features)
            poi.append(d)
            break
poi.sort(key=lambda x: x["total_payments"], reverse=True)
pprint(poi)

count = 0
for name, features in enron_data.iteritems():
    if features["email_address"] != 'NaN':
        count += 1
print "Number of valid email addresses: ", count
count = 0
for name, features in enron_data.iteritems():
    if features["salary"] != 'NaN':
        count += 1
print "Number of valid salaries: ", count

#Convert to array (list of list)
from feature_format import featureFormat, targetFeatureSplit
feature_list = ["poi", "salary", "bonus", "total_payments"]
enron_array = featureFormat(enron_data, feature_list, 
        remove_all_zeroes=False, remove_any_zeroes=False)
labels, features = targetFeatureSplit(enron_array)
print len(features)
print len(labels)
print "Same size as original dataset"

count = 0
for row in features:
    if row[2] > 0.: #Total payments
        pass
    else:
        count += 1
print "{} persons with no 'total_payments': this is {:.2f}%".format(
        count, (100. * count) / len(features))
        
count = 0
count_poi = 0
for label, row in zip(labels, features):
    if label < 1.: #this is not a POI
        continue
    else:
        count_poi += 1
    if row[2] > 0.: #Total payments
        pass
    else:
        count += 1
print "{} poi's with no 'total_payments': this is {:.2f}%".format(
        count, (100. * count) / count_poi)






