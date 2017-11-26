"""
This module contains functions to download datasets required for the Udacity
Data Analyst nanodegree for project Identify Fraud from Enron Email.

The following datasets are downloaded:

- The email dataset from https://www.cs.cmu.edu/~./enron
"""

import os
import sys
import tarfile
import zipfile
import shutil
import pickle

import requests


#URL of Enron email dataset
ENRON_EMAIL = 'https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz'
UD120_ZIP = 'https://github.com/udacity/ud120-projects/archive/master.zip'


def download_file(url):
    """
    Download file at given URL.
    
    - url: url of file to be downloaded
    - return: downloaded file name
    """
    filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return filename


def download_enron_email_dataset(force=False):
    """
    Download Enron email dataset.
    
    Emails are stored in dataset/maildir directory. If directory does not 
    exist, then download is launched. Otherwise downloading is skipped.
    
    - force: force download of dataset even if dataset is already downloaded
    """
    if os.path.exists("./dataset/maildir") and not force:
        return
    else:
        print "Now downloading Enron dataset. This may take a while... ",
        sys.stdout.flush()
        filename = download_file(ENRON_EMAIL)
        print "done"
        print "Now extracting Enron dataset. This may take a while... ",
        sys.stdout.flush()
        tarfile.open(filename).extractall(path="dataset")
        print "done"
        os.remove(filename)
        
        
def download_ud120_project(force=False):
    """
    Download Udacity 120 project (into to machine learning course) from GitHub.
    
    - force: force download of dataset even if dataset is already downloaded
    """
    #List of files to be retrieved from archive
    datasets = ["enron61702insiderpay.pdf", "final_project_dataset.pkl", 
            "final_project_dataset_modified.pkl", "emails_by_address"]
    
    #Check if items are already downloaded
    download = False
    for name in datasets:
        if not os.path.exists("./dataset/{}".format(name)):
            download = True
    
    #Download (if needed):
    if download or force:
        print "Now downloading Udacity 120 project... ",
        sys.stdout.flush()
        filename = download_file(UD120_ZIP)
        print "done"
    else:
        return
    
    #Create full list of files to be extracted
    datasets.pop(-1)
    arch = zipfile.ZipFile(filename, mode='r')
    root = "ud120-projects-master/final_project"
    for path in arch.namelist():
        if os.path.dirname(path) == "{}/emails_by_address".format(root):
            relpath = os.path.relpath(path, root)
            datasets.append(relpath)
        
    #Create directories
    os.makedirs("./dataset/emails_by_address")
    
    #Extract
    print "Now extracting Udacity 120 project... ",
    sys.stdout.flush()
    for name in datasets:
        zipname = "ud120-projects-master/final_project/{}".format(name)
        try:
            arch.extract(zipname, path="./dataset")
        except KeyError:
            #this may happen if we have a directory name
            pass
        else:
            os.rename("./dataset/{}".format(zipname), 
                      "./dataset/{}".format(name))
    
    #Clean
    shutil.rmtree("./dataset/ud120-projects-master")
    os.remove(filename)
    print "done"

        
def download_datasets(force=False):
    """
    Download all datasets required for project.
    
    - force: force dataset download even if dataset has been previously 
             downloaded.
    """
    download_enron_email_dataset(force)
    download_ud120_project(force)
    

def load_project_data():
    """
    Load project data from downloaded pickle file
    
    - returns: data dictionnary
    """
    if os.path.exists("final_project_dataset.pkl"):
        with open("final_project_dataset.pkl", "r") as data_file:
            return pickle.load(data_file)
    else:
        with open("./dataset/final_project_dataset.pkl", "r") as data_file:
            return pickle.load(data_file)


