import os
from neurosynth.base.dataset import download
import nimare
from bs4 import BeautifulSoup
import numpy as np

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

#

"""
 Due to bandwidth limitations, the web interface (https://neurosynth.org/) is not intended to support 
 mass downloading of hundreds or thousands of images, and attempts to scrape content in an automated 
 way will result in permanent IP bans.
 Source: check Data from https://neurosynth.org/code/
 Therefore we download manually each html showing the max number (100) of title under the tag 'studies'
 for each topic inside https://neurosynth.org/analyses/topics/v5-topics-200/ for example.
"""

title = []

for file in [1, 2, 3]:
    with open('/Users/jperaza/Desktop/neurosynth/topics/Neurosynth_topic_137_{}.htm'.format(file)) as html_file:
        soup = BeautifulSoup(html_file, 'lxml')

    studies = soup.find('div', class_='row').find('div', class_='row').find(
        'div', class_='col-md-10 content').find('div', class_='tab-content').find('div', id='studies').table.tbody.find_all('a')

    for study in studies:
        title.append(study.text)

found_ids = dset.metadata['title'].isin(title)
ids = np.zeros(len(dset.ids))
ids[found_ids]=1

# Add annotation to Dataset and save to file
dset.annotations['Neurosynth_v5topic200__topic137'] = ids 
dset.save(os.path.join(out_dir, 'neurosynth_dataset.pkl.gz'))