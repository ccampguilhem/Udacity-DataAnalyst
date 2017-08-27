
# coding: utf-8

from download import download_map_area


#Download dataset
status_code, dataset_path, dataset_size = download_map_area()
if status_code is None:
    print "The file {} is re-used from a previous download. Its size is {} bytes.".format(dataset_path, dataset_size)
elif status_code == 200:
    print "The file {} has been successfully downloaded. Its size is {} bytes.".format(dataset_path, dataset_size)
else:
    print "An error occured while downloading the file. Http status code is {}.".format(status_code)


#Import the XML library
import xml.etree.cElementTree as et

from collections import Counter, defaultdict
from pprint import pprint

import tabulate
from IPython.core.display import display, HTML


#Iterative parsing
element_tags = Counter()
for (event, elem) in et.iterparse(dataset_path):
    element_tags[elem.tag] += 1
pprint(dict(element_tags))


import xml.sax
from handler import OpenStreetMapXmlHandler


parser = xml.sax.make_parser()
with OpenStreetMapXmlHandler() as handler:
    parser.setContentHandler(handler)
    parser.parse(dataset_path)


#Get tag counts
pprint(handler.getTagsCount())


#Get tag ancestors
pprint(handler.getTagsAncestors())


import functools

#Function to check numbers
check_digit = lambda name, attr: attr[name].isdigit()
check_id_digit = functools.partial(check_digit, 'id')
check_uid_digit = functools.partial(check_digit, 'uid')
check_ref_digit = functools.partial(check_digit, 'ref')

#Define a schema
schema = {
    #osm is root node. There shall be exactely one.
    'osm': { 
        'ancestors': {''}, 
        'minOccurences': 1,
        'maxOccurences': 1},
    #meta shall be within osm element. There shall be exactely one of those.
    'meta': {
        'ancestors': {'osm'},
        'minOccurences': 1,
        'maxOccurences': 1},
    #meta shall be within osm element. There shall be exactely one of those.
    'note': {
        'ancestors': {'osm'},
        'minOccurences': 1,
        'maxOccurences': 1},        
    #node shall be within osm element. A node shall have id, lat (latitude) and lon (longitude) attributes.
    #Additionally, lat shall be in the range [-90, 90] and longitude in the range [-180, 180]. Id shall be a digit 
    #number
    'node': {
        'ancestors': {'osm'},
        'requiredAttributes': ['id', 'lat', 'lon', 'uid'],
        'attributesFuncs': [lambda attr: -90 <= float(attr['lat']) <= 90, 
                            lambda attr: -180 <= float(attr['lon']) <= 180,
                            check_id_digit,
                            check_uid_digit]},
    #way shall be within osm element. A way shall have id attribute. It shall have at least one nd children.
    #id shall be a digit.
    'way': {
        'ancestors': {'osm'},
        'requiredAttributes': ['id', 'uid'],
        'requiredChildren': ['nd'],
        'attributesFuncs': [check_id_digit, check_uid_digit]},
    #nd shall be within way element. A nd shall have ref attribute. ref attribute shall be a digit.
    'nd': {
        'ancestors': {'osm.way'},
        'requiredAttributes': ['ref'],
        'attributesFuncs': [check_ref_digit]},
    #relation shall be within a osm element. It shall have a id attribute and at least one member children. id shall
    #be a digit
    'relation': {
        'ancestors': {'osm'},
        'requiredAttributes': ['id', 'uid'],
        'requiredChildren': ['member'],
        'attributesFunc': [check_id_digit, check_uid_digit]},
    #member shall be within a relation element. It shall have type, ref and role attributes. The type attribute shall
    #be either way or node. The ref attribute shall be a digit.
    'member': {
        'ancestors': {'osm.relation'},
        'requiredAttributes': ['type', 'ref', 'role'],
        'attributesFuncs': [lambda attr: attr['type'] in ['way', 'node', 'relation'],
                            check_ref_digit]},
        
    #tag shall be within node, way or relation. It shall have k and v attributes.
    'tag': {
        'ancestors': {'osm.node', 'osm.way', 'osm.relation'},
        'requiredAttributes': ['k', 'v']},
    }


from validity_audit import DataValidityAudit


from parse import parse_and_audit


#Parse and audit
audit = [DataValidityAudit(schema)]
nonconformities = parse_and_audit(dataset_path, audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


#Used to convert digit in XML with thoudand separators into a Python integer
convert_to_int = lambda x: int(x.replace(" ", ""))

gold_standard_insee = {
    u'Tournefeuille': {
        'population': (convert_to_int, 26674),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31557)},
    u'Léguevin': {
        'population': (convert_to_int, 8892),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31291)},
    u'Colomiers': {
        'population': (convert_to_int, 38541),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31149)},
    u'Plaisance-du-Touch': {
        'population': (convert_to_int, 17278),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31424)},
    u'Cugnaux': {
        'population': (convert_to_int, 17004),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31157)},
    u'Pibrac': {
        'population': (convert_to_int, 8226),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31417)},
    u'Toulouse': {
        'population': (convert_to_int, 466297),
        'source:population': (str, 'INSEE 2014'),
        'ref:INSEE': (convert_to_int, 31555)},       
}


from accuracy_audit import DataAccuracyAudit


#Parse and audit
audit = [DataAccuracyAudit(gold_standard_insee)]
nonconformities = parse_and_audit(dataset_path, audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


gold_standard_pages_jaunes = [
    (u'Pharmacie Denise Ribère', (u'2', u'Rue Platanes', 31170, u'Tournefeuille')),
    (u'Pharmacie De La Ramée', (u'102', u'Chemin Larramet', 31170, u'Tournfeuille')),
    (u'Pharmacie Cap 2000', (u'1', u'Boulevard Jean Gay', 31170, u'Tournfeuille')),
    (u'Pharmacie De La Commanderie', (u'110', u'Avenue Marquisat', 31170, u'Tournfeuille')),
    (u'Pharmacie Julien Riviére-Sacaze', (u'18', u'Boulevard Eugène Montel', 31170, u'Tournfeuille')),
    (u'Pharmacie Arc En Ciel', (u'19', u'Avenue Alphonse Daudet', 31170, u'Tournfeuille')),
    (u'Pharmacie Du Centre', (u'67', u'Rue Gaston Doumergue', 31170, u'Tournfeuille')),
    (u'La Pharmacie Du Vieux Pigeonnier', (u'3', u'Rue Hector Berlioz', 31170, u'Tournfeuille')),
    (u'Pharmacie De Pahin', (u'37', u'Chemin Fournaulis', 31170, u'Tournfeuille'))]


from completeness_audit import DataCompletenessAudit


#Parse and audit
audit = [DataCompletenessAudit(gold_standard_pages_jaunes, warnings=True)]
nonconformities = parse_and_audit(dataset_path, audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


from consistency_audit import DataConsistencyAudit


#Parse and audit
audit = [DataConsistencyAudit()]
nonconformities = parse_and_audit(dataset_path, audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


from uniformity_audit import DataUniformityAudit


#Parse and audit
audit = [DataUniformityAudit(warnings=False)]
nonconformities = parse_and_audit(dataset_path, audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))
streets_patterns = audit[0].getStreetsPatterns()
print streets_patterns


#Parse and audit
full_audit = [DataValidityAudit(schema), DataAccuracyAudit(gold_standard_insee), 
         DataCompletenessAudit(gold_standard_pages_jaunes), DataConsistencyAudit(), DataUniformityAudit()]
nonconformities = parse_and_audit(dataset_path, full_audit)
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


from dictionnary_export import DictionnaryExport
from parse import parse


#Parse and extract
dataset_dict = { }
with DictionnaryExport(dataset_dict) as dict_export:
    parse(dataset_path, [dict_export])


from clean_data import clean_accuracy


inodes, irelations = clean_accuracy(dataset_dict, gold_standard_insee)


from clean_data import clean_completeness


pharmacy_mapping = {u"Pharmacie Ribère": u"Pharmacie Denise Ribère", 
                    u"Pharmaccie Arc-en-Ciel": u"Pharmacie Arc En Ciel", 
                    u"Pharmacie Robin": u"Pharmacie Julien Riviére-Sacaze",
                    u"Pharmacie Hebraud Meneghetti": u"La Pharmacie Du Vieux Pigeonnier",
                    u"Pharmacie de la Ramée": u"Pharmacie De La Ramée",
                    u"Pharmacie de la Commanderie": u"Pharmacie De La Commanderie",
                    u"Pharmacie du Centre": u"Pharmacie Du Centre",
                    u"Pharmacie de Pahin": "Pharmacie De Pahin",
                    u"Pharmacie CAP 2000": u"Pharmacie Cap 2000"}
inodes = clean_completeness(dataset_dict, pharmacy_mapping)


from clean_data import clean_consistency


missing_nodes = full_audit[3].getMissingNodes()
missing_ways = full_audit[3].getMissingWays()
missing_relations = full_audit[3].getMissingRelations()
iways, irelations = clean_consistency(dataset_dict, missing_nodes, missing_ways, missing_relations)


from clean_data import clean_uniformity


#Reminder of all patterns encountered
print streets_patterns


#Mapping
street_mapping = {u"rue": u"Rue",
                  u"impasse": u"Impasse",
                  u"avenue": u"Avenue",
                  u"Av.": u"Avenue",
                  u"place": u"Place",
                  u"allée": u"Allée"}
inodes, iways, irelations = clean_uniformity(dataset_dict, street_mapping)


import json
import os
with open('data.json', 'w') as fobj:
    fobj.write(json.dumps(dataset_dict))
print "Size of JSON file {} bytes.".format(os.path.getsize('data.json'))


with open('data.json', 'r') as fobj:
    dataset_dict = json.loads(fobj.read())
print "Dataset with {} nodes, {} ways and {} relations.".format(len(dataset_dict["nodes"]), 
        len(dataset_dict["ways"]), len(dataset_dict["relations"]))


#Connect to MongoDB and remove any previous database (if any)
from pymongo import MongoClient
mongodb_client = MongoClient()
mongodb_client.drop_database('udacity-wrangling')


#Mass import from JSON file of documents
db = mongodb_client['udacity-wrangling']
nodes = db['nodes']
nodes.insert_many(dataset_dict["nodes"])
ways = db['ways']
ways.insert_many(dataset_dict["ways"])
relations = db["relations"]
relations.insert_many(dataset_dict["relations"])
print db.collection_names()


#Request by OpenStreetMap id:
for item in nodes.find({'osmid': 8138771}):
    pprint(item)


#Request east-most nodes (max 3 nodes are returned), SQL LIMIT equivalent
for item in nodes.find({'longitude': {'$gt': 1.39}}).limit(1):
    pprint(item)


#Refined latitude / longitude box (equivalent to City center dataset)
for item in nodes.find({'longitude': {'$gt': 1.3434, '$lt': 1.3496}, 
                        'latitude': {'$gt': 43.5799, '$lt': 43.5838}}).limit(1):
    pprint(item) 


#Find in document attributes (list)
for item in relations.find({"nodes": 265545746}):
    pprint(item) 


#Find in document attributes (dict) with kind of SQL UNION and $and operator:
filter_tags = lambda x: x["key"] in ('name:fr', 'ref:INSEE', 'population', 'source:population')
city_criteria = {"$and": [{"tags.key": "ref:INSEE"}, {"tags.key": "population"}]}
items = [node for node in nodes.find(city_criteria)]
items.extend([relation for relation in relations.find(city_criteria)])
for item in items:
    pprint(dict((t["key"], t["value"]) for t in filter(filter_tags, item["tags"])))


#Look for pharmacies in Tournefeuille either with city name or postcode, combination of and and or operators:
find_criteria = {"$and": [{"tags.key": "amenity", "tags.value": "pharmacy"}, 
                          {"$or": [{"tags.key": "addr:postcode", "tags.value": "31170"},
                                   {"tags.key": "addr:city", "tags.value": "Tournefeuille"}]}]}
for node in nodes.find(find_criteria):
    pprint(node)


#Get major contributors: usage of aggregation, grouping and sorting (descending)
#We need to build an aggregation pipeline
for item in nodes.aggregate([{"$group": {"_id": "$userid", "count": {"$sum": 1}}}, #group by userid and count
                             {"$project": {"count": { "$multiply": [ "$count", 100. / nodes.count()]}}}, # calculate %
                             {"$sort": {"count": -1}}, #sort by descending order
                             {"$limit": 3}]): #limit to 3 users
    print item


#More information about userid 1685
for item in ways.find({"userid": 1685, "tags.key": "source"}).limit(1):
    pprint(item)


#First let's have a look at what unwind operator does. Match operator enables to use a find in an aggregation
for item in ways.aggregate([{"$match": {"osmid": 30907996}},
                            {"$unwind": "$nodes"},
                            {"$limit": 2}]):
    pprint(item)


#Now let's join
if map(lambda x: int(x), mongodb_client.server_info()['version'].split('.')) > (3, 2, 0):
    try:
        for item in ways.aggregate([{"$match": {"osmid": 30907996}},
                                    {"$unwind": "$nodes"},
                                    {"$lookup": 
                                        {"$from": "nodes", "$localField": "nodes", "$foreignField": "osmid"}}]):
            pprint(item)
    except:
        "Sorry for that, this code is untested because I don't have a recent version of MongoDB yet, "         "I need to updgrade."
else:
    print "Your version of MongoDB does not support $lookup operator."


from export_data import export_to_csv


#Reload a dataset from JSON (the one we have is linked to MongoDB)
with open('data.json', 'r') as fobj:
    dataset_csv = json.loads(fobj.read())

#Export to csv
export_to_csv(dataset_csv)

#Clean dataset
del dataset_csv


sql_schema = """
CREATE TABLE nodes (
    osmid INTEGER PRIMARY KEY NOT NULL,
    latitude REAL,
    longitude REAL,
    userid INTEGER
);

CREATE TABLE nodes_tags (
    node_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE ways (
    osmid INTEGER PRIMARY KEY NOT NULL,
    userid INTEGER
);

CREATE TABLE ways_tags (
    way_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE ways_nodes (
    way_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL
);

CREATE TABLE relations (
    osmid INTEGER PRIMARY KEY NOT NULL,
    userid INTEGER
);

CREATE TABLE relations_tags (
    relation_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE relations_nodes (
    relation_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL
);

CREATE TABLE relations_ways (
    relation_id INTEGER NOT NULL,
    way_id INTEGER NOT NULL
);

CREATE TABLE relations_relations (
    relation_container INTEGER NOT NULL,
    relation_content INTEGER NOT NULL
);
"""


#Create the database
import sqlite3
sql_database = 'data.sql'
#Delete any previous version of database:
try:
    os.remove(sql_database)
except OSError:
    pass
#Close any previous connection
try:
    sql_client.close()
except NameError:
    pass
sql_client = sqlite3.connect(sql_database)
cursor = sql_client.cursor()
cursor.executescript(sql_schema)
sql_client.commit()


from export_data import import_csv_into_sqlite
import_csv_into_sqlite(cursor)
print "Database {} ready [{} bytes].".format(sql_database, os.path.getsize(sql_database))


#Request by OpenStreetMap id:
cursor.execute("SELECT * FROM nodes WHERE osmid = ?", (8138771,))
pprint(cursor.fetchall())


#Request east-most nodes (max 3 nodes are returned)
cursor.execute("SELECT * FROM nodes WHERE longitude > 1.39 LIMIT 3")
pprint(cursor.fetchall())


#Refined latitude / longitude box (equivalent to City center dataset)
cursor.execute("""SELECT * FROM nodes 
               WHERE longitude > ? AND longitude < ? AND 
                     latitude > ? AND latitude < ?
               LIMIT 3""", (1.3434, 1.3496, 43.5799, 43.5838))
pprint(cursor.fetchall())


#Find in list attributes (contrary to MongoDB we need a join here)
cursor.execute("""SELECT relations.* FROM relations
               JOIN relations_nodes ON relations_nodes.relation_id = relations.osmid
               JOIN nodes ON relations_nodes.node_id = nodes.osmid
               WHERE nodes.osmid = ?""", (265545746,))
pprint(cursor.fetchall())


#Find in dict attributes
cursor.execute("""SELECT cities.node, nodes_tags.key, nodes_tags.value
                  FROM nodes_tags
                  JOIN                                                     --- This is a comment
                   (SELECT nodes.osmid AS node FROM nodes                  --- This is a subquery getting nodes
                    JOIN nodes_tags ON nodes_tags.node_id = nodes.osmid    --- with tags ref:INSEE and population
                    WHERE nodes_tags.key = ? OR nodes_tags.key = ?         --- we cannot use AND here so instead
                    GROUP BY nodes.osmid                                   --- we use GROUP BY, count() and HAVING
                    HAVING count(*) = 2) cities ON cities.node = nodes_tags.node_id
                  WHERE nodes_tags.key IN (?, ?, ?, ?)""", 
               (u"ref:INSEE", u"population", u"ref:INSEE", u"population", u"source:population", u"name:fr"))
pprint(cursor.fetchall())


#Get major contributors - we can make arithmetics in SQL requests
cursor.execute("""SELECT userid, count(*) * 100. / (SELECT count(*) FROM nodes) as n 
                  FROM nodes GROUP BY userid ORDER BY n DESC LIMIT 3""")
pprint(cursor.fetchall())


#More info on user 1685
#cursor.execute("""SELECT ways_tags.key, ways_tags.value """)
cursor.execute("""SELECT ways_tags.key, ways_tags.value 
                  FROM ways_tags
                  JOIN ways ON ways.osmid = ways_tags.way_id
                  WHERE ways.userid = ?
                  GROUP BY ways.userid""", (1685,))
pprint(cursor.fetchall())


#Now let's join
cursor.execute("""SELECT nodes.osmid FROM nodes
                  JOIN ways_nodes ON ways_nodes.node_id = nodes.osmid
                  WHERE ways_nodes.way_id = ?""", (30907996,))
pprint(cursor.fetchall())


#We are done with the database
sql_client.close()

