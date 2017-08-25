"""
Data export to dictionnary in a form of a callback for SAX content handler.
"""
class DictionnaryExport(object):
    """
    Constructor.
    
    - data: dictionnary to be populated with OpenStreetMap dataset
    """
    def __init__(self, data):
        self._data = data
        if not self._data.has_key('nodes'):
            self._data['nodes'] = [ ]
        if not self._data.has_key('ways'):
            self._data['ways'] = [ ]
        if not self._data.has_key('relations'):
            self._data['relations'] = [ ]
        
    """
    Method called back when a start event is encountered.
    
    - stack: stack of elements being read
    - locator: locator object from SAX parser
    """
    def startEventCallback(self, stack, locator):
        #Get name and attributes
        name = stack[-1][1]
        attrs = stack[-1][2]
        #Node
        if name == "node":
            osmid = int(attrs["id"])
            userid = int(attrs["uid"])
            latitude = float(attrs["lat"])
            longitude = float(attrs["lon"])
            self._data['nodes'].append({'osmid': osmid, 'userid': userid, 'latitude': latitude, 
                                        'longitude': longitude})
        #Way
        elif name == "way":
            osmid = int(attrs["id"])
            userid = int(attrs["uid"])
            self._data['ways'].append({'osmid': osmid, 'userid': userid})
        #Relation
        elif name == "relation":
            osmid = int(attrs["id"])
            userid = int(attrs["uid"])
            self._data['relations'].append({'osmid': osmid, 'userid': userid})
    
    """
    Method called back when an end event is encountered.
    
    - name: element name
    - children: element children
    - locator: locator object from SAX parser
    """
    def endEventCallback(self, name, children, locator):
        #Node
        if name == "node":
            item = self._data["nodes"][-1]
            self._populateWithTags(item, children)
        #Way
        elif name == "way":
            item = self._data["ways"][-1]
            self._populateWithTags(item, children)
            item['nodes'] = [ ]
            for child in children:
                if child[0] == "nd":
                    item['nodes'].append(int(child[1]['ref']))
        #Relation
        elif name == "relation":
            item = self._data["relations"][-1]
            self._populateWithTags(item, children)
            item['nodes'] = [ ]
            item['ways'] = [ ]
            item['relations'] = [ ]
            for child in children:
                if child[0] == "member":
                    if child[1]["type"] == "node":
                        item['nodes'].append(int(child[1]['ref']))
                    elif child[1]["type"] == "way":
                        item['ways'].append(int(child[1]['ref']))
                    elif child[1]["type"] == "relation":
                        item['relations'].append(int(child[1]['ref']))

    def _populateWithTags(self, item, children):
        """
        Append tags from children to given item.
        
        - item: dictionnary of item
        - children: list of (name, attrs) of element children
        """
        item['tags'] = [ ]
        for child in children:
            if child[0] == "tag":
                item['tags'].append({'key': child[1]['k'], 'value': child[1]['v']})                    