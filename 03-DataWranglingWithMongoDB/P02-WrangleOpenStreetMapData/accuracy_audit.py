from utils import findTagInChildren


"""
Data accuracy audit object in a form of a callback for SAX content handler.

This audit class checks compliance to gold standard. The nonconformities can be requested after parsing.
This audit is only applied to elements which has a tag element child with k = population.
"""
class DataAccuracyAudit(object):
    """
    Constructor.
    
    The specified standard has the following structure:
    
    - key: town name
    - value: dictionnary with the following keys / values. Each value is a tuple of conversion function and expected 
    value:
        - *population*: population as measured during the last census
        - *source:population*: source of last census
        - *ref:INSEE*: identifier of town in gold standard (INSEE)
        
    - standard: gold standard dictionnary
    """
    def __init__(self, standard):
        self._standard = standard
        self._nonconformities = [ ]
    
    """
    Method called back when a start event is encountered.
    
    - stack: stack of elements being read
    - locator: locator object from SAX parser
    """
    def startEventCallback(self, stack, locator):
        pass
    
    """
    Method called back when an end event is encountered.
    
    - name: element name
    - children: element children
    - locator: locator object from SAX parser
    """
    def endEventCallback(self, name, children, locator):
        #Find item with a tag child having population as k value and compare to standard
        match = findTagInChildren(children, 'population')
        if match is not None:
            town = findTagInChildren(children, 'name:fr')
            try:
                standard = self._standard[town]
            except KeyError:
                message = "Town {} has been found and not in standard. Accuracy cannot be assessed.".format(town)
                self._nonconformities.append(('Accuracy', message))
            else:
                for key, value in standard.iteritems():
                    value_in_dataset = findTagInChildren(children, key)
                    if value_in_dataset is not None:
                        dataset_value = value[0](value_in_dataset)
                        if dataset_value != value[1]:
                            message = '"{}" value provided for "{}" of {} is inaccurate. '\
                                    'Expected value is "{}".'.format(dataset_value, key, town, value[1])
                            self._nonconformities.append(('Accuracy', message))
                    else:
                        message = 'No value provided for "{}" of {} is inaccurate. '\
                                    'Expected value is "{}".'.format(key, town, value[1])
        
    """
    Return nonconformities.
    
    A list of tuple is returned:
    - type of audit
    - nonconformity description
    """
    def getNonconformities(self):
        return self._nonconformities[:]