
# coding: utf-8

# # Wrangle OpenStreetMap data
# [Cédric Campguilhem](https://github.com/ccampguilhem/Udacity-DataAnalyst), August 2017

# <a id="Top"/>

# ## Table of contents
# - [Introduction](#Introduction)
# - [Project organisation](#Organisation)
# - [Map area selection](#Area selection)
# - [XML data structure](#XML data structure)
# - [Data quality audit](#Data quality)
#     - [Validity](#Data validity)
#     - [Accuracy](#Data accuracy)
#     - [Completeness](#Data completeness)
#     - [Consistency](#Data consistency)
#     - [Uniformity](#Data uniformity)
#     - [Conclusion](#Audit conclusion)
# - [Data cleaning](#Data cleaning)
#     - [Method](#Method)
#     - [Converting to dictionnary-like structure](#Converting to dictionnary-like structure)
#     - [Cleaning accuracy issues](#Cleaning accuracy issues)
#     - [Cleaning completeness issues](#Cleaning completeness issues)
#     - [Cleaning consistency issues](#Cleaning consistency issues)
#     - [Cleaning uniformities issues](#Cleaning uniformities issues)
#     - [Conclusion](#Cleaning conclusion)
# - [Data export](#Data export)
#     - [To JSON and MongoDB](#JSON MongoDB)
#     - [To csv and SQLite](#csv SQLite)
# - [Conclusion](#Conclusion)
# - [Appendix](#Appendix)

# <a id="Introduction"/>

# ## Introduction *[top](#Top)*
# 
# This project is related to Data Wrangling with MongoDB course for Udacity Data Analyst Nanodegree program.
# The purpose of this project is to:
# 
# - Collect data from [OpenStreetMap](https://www.openstreetmap.org) web services.
# - Clean the data by fixing few issues introduced by users.
# - Store the dataset in a database to make any further analysis easier.
# 
# OpenStreetMap is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF). 
# 
# This project covers various aspects of data wrangling phase:
# - **screen scraping** with [Requests](http://requests.readthedocs.io/en/master/), an http Python library for making requests on web services,
# - **parsing** XML files with iterative and SAX parsers with Python standard library [xml.etree.ElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html?highlight=iterparse#module-xml.etree.ElementTree) and [xml.sax](https://docs.python.org/2/library/xml.sax.html),
# - **auditing** (validity, accuracy, completeness, consistency and uniformity) and **cleaning** data with Python,
#     - validity: does data conform to a schema ?
#     - accuracy: does data conform to gold standard (a dataset we trust) ?
#     - completeness: do we have all records ?
#     - consistency: is dataset providing contradictory information ?
#     - uniformity: are all data provided in the same units ?
# - **storing** data into SQL database (SQLite) with Python [sqlite3](https://docs.python.org/2/library/sqlite3.html) module and [MongoDG](https://www.mongodb.com/) no-SQL database.
# - exploring dataset **statistics**.
# 
# The storing step will make use of [csv](https://docs.python.org/2/library/csv.html?highlight=csv#module-csv) and [json](https://docs.python.org/2/library/json.html?highlight=json#module-json) formats respectively for SQL and MongoDB exports.
# 
# I am already a bit familiar with SQL but I will also provide SQL output in addition to MongoDB output for the cleaned dataset.

# <a id='Project organisation'/>

# ## Project organisation *[top](#Top)*
# 
# The project is decomposed in the following manner:
# 
# - This notebook (data_wrangling.ipynb) contains top-level code as well as results and report.
# - The [data_wrangling.html](./data_wrangling.html) file is a html export of this notebook.
# - The [environment.yml](./environment.yml) file contains the anaconda environment I used for this project.
# - The [data_wrangling.py](./data_wrangling.py) file is an export of this notebook. To be executed with ipython !
# - The [handler.py](./handler.py) module contains a class used as content handler for SAX XML parser.
# - The [utils.py](./utils.py) module contains functions used by audit classes.
# - The [validity_audit.py](./validity_audit.py) module contains a callback class for validity audit.
# - The [accuracy_audit.py](./accuracy_audit.py) module contains a callback class for accuracy audit.
# - The [completeness_audit.py](./completeness_audit.py) module contains a callback class for completeness audit.
# - The [consistency_audit.py](./consistency_audit.py) module contains a callback class for consistency audit.
# - The [uniformity_audit.py](./uniformity_audit.py) module contains a callback class for uniformity audit.
# - The [clean_data.py](./clean_data.py) module contains functions used to clean dataset.
# - The [dictionnary_export.py](./dictionnary_export.py) module contains a callback class to export data to a dicitonnary.
# - The [export_data.py](./export_data.py) module contains functions used to export data (into csv or SQLite).

# In[1]:


#Enable auto-reload of modules, will help as we have a lot of modules
get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# <a id="Area selection"/>

# ## Map area selection *[top](#Top)*
# 
# If you don't want to have details on how the data from OpenStreetMap is retrieved, you can skip this section. At the end of the processing, you should have a *data.osm* file in the same directory than this notebook.
# 
# I have made the map area selection dynamic. By configuring few variables, a different map area may be extracted from OpenStreetMap. Some pre-selections are available:
# 
# | Pre-selection | Description               | Usage               | File size (bytes) | OpenStreetMap link |
# |:------------- |:------------------------- |:------------------- | -----------------:|:------------------ |
# | Tournefeuille | The city I live in        | Project review      | 103 143 437       | [link](https://www.openstreetmap.org/relation/35735)
# | City center   | Tournefeuille city center | Testing, debugging  | 583 419           | [link](https://www.openstreetmap.org/export#map=14/43.5848/1.3516)
# | Toulouse      | Toulouse and surroundings | Benchmark           | 1 271 859 210     | [link](https://www.openstreetmap.org/search?query=toulouse#map=11/43.6047/1.4442)
# 
# The box variables are in the following order (south-west to north-east):
# 
# - minimum latitude
# - minimum longitude
# - maximum latitude
# - maximum longitude
# 
# **Note: ** The data cleaning provided in this project works for French area, if you select a non-french area no data cleaning will be performed.

# In[2]:


#SELECTION = "PRESELECTED" #Update the PRESELECTION variable
#SELECTION = "USER" #Update the USER_SELECTION with the box you want
SELECTION = "CACHE" #Use any data file present in directory
USER_SELECTION = (43.5799, 1.3434, 43.5838, 1.3496)
PRESELECTIONS = {"Tournefeuille": (43.5475, 1.2767, 43.6019, 1.3909),
                 "City center": (43.5799, 1.3434, 43.5838, 1.3496),
                 "Toulouse": (43.3871, 0.9874, 43.8221, 1.9006)}
PRESELECTION = "Tournefeuille"
TEMPLATE = """
(
   node({},{},{},{});
   <;
);
out meta;
"""


# I have used screen scrapping techniques presented throughout the course to extract data from OpenStreetMap:
# 
# - I use the Overpass API (http://wiki.openstreetmap.org/wiki/Overpass_API).
# - The query form (http://overpass-api.de/query_form.html) sends a POST request to http://overpass-api.de/api/interpreter.
# - From the api/interpreter we can just make a GET request which takes a data parameter containing the box selection:
# 
# ```
# (
#    node(51.249,7.148,51.251,7.152);
#    <;
# );
# out meta;
# ```
# 
# The idea is to send a http GET request using [Requests](http://requests.readthedocs.io/en/master/) and collect results in a stream. This is because the data we get from the request may be huge and may not fit into memory.
# 
# The following method `download_map_area` enables to download map area data and store it in a *data.osm* file:

# In[3]:


import os
import requests


def download_map_area():
    """
    Download the map area in a file named data.osm.
    
    This function takes into account the following global variables: SELECTION, USER_SELECTION, PRESELECTIONS, 
    PRESELECTION and TEMPLATE
    
    If a http request is made, the response status code is returned, otherwise None in returned.
    If SELECTION is set to CACHE and no file is present an exception is raised.
    
    - raise ValueError: if SELECTION=CACHE and there is no cached file
    - raise ValueError: if SELECTION is not [PRESELECTED, USER, CACHE]
    - raise NameError if either of SELECTION, PRESELECTION, PRESELECTIONS, USER_SELECTION or TEMPLATE does not exist.
    - return: tuple:
        - status code or None
        - path to dataset
        - dataset file size (in bytes)
    """
    filename = "data.osm"
    if SELECTION == "CACHE":
        if not os.path.exists(filename):
            raise ValueError("Cannot use SELECTION=CACHE if no {} file exists.".format(filename))
        else:
            return None, filename, os.path.getsize(filename)
    elif SELECTION == "PRESELECTED":
        data = TEMPLATE.format(*PRESELECTIONS[PRESELECTION])
    elif SELECTION == "USER":
        data = TEMPLATE.format(*USER_SELECTION)
    else:
        raise ValueError("SELECTION=")
        
    #Get XML data
    r = requests.get('http://overpass-api.de/api/interpreter', params={"data": data}, stream=True)
    with open(filename, 'wb') as fobj:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                fobj.write(chunk)
    return r.status_code, filename, os.path.getsize(filename)


# In[4]:


#Download dataset
get_ipython().magic(u'time status_code, dataset_path, dataset_size = download_map_area()')
if status_code is None:
    print "The file {} is re-used from a previous download. Its size is {} bytes.".format(dataset_path, dataset_size)
elif status_code == 200:
    print "The file {} has been successfully downloaded. Its size is {} bytes.".format(dataset_path, dataset_size)
else:
    print "An error occured while downloading the file. Http status code is {}.".format(status_code)


# <a id="XML data structure"/>

# ## XML data structure *[top](#Top)*
# 
# In the previous section, we have downloaded a dataset from OpenStreetMap web service. The XML file retrieved this way is stored in the file named *data.osm*.
# 
# In this section we are going to familiarize with the dataset to understand how it's built. As dataset may be a very large file (depending on the map area extracted) we are going to use an iterative parser that does not need to load the entire document in memory.

# In[5]:


#Import the XML library
import xml.etree.cElementTree as et

from collections import Counter, defaultdict
from pprint import pprint

from IPython.core.display import display, HTML


# In[6]:


#Iterative parsing
element_tags = Counter()
for (event, elem) in et.iterparse(dataset_path):
    element_tags[elem.tag] += 1
pprint(dict(element_tags))


# In OpenStreetMap, data is structured this way:
# - A **node** is a location in space defined by its latitude and longitude. It might indicate a standalone point and/or can be used to define shape of a way.
# - A **way** can be either a polyline to represent roads, rivers... or a closed polygon to delimit areas (buildings, parks...).
# - A **nd** is used within way to reference nodes.
# - A **relation** can be defined from **member** nodes and ways to represent routes, bigger area such as regions or city boundaries.
# - A **member** is a subpart of a relation pointing either to a node or a way.
# - A **tag** is a (key, value) information attached to nodes, ways and relations to document in more detail the item.
# - **osm** is the root node in .osm files.
# - **note** and **meta** are metadata.
# 
# We are now going to parse the XML file again to get the full path of each tag in the dataset. We need to use a SAX parser with a custom handler.

# In[7]:


import xml.sax
from handler import OpenStreetMapXmlHandler


# We can now use the handler in SAX parsing:

# In[8]:


parser = xml.sax.make_parser()
with OpenStreetMapXmlHandler() as handler:
    parser.setContentHandler(handler)
    parser.parse(dataset_path)


# In[9]:


#Get tag counts
pprint(handler.getTagsCount())


# The returned tag count is the same than the one we have calculated using `et.iterparse`.

# In[10]:


#Get tag ancestors
pprint(handler.getTagsAncestors())


# As we discussed later on:
# - **osm** element has no ancestor (it's root element)
# - **meta** and **note** only appear in **osm** element
# - **node**, **way** and **relation** are direct children of **osm**
# - **tag** can be used to document any of **node**, **way** and **relation**
# - **member** are only used in **relation** elements (to reference either nodes, ways or other relations)
# - **nd** are only used in **way** elements (to reference nodes)
# 
# Such result will help us a lot when auditing [data quality](#Data quality).

# <a id='Data quality'/>

# ## Data quality audit *[top](#Top)*
# 
# This chapter is divided into 5 sections for each kind of data quality audit:
# - [Validity](#Data validity)
# - [Accuracy](#Data accuracy)
# - [Completeness](#Data completeness)
# - [Consistency](#Data consistency)
# - [Uniformity](#Data uniformity)

# <a id='Data validity'/>

# ### Validity *[audit](#Data quality)*
# 
# Validity is about compliance to a schema. The data we have retrieved from OpenStreetMap servers is a XML file. It exists techniques to validate XML structures such as XML Schema. We won't use such technique here because schema is relatively simple and because XML files can be large enough so we want to stick to using SAX parser.
# 
# Actually, the SAX content handler that has been introduced in previous [section](#XML data structure) will be helpful here as it's already able to list ancestors for each element. We can then define a schema in a similar form and compare both to see if there is any issue.
# 
# The schema is a dictionnary structured this way:
# - key: element tag
# - value: dictionnary with the following keys / values:
#     - *ancestors*: List of any acceptable ancestor path. For example, the path ('osm.way') means that element shall be a children of a way element which itself is a children of a osm element.
#     - *minOccurences*: minimum number of element in the dataset (greater or equal to 0), optional
#     - *maxOccurences*: maximum number of element in the dataset (greater or equal to 1), optional
#     - *requiredAttributes*: list of attribute names that shall be defined for element
#     - *requiredChildren*: list of required children element
#     - *attributesFuncs*: list of callable objects to be run on the element attributes for further checks

# In[11]:


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


# In order to have this schema validated, we are going to create a callback to be passed to SAX content handler we have created earlier:

# In[12]:


from validity_audit import DataValidityAudit


# We create a function that will help us parsing and autiting the data:

# In[13]:


import tabulate

#Define a method to parse and audit
def parse_and_audit(dataset_path, audit=None):
    """
    Parse XML dataset and perform audit quality.
    
    - dataset_path: path to the dataset to be parsed and audited
    - audit: a sequence of audit objects
    - return: sequence of nonconformities
    """
    with OpenStreetMapXmlHandler() as handler:
        if audit is not None:
            for obj in audit:
                handler.registerStartEventCallback(obj.startEventCallback)
                handler.registerEndEventCallback(obj.endEventCallback)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(dataset_path)
    nonconformities = []
    if audit is not None:
        for obj in audit:
            nonconformities.extend(obj.getNonconformities())
    return nonconformities


# In[14]:


#Parse and audit
audit = [DataValidityAudit(schema)]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


# The returned list above shall be empty. It means that no nonconfirmity has been detected for validity audit. The data we get from OpenStreetMap may be trusted in terms of schema compliance.
# 
# The `%timeit` Jupyter magic command enables to monitor how much time it takes to parse and audit the data. As a reference it takes approximately 15 seconds to parse and audit the dataset of around 100 Mb.

# <a id='Data accuracy'/>

# ### Accuracy *[audit](#Data quality)*
# 
# Accuracy is a measurement of coformity with gold standard. On a dataset such as the one from OpenStreetMap it may be difficult to find a gold standard. We are then going to limit this audit to values that are sometimes provided in the dataset for items which represents a town:
# - INSEE indentifier (ref:INSEE in the above example)
# - Population
# - Date of last census (source:population in the above example)
# 
# Here is an example:
# 
# ```xml
# <node id="26691412" lat="43.5827846" lon="1.3466543" version="17" timestamp="2017-08-22T17:20:54Z" changeset="51349577" uid="6523296" user="ccampguilhem">
#     <tag k="addr:postcode" v="31170"/>
#     <tag k="name" v="Tournefeuille"/>
#     <tag k="name:fr" v="Tournefeuille"/>
#     <tag k="name:oc" v="TornafuÃ¨lha"/>
#     <tag k="place" v="town"/>
#     <tag k="population" v="26674"/>
#     <tag k="ref:FR:SIREN" v="213105570"/>
#     <tag k="ref:INSEE" v="31557"/>
#     <tag k="source:population" v="INSEE 2014"/>
#     <tag k="wikidata" v="Q328022"/>
#     <tag k="wikipedia" v="fr:Tournefeuille"/>
# </node>
# ```
# 
# But this information may also be attached to a relation element instead:
# ```xml
# <relation id="158881" version="20" timestamp="2017-06-22T16:33:19Z" changeset="49751028" uid="94578" user="andygol">
#     <member type="node" ref="534672451" role="admin_centre"/>
#     <member type="way" ref="36353842" role="outer"/>
#     <member type="way" ref="166581580" role="outer"/>
#     ...
#     <member type="way" ref="502733025" role="outer"/>
#     <member type="way" ref="502733024" role="outer"/>
#     <member type="way" ref="36353843" role="outer"/>
#     <tag k="addr:postcode" v="31820"/>
#     <tag k="admin_level" v="8"/>
#     <tag k="boundary" v="administrative"/>
#     <tag k="name" v="Pibrac"/>
#     <tag k="name:fr" v="Pibrac"/>
#     <tag k="name:ru" v="Пибрак"/>
#     <tag k="name:uk" v="Пібрак"/>
#     <tag k="name:zh" v="皮布拉克"/>
#     <tag k="population" v="8091"/>
#     <tag k="ref:FR:SIREN" v="213104177"/>
#     <tag k="ref:INSEE" v="31417"/>
#     <tag k="source:population" v="INSEE 2013"/>
# ```
# 
# Our audit code shall take this into account.
# 
# For this example, I have updated the OpenStreetMap database manually to match official data published by [INSEE](https://www.insee.fr/en/accueil). I will use INSEE data as gold standard (see [here](https://www.insee.fr/fr/statistiques/1405599?geo=COM-31557+COM-31291+COM-31149+COM-31424+COM-31157+COM-31417)). The last census in my region is from 2014.
# 
# We are going to define a gold standard in a dictionnary for few towns in the surrounding of Tournefeuille. If you have selected a user-defined area map, it may not be suitable to you:

# In[15]:


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


# Let's create an audit class for accuracy. It will compare each information from items having a "population" tag to the standard above.

# In[16]:


from accuracy_audit import DataAccuracyAudit


# In[17]:


#Parse and audit
audit = [DataAccuracyAudit(gold_standard_insee)]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


# Some accuracy issues are reported because data in OpenStreetMap is not up to date with census of 2014.
# No issue is reported for Tournefeuille because I have manually updated the OpenStreetMap database.
# 
# There are many more accuracy checks that we can do. For example, building with commercial activities have their phone number and web site mentioned in the OpenStreetMap database. Accuracy would have been assessed by checking existence of web site or by comparing phone number to official records.

# <a id='Data completeness'/>

# ### Completeness *[audit](#Data quality)*
# 
# Assessing completeness of data is a difficult task. We'll do the work for pharmacies. We will use another standard: [Pages Jaunes](https://www.pagesjaunes.fr/annuaire/tournefeuille-31/pharmacies). Pages Jaunes provides the same kind of services than Yellow Pages.
# 
# Here is the list of pharmacies we expect to find:

# In[18]:


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


# Let's create an audit class for completeness. It will compare each information from items having a "amenity/pharmacy" tag to the standard above.

# In[19]:


from completeness_audit import DataCompletenessAudit


# In[20]:


#Parse and audit
audit = [DataCompletenessAudit(gold_standard_pages_jaunes, warnings=True)]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


# 4 pharmacies are reported as missing. Some others are reported as present but not expected. This is because dataset extends over boundary of Tournefeuille. We can notice two things:
# 
# - Pharmacie Denise Ribère is missing and Pharmacie Ribère has been found. It may be the pharmacy we expected.
# - Pharmacie Arc En Ciel is missing and Pharmac**c**ie Arc-en-Ciel has been found. Our string comparison function converts to lower case and replace - by space, but there is a typo in OpenStreetMap database. Use of [fuzzy string](https://streamhacker.com/2011/10/31/fuzzy-string-matching-python/) matching algorithms might have helped in this situation.
# 
# For the last two missing items (La Pharmacie Du Vieux Pigeonnier and Pharmacie Julien Riviére-Sacaze), it seems at first glance that dataset is simply uncomplete. But after a closer look to Pages Jaunes on the location of pharmacies, it seems that they match position of Pharmacie Hebraud Meneghetti and Pharmacie Robin.
# 
# A simple rename of pharmacies in OpenStreetMap dataset would be enought to ensure a 100% completeness.

# <a id='Data consistency'/>

# ### Consistency *[audit](#Data quality)*
# 
# Consistency audit consits in finding contradictory information in the dataset or find issues that prevent us from using some information in the dataset.
# 
# In a previous [section](#XML data structure), we have seen that **relation** elements refer to **node**, **way** or other **relation** through the **member** element. Similarly, **way** elements refer to nodes throught **nd** item.
# 
# A consistent dataset would provide **relation** and **way** pointing to **node** and **way** also present in the dataset. This is the check we are going to implement:

# In[21]:


from consistency_audit import DataConsistencyAudit


# In[22]:


#Parse and audit
audit = [DataConsistencyAudit()]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


# Some ways (a very low percentage) refer to non-present nodes. A significant number of relations refer to non-present entities. One possible explanation is that towns may be not completly extracted and relation defines town boundaries with nodes or ways. Those nodes or ways are missing because they are out of the box we have extracted from OpenStreetMap.

# <a id='Data uniformity'/>

# ### Uniformity *[audit](#Data quality)*
# 
# To audit uniformity, we are going to focus on the way addresses are provided in the dataset.
# 
# Here is an example:
# 
# ```xml
# <relation id="1246249" version="2" timestamp="2017-08-21T10:30:22Z" changeset="51299391" uid="922338" user="Hervé TUC">
#     <member type="way" ref="74688949" role="outer"/>
#     <member type="way" ref="74695300" role="outer"/>
#     <member type="way" ref="74692941" role="outer"/>
#     <member type="way" ref="74688530" role="outer"/>
#     <tag k="addr:city" v="Toulouse"/>
#     <tag k="addr:housenumber" v="42"/>
#     <tag k="addr:postcode" v="31057"/>
#     <tag k="addr:street" v="Avenue Gaspard Coriolis"/>
#     ...
# ```
# 
# The item (a relation here) is documented with tags addr:city, addr:housenumber, addr:postcode, addr:street. The addresses in the dataset will be considered uniform if each of them contain all those components. In addition, the way addr:street are recorded will be analyzed to check if mulitple ways of writing street components (Rue, Avenue, Boulevard, Place, ...) are used. The audit class will report any non-uniformity throughout the dataset:

# In[23]:


from uniformity_audit import DataUniformityAudit


# In[24]:


#Parse and audit
audit = [DataUniformityAudit(warnings=False)]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))
streets_patterns = audit[0].getStreetsPatterns()
print streets_patterns


# In terms of uniformity of providing the same address components, the most common issue is to not have postcode and city. Few times housenumber is also missing. Fixing housenumber automatically seems difficult. Fixing postcode may be easy in the case city, as recorded in OpenStreetMap has a single postcode and item has a city attached. There is nothing obvious we can do for items having no postcode and city fields. One possible solution would be to check inclusion of node (given its latitude / longitude) in the polygon delimiting city (as provided by **relation** elements) which can be solved with a little [maths](http://geomalgorithms.com/a03-_inclusion.html).
# 
# There is also a lack of uniformity in the way streets are recorded. For example we can see Av., avenue, or Avenue but this is not a big deal and be fixed easilly.

# <a id='Audit conclusion'/>

# ### Conclusion *[audit](#Data quality)*
# 
# The audit performed is rather incomplete in terms of check that can be performed. But we have seen how we can audit any kind of nonconformity (validity, accuracy, completeness, consistency and uniformity).
# 
# Yet, the frontier between each type of audit may be tenuous:
# - The completeness issues indentified with missing pharmacies turned out to be an accuracy problem (pharmacies are in the dataset but with a different name).
# - The inconsistency issue with nodes or ways referenced either in ways or relations but missing from dataset may be seen as a completeness issue. Nodes and ways probably exist in the full OpenStreetMap database, so this is probably more related to how the data from full database is extracted with a box selection.
# - The uniformity issues in the way addresses are recorded may also be seen as a completeness issue because housenumbers are missing.
# 
# The classification of nonconformities is not that important, but the list (validity, accuracy, completeness, consistency and uniformity) is probably a good hint to be sure we do not forget some kind of checks.
# 
# On large datasets, it seems not impossible but very tedious to run a full quality audit. Knowing the scope of analysis helps in selecting the minimum set of audits to run on the dataset.
# 
# Using an iterative parser is clearly an additional difficulty in writing audit code, things would have been much simpler by using a full-parser like the ones provided by [lxml](http://lxml.de/) library. lxml also implements pretty advanced XPath requests that would have made both auditing and cleaning much faster.
# 
# The following code wraps all audit tasks and returns a table with all kind of nonconformities:

# In[25]:


#Parse and audit
full_audit = [DataValidityAudit(schema), DataAccuracyAudit(gold_standard_insee), 
         DataCompletenessAudit(gold_standard_pages_jaunes), DataConsistencyAudit(), DataUniformityAudit()]
get_ipython().magic(u'time nonconformities = parse_and_audit(dataset_path, full_audit)')
display(HTML(tabulate.tabulate(nonconformities, tablefmt='html')))


# Note that we have not found any validity issue. The XML structure is pretty simple and OpenStreetMap provides XML files that can be trusted in terms of structure. The issues come from data that has been provided by users.
# 
# In the [next section](#Data cleaning), we are going to clean this dataset before importing it into a database.

# <a id='Data cleaning'/>

# ## Data cleaning *[top](#Top)*

# <a id='Method'/>

# ### Method *[cleaning](#Data cleaning)*
# 
# We are not going to clean the XML file we have downloaded from OpenStreetMap. As we need to parse it iteratively, writing a cleaning algorithm would be pretty difficult.
# 
# Here are the steps we are going to follow:
# 
# - Export dataset into a Python dictionnary-like structure.
# - Clean the dictionnary.
# - Save dictionnary into a JSON file.
# - Import JSON file into MongoDB database.
# - Write csv files from dictionnary-like structure.
# - Import csv files into SQLite database.
# 
# **Note:** exporting the dataset to a dictionnary may be memory consumming. I have not used any technique here to reduce memory footprint but [shelve](https://docs.python.org/2/library/shelve.html?highlight=shelve#module-shelve) in standard library may help. Alternatives may be [diskcache](http://www.grantjenks.com/docs/diskcache/tutorial.html) and even directly [pymongo](https://api.mongodb.com/python/current/tutorial.html).

# <a id='Converting to dictionnary-like structure'/>

# ### Converting to dictionnary-like structure *[cleaning](#Data cleaning)*
# 
# We are going to use a similar technique than the one we had for data quality audit. We are basically going to plug a callback class to the SAX content handler to load OpenStreetMap dataset into a dictonnary-like structure.
# 
# First we need to define the dictionnary structure we want to have (this is pseudo-code not actually used in the program):
# 
# ```python
# schema_dict = {
#     'nodes': [
#         {'osmid': 0, #the OpenStreetMap id of node
#          'latitude': 0., #latitude [-90, 90]
#          'longitude': 0., #longitude [-180, 180]
#          'userid': 0, #OpenStreetMap id of owner
#          'tags': [ #list of associated tags
#              {'key': '', #tag key
#               'value': ''}] #tag value
#         }
#     ]
#     'ways': [
#         {'osmid': 0, #the OpenStreetMap id of node
#          'userid': 0, #OpenStreetMap id of owner
#          'tags': [ #list of associated tags
#              {'key': '', #tag key
#               'value': ''}] #tag value
#          'nodes': [ ] #a list of nodes osmid
#         }
#     ]
#     'relations': [
#         {'osmid': 0, #the OpenStreetMap id of node
#          'userid': 0, #OpenStreetMap id of owner
#          'tags': [ #list of associated tags
#              {'key': '', #tag key
#               'value': ''}] #tag value
#          'nodes': [ ] #a list of nodes osmid
#          'ways': [ ] #a list of ways osmid
#          'relations': [ ] #a list of relations osmid
#         }
#     ]
# ```

# In[26]:


from dictionnary_export import DictionnaryExport


# In[27]:


import sys

#Parse and extract
parser = xml.sax.make_parser()
dataset_dict = { }
extract_class = DictionnaryExport(dataset_dict)
with OpenStreetMapXmlHandler() as handler:
    handler.registerStartEventCallback(extract_class.startEventCallback)
    handler.registerEndEventCallback(extract_class.endEventCallback)
    parser.setContentHandler(handler)
    get_ipython().magic(u'time parser.parse(dataset_path)')
for kind in ['nodes', 'ways', 'relations']:
    print "{} {} exported.".format(len(dataset_dict[kind]), kind)


# All nodes, ways and relations have been exported. We can investigate few items:

# In[28]:


print dataset_dict['nodes'][-1]


# In[29]:


print dataset_dict['ways'][-1]


# In[30]:


print dataset_dict['relations'][-1]


# Having the dataset in this format is much more handy. But making queries into it requires to write dedicated functions. That's all the point to use a database: anything to perform requests is already implemented for us. For now, it is convenient enough to perform the data cleaning.

# <a id='Cleaning accuracy issues'/>

# ### Cleaning accuracy issues *[cleaning](#Data cleaning)*
# 
# In data accuracy audit [section](#Data accuracy) we have spotted few accuracy issues regarging city populations. The idea here is just to update nodes and relations having population tag so they match the INSEE standard.
# 
# A simple function may be written for that purpose:

# In[31]:


from clean_data import clean_accuracy


# In[32]:


get_ipython().magic(u'time inodes, irelations = clean_accuracy(dataset_dict, gold_standard_insee)')
for inode in inodes:
    pprint(dataset_dict["nodes"][inode]["tags"])
for irelation in irelations:
    pprint(dataset_dict["relations"][irelation]["tags"])


# <a id='Cleaning completeness issues'/>

# ### Cleaning completeness issues *[cleaning](#Data cleaning)*
# 
# In data completeness audit [section](#Data completeness) we have indentified missing records in the dataset. It turned out that issues indentified as completeness issues may be seen as accuracy issues since the pharmacies are not  recorded with the proper name.
# 
# We can deal with these issues with a simple function:

# In[33]:


from clean_data import clean_completeness


# In[34]:


pharmacy_mapping = {u"Pharmacie Ribère": u"Pharmacie Denise Ribère", 
                    u"Pharmaccie Arc-en-Ciel": u"Pharmacie Arc En Ciel", 
                    u"Pharmacie Robin": u"Pharmacie Julien Riviére-Sacaze",
                    u"Pharmacie Hebraud Meneghetti": u"La Pharmacie Du Vieux Pigeonnier",
                    u"Pharmacie de la Ramée": u"Pharmacie De La Ramée",
                    u"Pharmacie de la Commanderie": u"Pharmacie De La Commanderie",
                    u"Pharmacie du Centre": u"Pharmacie Du Centre",
                    u"Pharmacie de Pahin": "Pharmacie De Pahin",
                    u"Pharmacie CAP 2000": u"Pharmacie Cap 2000"}
get_ipython().magic(u'time inodes = clean_completeness(dataset_dict, pharmacy_mapping)')
for inode in inodes:
    pprint(dataset_dict["nodes"][inode])


# <a id='Cleaning consistency issues'/>

# ### Cleaning consistency issues *[cleaning](#Data cleaning)*
# 
# Some **node**s, **way**s or **relation**s are referenced in **way** or **relation** items but are missing in dataset we have extracted. I have decided to remove any of those items from the dictionnary-like dataset in order to keep a consistent database as output.
# 
# The audit class can be requested to get a set of missing items. Knowing the list, we just have to remove any reference to those items in our cleaned dataset. This can be done with the following function:

# In[35]:


from clean_data import clean_consistency


# In[36]:


missing_nodes = full_audit[3].getMissingNodes()
missing_ways = full_audit[3].getMissingWays()
missing_relations = full_audit[3].getMissingRelations()
get_ipython().magic(u'time iways, irelations = clean_consistency(dataset_dict, missing_nodes, missing_ways, missing_relations)')


# The number of updated ways and relations matches the number of issues we have identified earlier.

# <a id='Cleaning uniformity issues'/>

# ### Clean uniformity issues *[cleaning](#Data cleaning)*
# 
# In data quality audit [section](#Data uniformity) we have identified two different kinds of nonconformities:
# - missing addr:housenumber or addr:postcode
# - non-uniform way of naming streets component
# 
# We will not fix the addr:housenumber because there is no obvious way to do it. We'll try to fix addr:postcode as we may have postcode information in city data. We may not be able to fix 100% of postcode though:
# - some big cities have multiple postcodes
# - the city in addr:city may not match the city name
# - addr:city may not be provided
# 
# Finally, we can easilly solve the second kind of non-uniformity by providing a mapping.
# 
# The following function performs all cleaning related to uniformity issues:

# In[37]:


from clean_data import clean_uniformity


# In[38]:


#Reminder of all patterns encountered
print streets_patterns


# In[39]:


#Mapping
street_mapping = {u"rue": u"Rue",
                  u"impasse": u"Impasse",
                  u"avenue": u"Avenue",
                  u"Av.": u"Avenue",
                  u"place": u"Place",
                  u"allée": u"Allée"}
get_ipython().magic(u'time inodes, iways, irelations = clean_uniformity(dataset_dict, street_mapping)')


# We have been able to fix few postcodes issues (all for which city was provided and was different from Toulouse).

# <a id='Cleaning conclusion'/>

# ### Conclusion *[cleaning](#Data cleaning)*
# 
# Cleaning is far from being perfect, but we have illustrated different techniques to clean a dataset. This is definitely a time-consumming activity :)
# 
# It's now time to export dataset into files and databases.

# <a id='Data export'/>

# ## Data export *[top](#Top)*

# <a id='JSON MongoDB'/>

# ### To JSON and MongoDB *[export](#Data export)*
# 
# This is the couple I am least confortable with. Luckily, our dictionnary-like structure is really adapted to both transformation to JSON file or for mass import into MongoDB.
# 
# Let's start with dumping a JSON file:

# In[40]:


import json
with open('data.json', 'w') as fobj:
    get_ipython().magic(u'time fobj.write(json.dumps(dataset_dict))')
print "Size of JSON file {} bytes.".format(os.path.getsize('data.json'))


# Writing is pretty fast for a 68 Mb file.
# 
# Let's try to reload the file:

# In[41]:


with open('data.json', 'r') as fobj:
    get_ipython().magic(u'time dataset_dict = json.loads(fobj.read())')
print "Dataset with {} nodes, {} ways and {} relations.".format(len(dataset_dict["nodes"]), 
        len(dataset_dict["ways"]), len(dataset_dict["relations"]))


# We have not lost anything. Reading is a JSON is longer than writing it though. We can now store the data into a MongoDB database:

# In[42]:


#Connect to MongoDB and remove any previous database (if any)
from pymongo import MongoClient
mongodb_client = MongoClient()
mongodb_client.drop_database('udacity-wrangling')


# In[43]:


#Mass import from JSON file of documents
db = mongodb_client['udacity-wrangling']
nodes = db['nodes']
nodes.insert_many(dataset_dict["nodes"])
ways = db['ways']
ways.insert_many(dataset_dict["ways"])
relations = db["relations"]
relations.insert_many(dataset_dict["relations"])
print db.collection_names()


# In[44]:


#What's in there?
print nodes.find_one()
print ways.find_one()
print relations.find_one()


# In[45]:


#Request by OpenStreetMap id:
for item in nodes.find({'osmid': 8138771}):
    pprint(item)


# In[46]:


#Request east-most nodes (max 3 nodes are returned), SQL LIMIT equivalent
for item in nodes.find({'longitude': {'$gt': 1.39}}).limit(3):
    pprint(item)


# In[47]:


#Refined latitude / longitude box (equivalent to City center dataset)
for item in nodes.find({'longitude': {'$gt': 1.3434, '$lt': 1.3496}, 
                        'latitude': {'$gt': 43.5799, '$lt': 43.5838}}).limit(3):
    pprint(item) 


# In[48]:


#Find in document attributes (list)
for item in relations.find({"nodes": 265545746}):
    pprint(item) 


# In[49]:


#Find in document attributes (dict) with kind of SQL UNION and $and operator:
filter_tags = lambda x: x["key"] in ('name:fr', 'ref:INSEE', 'population', 'source:population')
city_criteria = {"$and": [{"tags.key": "ref:INSEE"}, {"tags.key": "population"}]}
items = [node for node in nodes.find(city_criteria)]
items.extend([relation for relation in relations.find(city_criteria)])
for item in items:
    pprint(dict((t["key"], t["value"]) for t in filter(filter_tags, item["tags"])))


# In[50]:


#Look for pharmacies in Tournefeuille either with city name or postcode, combination of and and or operators:
find_criteria = {"$and": [{"tags.key": "amenity", "tags.value": "pharmacy"}, 
                          {"$or": [{"tags.key": "addr:postcode", "tags.value": "31170"},
                                   {"tags.key": "addr:city", "tags.value": "Tournefeuille"}]}]}
for node in nodes.find(find_criteria):
    pprint(node)


# There is a single one pharmacy with either addr:postcode or addr:city attribute set for pharmacies in Tournfeuille.
# The cleaning made is insufficiant because we haven't been able to affect postcode or city to nodes missing both of them.

# In[51]:


#Get major contributors: usage of aggregation, grouping and sorting (descending)
#We need to build an aggregation pipeline
for item in nodes.aggregate([{"$group": {"_id": "$userid", "count": {"$sum": 1}}}, #group by userid and count
                             {"$project": {"count": { "$multiply": [ "$count", 100. / nodes.count()]}}}, # calculate %
                             {"$sort": {"count": -1}}, #sort by descending order
                             {"$limit": 10}]): #limit to 10 users
    print item
print nodes.count()


# The user owning the most number of nodes in OpenStreetMap is also owner of more than 68% of all nodes ! Let's find out if we can know more about him/her:

# In[52]:


#More information about userid 1685
for item in ways.find({"userid": 1685, "tags.key": "source"}).limit(1):
    pprint(item)


# It seems that he/she is working in Direction Générale des Impôts (French Tax Directorate) in the land registry office (french word: cadastre). French land registry office seems to use OpenStreetMap ;)
# 
# To end this MongoDB capabilities overview, we are trying to do a join to get latitude and longitude of all nodes in the previous way:

# In[53]:


#First let's have a look at what unwind operator does. Match operator enables to use a find in an aggregation
for item in ways.aggregate([{"$match": {"osmid": 30907996}},
                            {"$unwind": "$nodes"},
                            {"$limit": 3}]):
    pprint(item)


# \$unwind operator enables to "deconstruct" an array. In fact we are going to need this operator to perform a join (\$lookup operator). Lookup performs a left join. The join syntax is:

# In[54]:


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


# I am using a LTS version of Ubuntu 16.04 coming with MongoDB 2.6 not supporting yet $lookup operator (supported from version 3.2).
# 
# MongoDB differs from what I know about SQL:
# - no need of schema, it's very easy to store collections from Python
# - aggregate, group, sort, limit, etc... works a bit differently than SQL equivalent but product is well documented and it's easy to find answers on [StackOverflow](https://stackoverflow.com/questions/tagged/mongodb) (as always...)
# - "documents" are also easier to read, information is not spread into multiple tables
# - joining is a bit trickier than SQL, but that's probably the price to pay for lack of strict schema and "completeness" of records. I definitely need to install a newer version to take advantage of it.

# <a id='csv SQLite'/>

# ### To csv and SQLite *[export](#Data export)*
# 
# I have not re-writen another SAX content handler for csv export. I am just going to make use of dictionnary-like structure to export csv files matching the way I am going to structure the SQL database.
# 
# I will create the following files:
# 
# | File                    | Description                                          |
# |:----------------------- |:---------------------------------------------------- |
# | nodes.csv               | nodes attributes                                     |
# | nodes_tags.csv          | nodes tags                                           |
# | ways.csv                | ways attributes                                      |
# | ways_nodes.csv          | references to nodes from ways                        |
# | ways_tags.csv           | ways tags                                            |
# | relations.csv           | relations attributes                                 |
# | relations_nodes.csv     | references to nodes from relations                   |
# | relations_ways.csv      | references to ways from relations                    |
# | relations_relations.csv | references to relations from relations               |
# 
# Contrary to MongoDB, preparation for mass import required more work !
# 
# The following function will create all those files. It takes the dictionnary-like structure as argument:

# In[55]:


from export_data import export_to_csv


# In[56]:


#Reload a dataset from JSON (the one we have is linked to MongoDB)
with open('data.json', 'r') as fobj:
    dataset_csv = json.loads(fobj.read())

#Export to csv
get_ipython().magic(u'time export_to_csv(dataset_csv)')

#Clean dataset
del dataset_csv


# We now have to create the SQLite database. We need to define a schema:

# In[57]:


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


# In[58]:


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


# In[59]:


from export_data import import_csv_into_sqlite
import_csv_into_sqlite(cursor)
print "Database {} ready [{} bytes].".format(sql_database, os.path.getsize(sql_database))


# Now the database has been populated with our dataset we can make some requests. Note that the SQLite file is around 35 Mb, smaller than the JSON file (which was 68 Mb).
# 
# Here are few requests with SQL database:

# In[60]:


#Request by OpenStreetMap id:
cursor.execute("SELECT * FROM nodes WHERE osmid = ?", (8138771,))
pprint(cursor.fetchall())


# In[61]:


#Request east-most nodes (max 3 nodes are returned)
cursor.execute("SELECT * FROM nodes WHERE longitude > 1.39 LIMIT 3")
pprint(cursor.fetchall())


# In[62]:


#Refined latitude / longitude box (equivalent to City center dataset)
cursor.execute("""SELECT * FROM nodes 
               WHERE longitude > ? AND longitude < ? AND 
                     latitude > ? AND latitude < ?
               LIMIT 3""", (1.3434, 1.3496, 43.5799, 43.5838))
pprint(cursor.fetchall())


# In[63]:


#Find in list attributes (contrary to MongoDB we need a join here)
cursor.execute("""SELECT relations.* FROM relations
               JOIN relations_nodes ON relations_nodes.relation_id = relations.osmid
               JOIN nodes ON relations_nodes.node_id = nodes.osmid
               WHERE nodes.osmid = ?""", (265545746,))
pprint(cursor.fetchall())


# In[64]:


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


# In both cases (SQL and MongoDB), making requests based to tag keys and values requires relatively complex code.
# Having a list of tags key / value is highly flexible because new tags may be added easilly but the cost to pay is to make queries and exploration less easy. We could have selected a subset of tags we are interested in and turn them into fields in the database.
# 
# Looking for pharmacies in Tournefeuille would require the a similar kind of request.

# In[65]:


#Get major contributors - we can make arithmetics in SQL requests
cursor.execute("""SELECT userid, count(*) * 100. / (SELECT count(*) FROM nodes) as n 
                  FROM nodes GROUP BY userid ORDER BY n DESC LIMIT 10""")
pprint(cursor.fetchall())


# In[66]:


#More info on user 1685
#cursor.execute("""SELECT ways_tags.key, ways_tags.value """)
cursor.execute("""SELECT ways_tags.key, ways_tags.value 
                  FROM ways_tags
                  JOIN ways ON ways.osmid = ways_tags.way_id
                  WHERE ways.userid = ?
                  GROUP BY ways.userid""", (1685,))
pprint(cursor.fetchall())


# Finally, the latest MongoDB request requiring a join is simple in SQL:

# In[67]:


#Now let's join
cursor.execute("""SELECT nodes.osmid FROM nodes
                  JOIN ways_nodes ON ways_nodes.node_id = nodes.osmid
                  WHERE ways_nodes.way_id = ?""", (30907996,))
pprint(cursor.fetchall())


# In[68]:


#We are done with the database
sql_client.close()


# We stated earlier than joining in MongoDB was more difficult (moreover it's only supported from version 3.2), but actually SQL requires more join operations due to the desing of tables.
# 
# In both cases, it is not straightforward to write requests with tags. The way OpenStreetMap uses tags is very flexible but this flexibility is also playing against consistency in an open-source database (we have found a lot of non-uniformities in the way addresses are recorded for example).
# 
# As we have kept a schema very close from the one in OpenStreetMap, (both for SQLite and MongoDB), we face the same difficulties: the way tags are recorded brings maximum flexibility but writing requests becomes also much more difficult. There is then a trade-off to make between a database structure which enables maximum flexibility (and by extension a higher number of applications) or a database more strict in terms of tagging (fixed-tags for example) that would greatly improve the simplicity of use.

# <a id='Conclusion'/>

# ## Conclusions *[top](#Top)*
# 
# Udacity instructors said thad many data analysts report spending most of their time (up to around 75%) wrangling data, at the end of this project I can say that I now better understand that statement :)
# 
# You can refer to this [Forbes article](https://www.forbes.com/sites/gilpress/2016/03/23/data-preparation-most-time-consuming-least-enjoyable-data-science-task-survey-says/#4ed61cb66f63) for data analysts survey results or to New York Times [one](https://www.nytimes.com/2014/08/18/technology/for-big-data-scientists-hurdle-to-insights-is-janitor-work.html?_r=1) for sources.
# 
# Wrangling data is making compromises:
# 
# - We can probably spend infinite amount of time auditing and cleaning large datasets. The more time is spent on wrangling and the less time will be passed on data exploration tasks. But also the more potential applications we can have with the dataset.
# 
# - The way dataset is made persistant also plays an important role. Schema may be strict and improve the ease of use during data exploration but also decreases the potential of reusability for different purposes.
# 
# Another interesting article from [Openbridge](https://www.openbridge.com/data-wrangling-losing-the-battle/) on data wrangling "battle".
# 
# In terms of techniques, there are a lot of improvements we can make:
# 
# - The dataset of the project remains very small. Even the 1 Gb dataset is small and can fit into memory. So I haven't really explored all techniques for dealing with large datasets: if I used SAX XML parsers, I also, at some point, had a Python dictionnary with the whole dataset in memory. JSON writing also requires to have a full dataset in memory. I gave a brief try to shelve and diskcache modules but I found them very slow, probably a misuse.
# 
# - String comparison may fail, due to different case, accented characters or not, use of - in names,... We could probably increase the flexibility of cleaning (and auting) steps by using some fuzzy comparisons. In addition,  caution is needed to properly deal with unicode strings, encoding and decoding ([Ned Batchelder talk at Pycon 2012 is worth the detour.](https://www.youtube.com/watch?v=sgHbC6udIqc))
# 
# - Finally, my first experience in SQL helps but is not enough when it comes to bigger requests (with subrequests, pivoting...) so I need more practice. MongoDB is the first no-SQL database I use, so I need to practice even more with aggregation pipelines and lookups once I have updated my configuration. I have also seen that it exists a lot of Object Relational Mapping systems based on Python and Mongodb. This would probably worth a try when I have some spare time :)

# <a id="Appendix"/>

# ## Appendix *[top](#Top)*

# ### References
# 
# [OpenStreetData wiki](http://wiki.openstreetmap.org/wiki/Main_Page)<hr>
# [INSEE](https://www.insee.fr/en/accueil) is French National Institute of Statistics and Economic Information. In this project, it is used as *gold* standard.<hr>
# [Pages Jaunes](https://www.pagesjaunes.fr/annuaire/tournefeuille-31/pharmacies) used as another *gold* standard.<hr>
# Validating XML tree with [XML Schema](https://www.w3schools.com/xml/schema_intro.asp) can be done with [lxml](http://lxml.de/validation.html) library. This technique has not been used here as the structure of XML is simple enough. Additionaly, XML Schema validation requires to have XML data into memory and may not be suitable for large files like the ones we might have here.<hr>
# Get line number in a content handler with SAX parser on [StackOverflow](https://stackoverflow.com/a/15477803/8500344).<hr>
# Display lists as html tables in notebook on [StackOverflow](https://stackoverflow.com/a/42323522/8500344).<hr>
# Fuzzy string matching blog post on [streamhacker.com](https://streamhacker.com/2011/10/31/fuzzy-string-matching-python/).<hr>
# MongoDB from Python: [pymongo](http://api.mongodb.com/python/current/tutorial.html) tutorial.<hr>
# MongoDB [manual](https://docs.mongodb.com/manual/).<hr>
# Geometry algorithms for [inclusion](http://geomalgorithms.com/a03-_inclusion.html) checks.<hr>
# StackOverflow for [MongoDB](https://stackoverflow.com/questions/tagged/mongodb).<hr>
# Ned Batchelder talk at Pycon 2012 on [YouTube](https://www.youtube.com/watch?v=sgHbC6udIqc): How to stop unicode pain ?<hr>
# Python SQLite import from csv on [StackOverflow](https://stackoverflow.com/a/2888042/8500344).<hr>
