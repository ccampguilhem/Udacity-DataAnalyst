"""
Data cleaning

Contains functions used to clean data.
"""

def clean_accuracy(dataset, standard):
    """
    Clean accuracy issues according to INSEE standard.
    
    The dataset is modified in-place.
    
    - dataset: dataset to be cleaned
    - standard: gold standard for accuracy criteria (INSEE gold standard)
    - return: list of updated nodes index and list of updated relations index
    """
    nodes = [ ]
    relations = [ ]
    def process_item(kind, modified):
        #Process nodes
        for iitem, item in enumerate(dataset[kind]):
            tag_keys = [tag['key'] for tag in item['tags']]
            #Has population tag?
            try:
                population_index = tag_keys.index('population')
            except ValueError:
                continue
            #Update
            try:
                city = item['tags'][tag_keys.index('name:fr')]['value']
            except ValueError:
                city = item['tags'][tag_keys.index('name')]['value']
            source_population_index = tag_keys.index('source:population')
            if item['tags'][source_population_index]['value'] != standard[city]['source:population'][1]:
                item['tags'][source_population_index]['value'] = standard[city]['source:population'][1]
                item['tags'][population_index]['value'] = standard[city]['population'][1]
                print "updated {} {} ({}).".format(kind.rstrip('s'), item["osmid"], city)
                modified.append(iitem)
            else:
                print "{} {} ({}) is left unchanged.".format(kind.rstrip('s'), item["osmid"], city)
    #Process nodes
    process_item("nodes", nodes)
    #Process relations
    process_item("relations", relations)    
    return nodes, relations



def clean_completeness(dataset, mapping):
    """
    Clean completeness issues according to Pages Jaunes standard.
    
    The dataset is modified in-place.
    
    - dataset: dataset to be cleaned
    - mapping: mapping of phamarcy names
    - return: list of updated nodes index
    """
    nodes = [ ]
    for inode, node in enumerate(dataset["nodes"]):
        tag_keys = [tag['key'] for tag in node['tags']]
        #Has amenity tag?
        try:
            amenity_index = tag_keys.index('amenity')
        except ValueError:
            continue
        else:
            #Check this is a pharmacy
            if node["tags"][amenity_index]['value'].lower() != "pharmacy":
                continue
        #Fix pharmacy name
        name_index = tag_keys.index('name')
        name = node["tags"][name_index]["value"]
        try:
            fixed_name = mapping[name]
        except KeyError:
            print u"{} is left unchanged.".format(name)
        else:
            node["tags"][name_index]["value"] = fixed_name
            nodes.append(inode)
            print u"{} has been updated to {}.".format(name, fixed_name)
    return nodes


def clean_consistency(dataset, missing_nodes, missing_ways, missing_relations):
    """
    Clean consistency issues by removing any reference to missing nodes, ways or relations.
    
    The dataset is modified in-place.
    
    - dataset: dataset to be cleaned
    - missing_nodes: set of missing nodes
    - missing_ways: set of missing ways
    - missing_relations: set of missing relations
    - return: set of updated ways index, set of updated relations
    """
    ways = set()
    relations = set()
    #Process ways
    for iway, way in enumerate(dataset["ways"]):
        to_be_removed = [ ]
        for inode, node in enumerate(way["nodes"]):
            if node in missing_nodes:
                to_be_removed.append(inode)
        to_be_removed.reverse() #so we do not change indexes of items in list while we iterate
        for i in to_be_removed:
            value = way["nodes"].pop(i)
            assert value in missing_nodes #cross-check, just in case I introduce errors by mistake
            ways.add(iway)
    print "{} ways updated.".format(len(ways))
    #Process relations
    for irelation, relation in enumerate(dataset["relations"]):
        for (kind, missing) in [("nodes", missing_nodes), ("ways", missing_ways), ("relations", missing_relations)]:
            to_be_removed = [ ]
            for iitem, item in enumerate(relation[kind]):
                if item in missing:
                    to_be_removed.append(iitem)
            to_be_removed.reverse() #so we do not change indexes of items in list while we iterate
            for i in to_be_removed:
                value = relation[kind].pop(i)
                assert value in missing #cross-check, just in case I introduce errors by mistake
                relations.add(irelation)
    print "{} relations updated.".format(len(relations))
    return ways, relations


def clean_uniformity(dataset, street_mapping):
    """
    Clean uniformity issues by:
    - replacing street components by uniform ones
    - trying to set postcode automatically
    
    The dataset is modified in-place.
    
    - dataset: dataset to be cleaned
    - street_mapping: mapping of street components
    - return: set of updated nodes index, set of updated ways index, set of updated relations index
    """
    nodes = set()
    ways = set()
    relations = set()
    #Process street components
    def process_street_component(kind, dataset, mapping, updated):
        for iitem, item in enumerate(dataset[kind]):
            for tag in item['tags']:
                if tag['key'] == 'addr:street':    
                    component = tag['value'].strip().split()[0]
                    try:
                        fixed_component = mapping[component]
                    except KeyError:
                        continue
                    else:
                        tag['value'] = tag['value'].replace(component, fixed_component, 1)
                        updated.add(iitem)
    for kind, mapping, updated in [("nodes", street_mapping, nodes),
                                   ("ways", street_mapping, ways),
                                   ("relations", street_mapping, relations)]:
        process_street_component(kind, dataset, mapping, updated)
    #Process post codes
    #First we need to get a mapping of city with postcode
    city_postcodes = { }
    def get_postcodes(kind, dataset, postcodes):
        for iitem, item in enumerate(dataset[kind]):
            tag_keys = [tag['key'] for tag in item['tags']]
            try:
                population_index = tag_keys.index('ref:INSEE')
            except ValueError:
                continue
            else:
                #This is a city
                try:
                    city = item['tags'][tag_keys.index('name:fr')]['value']
                except ValueError:
                    city = item['tags'][tag_keys.index('name')]['value']
                #Get postcode
                try:
                    postcode = item['tags'][tag_keys.index('addr:postcode')]['value']
                except:
                    pass
                else:
                    if postcode.isdigit():
                        postcodes[city] = postcode
                    else:
                        print "Items in {} cannot be fixed because there are many postcodes: {}.".format(
                                city, postcode)
    for kind in ["nodes", "relations"]:
        get_postcodes(kind, dataset, city_postcodes)
    #Now we can try to fix addresses for which postcode is missing
    def update_postcodes(kind, dataset, postcodes, updated):
        for iitem, item in enumerate(dataset[kind]):
            tag_keys = [tag['key'] for tag in item['tags']]
            try:
                street_index = tag_keys.index('addr:street')
            except ValueError:
                continue
            else:
                try:
                    postcode_index = tag_keys.index('addr:postcode')
                except ValueError:
                    #postcode is not set
                    try:
                        city = item["tags"][tag_keys.index('addr:city')]["value"]
                    except ValueError:
                        #Item has neither postcode nor city...
                        continue
                    try:
                        postcode = postcodes[city]
                    except KeyError:
                        #We have no postcode for this city
                        #print "{} with osmid {} cannot be fixed because there is no postcode for city {}.".format(
                        #        kind, item['osmid'], city)
                        continue
                    else:
                        item["tags"].append({"key": "addr:postcode", "value": postcode})
                        #print "{} with osmid {} now has a addr:postcode {}.".format(
                        #        kind, item['osmid'], postcode)
                        updated.add(iitem)
                else:
                    #postcode is already set
                    continue
    for kind, updated in [("nodes", nodes),
                          ("ways", ways),
                          ("relations", relations)]:
        update_postcodes(kind, dataset, city_postcodes, updated)   
    print "{} nodes updated.".format(len(nodes))
    print "{} ways updated.".format(len(ways))
    print "{} relations updated.".format(len(relations))    
    return nodes, ways, relations