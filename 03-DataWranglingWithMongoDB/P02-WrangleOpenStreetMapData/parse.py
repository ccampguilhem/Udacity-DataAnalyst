"""
Functions to parse the XML dataset.
"""

import xml.sax

from handler import OpenStreetMapXmlHandler


def parse(dataset_path, pluggins=None):
    """
    Parse XML dataset and execute pluggins.
    
    Pluggins are objects of classes implementing startEventCallback and endEventCallback methods.
    
    - dataset_path: path to the dataset to be parsed and audited
    - pluggins: sequence of pluggins
    """
    with OpenStreetMapXmlHandler() as handler:
        if pluggins is not None:
            for obj in pluggins:
                handler.registerStartEventCallback(obj.startEventCallback)
                handler.registerEndEventCallback(obj.endEventCallback)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(dataset_path)       


def parse_and_audit(dataset_path, audit=None):
    """
    Parse XML dataset and perform audit quality.
    
    - dataset_path: path to the dataset to be parsed and audited
    - audit: a sequence of audit objects
    - return: sequence of nonconformities
    """
    parse(dataset_path, audit)
    nonconformities = []
    if audit is not None:
        for obj in audit:
            nonconformities.extend(obj.getNonconformities())
    return nonconformities
