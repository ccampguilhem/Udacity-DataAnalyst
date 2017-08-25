"""
Data consistency audit object in a form of a callback for SAX content handler.

This audit class checks existence of nodes and ways referenced by ways or relations. Instead of reporting each 
inconsistency, the audit calculates proportion of ways and relations defined without the elements they refer to.

It is possible to request ids of missing nodes, ways and relations.
"""
class DataConsistencyAudit(object):
    """
    Constructor.
    """
    def __init__(self):
        self._nonconformities = [ ]
        self._known_nodes = set()
        self._known_ways = set()
        self._known_relations = set()
        self._ways_ok = 0
        self._ways_ko = 0
        self._relations_ok = 0
        self._relations_ko = 0
        self._missing_nodes = set()
        self._missing_ways = set()
        self._missing_relations = set()
    
    """
    Method called back when a start event is encountered.
    
    - stack: stack of elements being read
    - locator: locator object from SAX parser
    """
    def startEventCallback(self, stack, locator):
        name = stack[-1][1]
        attrs = stack[-1][2]
        try:
            element_id = attrs["id"]
        except KeyError:
            element_id = None
        #node element
        if name == "node":
            self._known_nodes.add(int(element_id))
        #way element
        elif name == "way":
            self._known_ways.add(int(element_id))
        #relation element
        elif name == "relation":
            self._known_relations.add(int(element_id))
    
    """
    Method called back when an end event is encountered.
    
    - name: element name
    - children: element children
    - locator: locator object from SAX parser
    """
    def endEventCallback(self, name, children, locator):
        #way element
        if name == "way":
            error = False
            for child in children:
                if child[0] == "nd":
                    node_id = int(child[1]["ref"])
                    if node_id not in self._known_nodes:
                        self._missing_nodes.add(node_id)
                        error = True
                        break
            if error:
                self._ways_ko += 1
            else:
                self._ways_ok += 1
        #relation element
        elif name == "relation":
            error = False
            for child in children:
                if child[0] == "member":
                    member_type = child[1]["type"]
                    element_id = int(child[1]["ref"])
                    if member_type == "node":
                        if element_id not in self._known_nodes:
                            error = True
                            self._missing_nodes.add(element_id)
                            break
                    elif member_type == "way":
                        if element_id not in self._known_ways:
                            error = True
                            self._missing_ways.add(element_id)
                            break
                    elif member_type == "relation":
                        if element_id not in self._known_relations:
                            error = True
                            self._missing_relations.add(element_id)
                            break
            if error:
                self._relations_ko += 1
            else:
                self._relations_ok += 1

    """
    Return nonconformities.
    
    return: list of tuple (type of audit, nonconformity description)
    """
    def getNonconformities(self):
        if self._ways_ko > 0:
            count = self._ways_ko + self._ways_ok
            message = '{} ways refer to non-present entities out of {} ({:.1f}%)'.format(self._ways_ko, 
                    count, 100. * self._ways_ko / float(count))
            self._nonconformities.append(('Consistency', message))
        if self._relations_ko > 0:
            count = self._relations_ko + self._relations_ok
            message = '{} relations refer to non-present entities out of {} ({:.1f}%)'.format(self._relations_ko, 
                    count, 100. * self._relations_ko / float(count))
            self._nonconformities.append(('Consistency', message))
        return self._nonconformities
    
    """
    Return a list of all missing nodes in dataset.
    
    - return: set of nodes id
    """
    def getMissingNodes(self):
        return self._missing_nodes
    
    """
    Return a list of all missing ways in dataset.
    
    - return: set of ways id
    """
    def getMissingWays(self):
        return self._missing_ways

    """
    Return a list of all missing relations in dataset.
    
    - return: set of relations id
    """
    def getMissingRelations(self):
        return self._missing_relations

        