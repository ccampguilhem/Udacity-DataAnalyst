"""
Function to download OpenStreetMap dataset.
"""

CONFIG = {
    #"SELECTION": "PRESELECTED", #Update the PRESELECTION variable
    #"SELECTION": "USER", #Update the USER_SELECTION with the box you want
    "SELECTION": "CACHE", #Use any data file present in directory
    "USER_SELECTION": (43.5799, 1.3434, 43.5838, 1.3496),
    "PRESELECTIONS": {"Tournefeuille": (43.5475, 1.2767, 43.6019, 1.3909),
                      "City center": (43.5799, 1.3434, 43.5838, 1.3496),
                      "Toulouse": (43.3871, 0.9874, 43.8221, 1.9006)},
    "PRESELECTION": "Tournefeuille",
    "TEMPLATE": """
(
   node({},{},{},{});
   <;
);
out meta;
"""
}
        
import os
import requests


def download_map_area():
    """
    Download the map area in a file named data.osm.
    
    This function takes into account the following global variables: SELECTION, USER_SELECTION, PRESELECTIONS, 
    PRESELECTION and TEMPLATE defined in CONFIG.
    
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
    if CONFIG["SELECTION"] == "CACHE":
        if not os.path.exists(filename):
            raise ValueError("Cannot use SELECTION=CACHE if no {} file exists.".format(filename))
        else:
            return None, filename, os.path.getsize(filename)
    elif CONFIG["SELECTION"] == "PRESELECTED":
        data = CONFIG["TEMPLATE"].format(*CONFIG["PRESELECTIONS"][CONFIG["PRESELECTION"]])
    elif CONFIG["SELECTION"] == "USER":
        data = CONFIG["TEMPLATE"].format(*CONFIG["USER_SELECTION"])
    else:
        raise ValueError("SELECTION={}".format(CONFIG["SELECTION"]))
        
    #Get XML data
    r = requests.get('http://overpass-api.de/api/interpreter', params={"data": data}, stream=True)
    with open(filename, 'wb') as fobj:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                fobj.write(chunk)
    return r.status_code, filename, os.path.getsize(filename)