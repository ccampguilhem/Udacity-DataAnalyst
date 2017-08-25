from collections import Counter


"""
Data validity audit object in a form of a callback for SAX content handler.

This audit class checks the validity to a schema. The nonconformities can be requested after parsing.
"""
class DataValidityAudit(object):
    """
    Constructor.
    
    The specified schema has the following structure:
    
    - key: element tag
    - value: dictionnary with the following keys / values:
        - *ancestors*: List of any acceptable ancestor path. For example, the path 'osm.way' means that element 
        shall be a children of a way element which itself is a children of a osm element.
        - *minOccurences*: minimum number of element in the dataset (greater or equal to 0), optional
        - *maxOccurences*: maximum number of element in the dataset (greater or equal to 1), optional
        - *requiredAttributes*: list of attribute names that shall be defined for element
        - *requiredChildren*: list of required children element
        - *attributesFuncs*: list of callable objects to be run on the element attributes for further checks
    
    - schema: dictionnary with schema to be checked.
    """
    def __init__(self, schema):
        self._schema = schema
        self._count_tags = Counter()
        self._nonconformities = [ ]
    
    """
    Method called back when a start event is encountered.
    
    - stack: current stack of elements being read
    - locator: locator object from SAX parser
    """
    def startEventCallback(self, stack, locator):
        #Get name and attributes
        name = stack[-1][1]
        attrs = stack[-1][2]
        ancestor = ".".join(s[1] for s in stack[:-1])
        
        #Update counter
        self._count_tags[name] += 1
        
        #Check ancestors
        try:
            ancestors = self._schema[name]['ancestors']
        except KeyError:
            pass
        else:
            if ancestor not in ancestors:
                message = "{} element at line {} and column {} has an invalid ancestor: {}".format(
                    name, locator.getLineNumber(), locator.getColumnNumber(), ancestor)
                self._nonconformities.append(('Validity', message))
                
        #Check attributes
        try:
            required_attributes = self._schema[name]['requiredAttributes']
        except KeyError:
            pass
        else:
            for attribute in required_attributes:
                try:
                    attrs[attribute]
                except KeyError:
                    message = "{} element at line {} and column {} is missing a required attribute {}.".format(
                        name, locator.getLineNumber(), locator.getColumnNumber(), attribute)
                    self._nonconformities.append(('Validity', message))
                    
        #Special checks for attributes
        try:
            funcs = self._schema[name]['attributesFuncs']
        except KeyError:
            pass
        else:
            for i, func in enumerate(funcs):
                try:
                    status = func(attrs)
                except Exception as e:
                    exception = "{}({})".format(type(e).__name__, e)
                    message = "An exception {} has been raised while checking attributes with function {} " \
                            "for element {} at line {} and column {}.".format(
                            exception, i, name, locator.getLineNumber(), locator.getColumnNumber())
                    self._nonconformities.append(('Validity', message))
                else:
                    if not status:
                        message = "A custom attribute check failed with function {} for element {} at line {} " \
                            "and column {}.".format(i, name, locator.getLineNumber(), locator.getColumnNumber())
                        self._nonconformities.append(('Validity', message))
                        
    """
    Method called back when an end event is encountered.
    
    - name: element name
    - children: element children
    - locator: locator object from SAX parser
    """
    def endEventCallback(self, name, children, locator):
        #Check required children
        try:
            required_children = self._schema[name]['requiredChildren']
        except KeyError:
            pass
        else:
            actual_children = {c[0] for c in children}
            for r in required_children:
                if r not in actual_children:
                    message = "An element {} is missing in element {} at line {} and column {}.".format(
                            r, name, locator.getLineNumber(), locator.getColumnNumber())
                    self._nonconformities.append(('Validity', message))

    """
    Return nonconformities.
    
    A list of tuple is returned:
    - type of audit
    - nonconformity description
    """
    def getNonconformities(self):
        #Initialization
        nonconformities = self._nonconformities[:]
        
        #Check occurences (we cannot do that on the fly)
        for tag, conf in self._schema.iteritems():
            try:
                min_occurs = conf['minOccurences']
            except KeyError:
                pass
            else:
                if self._count_tags[tag] < min_occurs:
                    message = "The minOccurences criteria failed for {} element. " \
                        "Found {} element(s) while {} is the minimum.".format(tag, self._count_tags[tag], min_occurs)
                    nonconformities.append(('Validity', message))
            try:
                max_occurs = conf['maxOccurences']
            except KeyError:
                pass
            else:
                if self._count_tags[tag] > max_occurs:
                    message = "The maxOccurences criteria failed for {} element. " \
                        "Found {} element(s) while {} is the maximum.".format(tag, self._count_tags[tag], max_occurs)
                    nonconformities.append(('Validity', message))
            
        #End of post-processing
        return nonconformities