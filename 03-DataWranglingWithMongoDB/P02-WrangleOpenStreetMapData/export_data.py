"""
Functions to export data into different formats
"""

import csv
import os


def export_to_csv(dataset):
    """
    Export dataset to csv files.
    
    Python csv module does not support Unicode strings, we need to encode manually in UTF-8.
    The encoding is done by function.
    
    - dataset: dataset to be exported.
    """        
    def encode_utf8(dct):
        """
        Encode keys and values in UTF-8 if they are unicode strings.
        
        csv Python module does not handle it automatically.
        
        - dct: input dictionnary with possibly unicode strings for text keys and values.
        - return: dictionnary with text keys and values into byte strings encoded in UTF-8.
        """
        output = { }
        for key, value in dct.iteritems():
            if type(key) == type(u""):
                key = key.encode('utf-8')
            if type(value) == type(u""):
                value = value.encode('utf-8')
            output[key] = value
        return output
    
    #Process nodes
    with open('nodes.csv', 'w') as f_nodes, open('nodes_tags.csv', 'w') as f_tags:
        f_nodes_fields = ['osmid', 'longitude', 'latitude', 'userid']
        f_tags_fields = ['node_id', 'key', 'value']
        w_nodes = csv.DictWriter(f_nodes, fieldnames=f_nodes_fields)
        w_tags = csv.DictWriter(f_tags, fieldnames=f_tags_fields)
        w_nodes.writeheader()
        w_tags.writeheader()
        for node in dataset["nodes"]:
            osmid = node['osmid']
            tags = node.pop("tags")
            for tag in tags:
                tag[u'node_id'] = osmid
                w_tags.writerow(encode_utf8(tag))
            w_nodes.writerow(encode_utf8(node))
            node["tags"] = tags
    
    #Process ways
    with open('ways.csv', 'w') as f_ways, open('ways_nodes.csv', 'w') as f_nodes, \
            open('ways_tags.csv', 'w') as f_tags:
        f_ways_fields = ['osmid', 'userid']
        f_nodes_fields = ['way_id', 'node_id']
        f_tags_fields = ['way_id', 'key', 'value']
        w_ways = csv.DictWriter(f_ways, fieldnames=f_ways_fields)
        w_nodes = csv.DictWriter(f_nodes, fieldnames=f_nodes_fields)
        w_tags = csv.DictWriter(f_tags, fieldnames=f_tags_fields)
        w_ways.writeheader()
        w_nodes.writeheader()
        w_tags.writeheader()
        for way in dataset["ways"]:
            osmid = way["osmid"]
            tags = way.pop("tags")
            nodes = way.pop("nodes")
            for tag in tags:
                tag[u'way_id'] = osmid
                w_tags.writerow(encode_utf8(tag))
            for node in nodes:
                w_nodes.writerow({'node_id': node, 'way_id': osmid})
            w_ways.writerow(encode_utf8(way))
            way["tags"] = tags
            way["nodes"] = nodes
        
    #Process relations
    with open('relations_ways.csv', 'w') as f_ways, open('relations_nodes.csv', 'w') as f_nodes,  \
            open('relations_tags.csv', 'w') as f_tags, open('relations.csv', 'w') as f_relations, \
            open('relations_relations.csv', 'w') as f_rel_rel:
        f_relations_fields = ['osmid', 'userid']
        f_tags_fields = ['relation_id', 'key', 'value']
        f_ways_fields = ['relation_id', 'way_id']
        f_nodes_fields = ['relation_id', 'node_id']
        f_rel_rel_fields = ['relation_container', 'relation_content']
        w_relations = csv.DictWriter(f_relations, fieldnames=f_relations_fields)
        w_tags = csv.DictWriter(f_tags, fieldnames=f_tags_fields)
        w_ways = csv.DictWriter(f_ways, fieldnames=f_ways_fields)
        w_nodes = csv.DictWriter(f_nodes, fieldnames=f_nodes_fields)
        w_rel_rel = csv.DictWriter(f_rel_rel, fieldnames=f_rel_rel_fields)
        w_relations.writeheader()
        w_ways.writeheader()
        w_nodes.writeheader()
        w_tags.writeheader()
        w_rel_rel.writeheader()
        for relation in dataset["relations"]:
            osmid = relation["osmid"]
            tags = relation.pop("tags")
            nodes = relation.pop("nodes")
            ways = relation.pop("ways")
            relations = relation.pop("relations")
            for tag in tags:
                tag[u'relation_id'] = osmid
                w_tags.writerow(encode_utf8(tag))
            for node in nodes:
                w_nodes.writerow({'node_id': node, 'relation_id': osmid})
            for way in ways:
                w_ways.writerow({'way_id': way, 'relation_id': osmid})
            for rel in relations:
                w_rel_rel.writerow({'relation_container': osmid, 'relation_content': rel})
            w_relations.writerow(encode_utf8(relation))
            relation["tags"] = tags
            relation["ways"] = ways
            relation["nodes"] = nodes
            relation["relations"] = relations


def import_csv_into_sqlite(cursor):
    """
    Mass import csv into SQLite database.
    
    Inspired by https://stackoverflow.com/a/2888042/8500344
    
    - cursor: a database cursor to execute SQL queries
    """
    for table, columns in [('nodes', ['osmid', 'latitude', 'longitude', 'userid']),
                           ('nodes_tags', ['node_id', 'key', 'value']),
                           ('ways', ['osmid', 'userid']),
                           ('ways_tags', ['way_id', 'key', 'value']),
                           ('ways_nodes', ['way_id', 'node_id']),
                           ('relations', ['osmid', 'userid']),
                           ('relations_tags', ['relation_id', 'key', 'value']),
                           ('relations_nodes', ['relation_id', 'node_id']),
                           ('relations_ways', ['relation_id', 'way_id']),
                           ('relations_relations', ['relation_container', 'relation_content'])]:
        with open('{}.csv'.format(table)) as fobj:
            print "Importing {}.csv [{} bytes]...".format(table, os.path.getsize("{}.csv".format(table))),
            reader = csv.DictReader(fobj)
            script = "INSERT INTO {} ({}) VALUES ({})".format(
                table, ",".join(columns), ",".join(map(lambda x: '?', columns)))
            to_db = [[row[col].decode('utf-8') for col in columns] for row in reader]
            cursor.executemany(script, to_db)
            print "done"
