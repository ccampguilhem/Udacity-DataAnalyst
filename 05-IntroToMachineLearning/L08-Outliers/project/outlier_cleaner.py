#!/usr/bin/python

import math


def outlierCleaner(predictions, ages, net_worths):
    """
        Clean away the 10% of points that have the largest
        residual errors (difference between the prediction
        and the actual net worth).

        Return a list of tuples named cleaned_data where 
        each tuple is of the form (age, net_worth, error).
    """
    nb_cleaned = int(math.ceil(len(predictions) * 0.1))
    cleaned_data = []

    #Calculate all residual errors
    for prediction, age, net_worth in zip(predictions, ages, net_worths):
        error = (prediction - net_worth)**2
        cleaned_data.append((age, net_worth, error))
    
    #Sort with highest error first
    cleaned_data.sort(key=lambda x: x[2], reverse=True)
    
    #Remove highest errors:
    cleaned_data = cleaned_data[nb_cleaned:]
    
    return cleaned_data

