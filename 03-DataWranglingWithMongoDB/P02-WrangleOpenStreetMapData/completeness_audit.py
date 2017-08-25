from utils import *

"""
Data completeness audit object in a form of a callback for SAX content handler.

This audit class checks compliance to gold standard. The nonconformities can be requested after parsing.
This audit is only applied to elements which has a tag element child with k = amenity and v = pharmacy
"""
class DataCompletenessAudit(object):
    """
    Constructor.
    
    The specified standard is a list of tuples:
    - Pharmacy name
    - Adress
            
    - standard: gold standard list
    - warnings: toggle to report warnings
    """
    def __init__(self, standard, warnings=False):
        self._standard = standard
        self._missing = standard[:]
        self._nonconformities = [ ]
        self._warnings = warnings
    
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
        #Find item with a tag child having amenity as k value and pharmacy as v value and compare to standard
        match = findTagInChildren(children, 'amenity', 'pharmacy')
        if match is not None:
            name = findTagInChildren(children, 'name')
            found = False
            for i in xrange(len(self._missing)):
                if compareStrings(self._missing[i][0], name):
                    found = True
                    break
            if found:
                self._missing.pop(i)
            elif self._warnings:
                message = u'Pharmacy "{}" found but not expected.'.format(name)
                self._nonconformities.append(('Warning', message))

    """
    Return nonconformities.
    
    A list of tuple is returned:
    - type of audit
    - nonconformity description
    """
    def getNonconformities(self):
        for row in self._missing:
            message = u'Pharmacy "{}" is missing in dataset.'.format(row[0])
            self._nonconformities.append(('Completeness', message))
        return self._nonconformities