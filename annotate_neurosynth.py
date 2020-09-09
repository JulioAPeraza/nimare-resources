import os
from neurosynth.base.dataset import download
import nimare
from bs4 import BeautifulSoup
import numpy as np
import glob
#from nimare.dataset import Dataset

# Download Neurosynth
out_dir = os.path.abspath('/Users/jperaza/Desktop/neurosynth/')

if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
if not os.path.isfile(os.path.join(out_dir, 'database.txt')):
    download(out_dir, unpack=True)

# Convert Neurosynth database files to NiMARE Dataset
dset = nimare.io.convert_neurosynth_to_dataset(
    os.path.join(out_dir, 'database.txt'),
    os.path.join(out_dir, 'features.txt'))

dset.save(os.path.join(out_dir, 'neurosynth_dataset.pkl.gz'))

"""
 Due to bandwidth limitations, the web interface (https://neurosynth.org/) is not intended to support 
 mass downloading of hundreds or thousands of images, and attempts to scrape content in an automated 
 way will result in permanent IP bans.
 Source: check Data from https://neurosynth.org/code/

 Therefore we download manually each html showing the max number (100) of title under the tag 'studies'
 for each topic inside https://neurosynth.org/analyses/topics/v5-topics-200/ for example.
 Donwload all the files to out_dir/v5topic200
 Download the root pages of the topics (https://neurosynth.org/analyses/topics/v5-topics-200/) as:
    - Neurosynth_v5topic200_00_topics.htm
    - Neurosynth_v5topic200_01_topics.htm
    - ...
 Download the pages of each topic (https://neurosynth.org/analyses/topics/v5-topics-200/0) as:
    - Neurosynth_v5topic200_topic000_00.htm
    - Neurosynth_v5topic200_topic000_01.htm
    - ...
"""
#dset = Dataset.load(os.path.join(out_dir, 'neurosynth_dataset.pkl.gz'))
title = []
topics='v5topic200'
for topic in range(200):
    files = glob.glob(os.path.join(out_dir,topics, 'Neurosynth_v5topic200_topic{:03d}_*.htm'.format(topic)))
    files.sort()
    n_topics = glob.glob(os.path.join(out_dir,topics, 'Neurosynth_v5topic200_*_topics.htm'))
    n_topics.sort()

    # find the number of studies by topic to perform a final check
    n_studies = []
    for n_topic in n_topics:
        with open(n_topic) as html_topics:
            soup_topics = BeautifulSoup(html_topics, 'lxml')
        studies_table = soup_topics.find('div', class_='row').find('div', class_='col-md-12 content').find_all('td')

        [n_studies.append(int(studies_table[idx*3+2].text)) for idx in range(int(len(studies_table)/3))]   
    
    #topic_ids = []
    # Find by title
    title = []
    for file in files:
        with open(file) as html_topic:
            soup_topic = BeautifulSoup(html_topic, 'lxml')

        studies = soup_topic.find('div', class_='row').find('div', class_='row').find(
            'div', class_='col-md-10 content').find('div', class_='tab-content').find('div', id='studies').table.tbody.find_all('a')

        for study in studies:
            #topic_ids.append(study['href'].split('/')[4])
            title.append(study.text)

    #if len(topic_ids) != n_studies[topic]:
    if len(title) != n_studies[topic]:
        #print('Only {} out of {} studies found in topic {} from {}'.format(len(topic_ids),n_studies[topic],topic,topics))
        print('Only {} out of {} studies found in topic {} from {}'.format(len(title),n_studies[topic],topic,topics))
        print('Check local html file')

    #found_ids = dset.ids.isin(topic_ids)
    found_ids = dset.metadata['title'].isin(title)
    ids_colum = np.zeros(len(dset.ids))
    ids_colum[found_ids]=1

    # Add annotation to Dataset and save to file
    dset.annotations['Neurosynth_{}__topic{:03d}'.format(topics,topic)] = ids_colum 

dset.save(os.path.join(out_dir, 'neurosynth_dataset_annotation.pkl.gz'))