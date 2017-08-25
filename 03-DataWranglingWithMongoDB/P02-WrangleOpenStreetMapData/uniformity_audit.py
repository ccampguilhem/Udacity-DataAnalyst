from collections import Counter

from utils import findTagInChildren

"""
Data uniformity audit object in a form of a callback for SAX content handler.

This audit class checks existence of all component for addresses:
- addr:city
- addr:housenumber
- addr:street
- addr:postcode

It also checks how addr:street are recorded.
"""
class DataUniformityAudit(object):
    """
    Constructor.
    """
    def __init__(self, warnings=False):
        self._nonconformities = [ ]
        self._streets_patterns = set()
        self._attributes = [ ] #works as a LIFO queue
        self._kind = Counter() #count each kind of non-uniformity
        self._warnings = warnings
    
    """
    Method called back when a start event is encountered.
    
    - stack: stack of elements being read
    - locator: locator object from SAX parser
    """
    def startEventCallback(self, stack, locator):
        name = stack[-1][1]
        attrs = stack[-1][2]
        self._attributes.append(attrs)
        if name == "tag":
            try:
                key = attrs["k"]
            except KeyError:
                return
            else:
                if key != "addr:street":
                    return
            try:
                value = attrs["v"]
            except KeyError:
                return
            #Get first component of street
            self._streets_patterns.add(value.strip().split()[0])
    
    """
    Method called back when an end event is encountered.
    
    - name: element name
    - children: element children
    - locator: locator object from SAX parser
    """
    def endEventCallback(self, name, children, locator):
        #Clean attributes cache
        attrs = self._attributes.pop(-1)
        #Check if item has a tag with k = addr:street
        street = findTagInChildren(children, "addr:street")
        if street is None:
            return
        element_id = int(attrs["id"])
        #Try to get all components (addr:city, addr:postcode, addr:housenumber)
        city = findTagInChildren(children, "addr:city")
        postcode = findTagInChildren(children, "addr:postcode")
        housenumber = findTagInChildren(children, "addr:housenumber")
        #Report any missing field
        missing = [ ]
        if city is None:
            missing.append('city')
        if postcode is None:
            missing.append('postcode')
        if housenumber is None:
            missing.append('housenumber')
        if missing:
            self._kind[tuple(missing)] += 1
            if self._warnings:
                message = "{} element (id: {}) misses the following fields: {}.".format(name, element_id, 
                        ", ".join(missing))
                self._nonconformities.append(('Warning', message))

    """
    Return nonconformities.
    
    A list of tuple is returned:
    - type of audit
    - nonconformity description
    
    - return: list of non-conformities
    """
    def getNonconformities(self):
        for key, value in self._kind.iteritems():
            message = "{} elements miss the following fields: {}.".format(value, ", ".join(key))
            self._nonconformities.append(('Uniformity', message))
        return self._nonconformities
    
    """
    Get all streets patterns from dataset.
    
    - return: set of all streets patterns
    """
    def getStreetsPatterns(self):
        return self._streets_patterns