def findTagInChildren(children, key, value=None):
    """
    Find in children a tag element with specified attribute key.

    If value is set to None, the value is returned. If value is specified, name et attrs of child are returned.
    In case no element or value is found, None is returned

    - children: list of tuples (name of element, element attributes)
    - return: value, (name, attibutes) or None
    """
    #try to get tag with k = place
    for name, attrs in children:
        #Skip if this is not a tag
        if name != "tag":
            continue
        #It's a tag
        try:
            k = attrs['k']
        except KeyError:
            continue
        else:
            if k != key:
                continue
            else:
                try:
                    v = attrs['v']
                except KeyError:
                    continue
                else:
                    if value is None:
                        return v
                    elif v == value:
                        return name, attrs
        return
    
"""
Compare two strings and return True if strings match.

Each string is converted into lower case characters before comparison.
- characters are replaces with space characters.
"""
def compareStrings(string1, string2):
    s1 = string1.lower().replace('-', ' ')
    s2 = string2.lower().replace('-', ' ')
    match = False
    if s1 == s2:
        match = True
    return match
