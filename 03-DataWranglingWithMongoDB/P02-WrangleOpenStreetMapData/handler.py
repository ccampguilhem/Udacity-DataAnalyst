import xml.sax
from collections import Counter, defaultdict

"""
Custom handler for parsing OpenStreetMap XML files.

While parsing the XML file, handler keeps trace of:

- tags count
- tags ancestors

It is possible to register callback functions for start or end events.
The callbacks for start event will be called passing the following arguments:
- stack
- locator

The callbacks for end event will be called passing the following arguments:
- element name 
- element children
- locator

Return value of callbacks is ignored by the handler class.

This enables to enhance the parser with 'on the fly' data quality audit or export.
"""
class OpenStreetMapXmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        """
        Constructor.
        
        This class is intended to be used as a context manager.
        
        The state of object keeps a trace of stack while parsing. This enables to collect information 
        from children. The stack is destroyed when end event occured. This enables to limit memory usage
        while parsing.
        
        The _stack internal variable stores tuples
        - element unique identifier
        - element name (as provided by start event)
        - element attributes (as provided by start event)
        """
        xml.sax.ContentHandler.__init__(self)      #super not working here ???
        
    def __enter__(self):
        """
        Context manager entry point.
        """
        self._id = 0                               #unique identifier incremented at
        self._stack = [ ]                          #current stack of element being read
        self._element_tags = Counter()             #counter of element tags
        self._element_ancestors = defaultdict(set) #collection of ancestors per tag
        self._start_callbacks = [ ]                #start event callbacks
        self._end_callbacks = [ ]                  #end event callbacks
        self._children = { }                       #children elements of elements being read
        return self
            
    def __exit__(self, *args):
        """
        Context manager exit point.
        """
        pass

    def startElement(self, name, attrs):
        """
        Method invoked when starting to read an element in XML dataset.

        This method is part of of xml.sax.ContentHandler interface and is overloaded here.

        - name: tag of element being read
        - attrs: element attributes
        """
        #Get identifier for current element
        identifier = self._requestUniqueIdentifier()

        #Has element a parent? If yes get the id.
        try:
            parent_tuple = self._stack[-1]
            if parent_tuple[1] == 'osm':
                #We ignore osm element as it has too many children
                parent = None
            else:
                parent = parent_tuple[0]
        except IndexError:
            parent = None
                    
        #Exploit current stack to get ancestor
        ancestor = ".".join([s[1] for s in self._stack])
        self._element_ancestors[name].add(ancestor)
        
        #Update tag counter
        self._element_tags[name] += 1
        
        #Update parent children (if any)
        if parent is not None:
            self._children[parent].append((name, attrs))
            
        #Initialisation of own children
        self._children[identifier] = [ ]
        
        #Update stack
        self._stack.append((identifier, name, attrs))
        
        #Use registered callbacks
        for callback in self._start_callbacks:
            callback(self._stack, self._locator)
        
    def endElement(self, name):
        """
        Method invoked when ending to read an element in XML dataset.

        This method is part of of xml.sax.ContentHandler interface and is overloaded here.

        - name: tag of element being read
        """        
        #Get identifier
        identifier = self._stack[-1][0]
        
        #Use registered callbacks before element is cleaned        
        for callback in self._end_callbacks:
            
            callback(name, self._children[identifier], self._locator)
            
        #Cleaning
        identifier, name, attrs = self._stack.pop(-1)
        del self._children[identifier]
            
    def getTagsCount(self):
        """
        Get a dictionnary with tags count.

        - return: dictionnary where keys are tags and values are count
        """
        return dict(self._element_tags)

    def getTagsAncestors(self):
        """
        Get a dictionnary with tags ancestors.

        - return: dictionnary where keys are tags and values are a sequence of all different ancestors path
        """
        return dict(self._element_ancestors)
    
    def registerStartEventCallback(self, func):
        """
        Register a callback for start event.

        Note that return value of callback is ignored. Any exception raised by callback is not catched by handler, 
        so you should take care of catching all exceptions within the callback itself.

        - func: a callable object taking stack and locator as arguments.
        """
        self._start_callbacks.append(func)
        
    def registerEndEventCallback(self, func):
        """
        Register a callback for end event.

        Note that return value of callback is ignored. Any exception raised by callback is not catched by handler, 
        so you should take care of catching all exceptions within the callback itself.

        - func: a callable object taking element name, element children and locator as arguments.
        """
        self._end_callbacks.append(func)
        
    def clearCallbacks(self):
        """
        Remove all registered callbacks.
        """
        self._end_callbacks = [ ]
        self._start_callbacks = [ ]
        
    def _requestUniqueIdentifier(self):
        """
        Return a unique identifier used at parsing time.
        
        - return: identifier
        """
        self._id += 1
        return self._id