import sys
import os

# Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
crt_path = os.path.abspath("../../Cluster-Reporting-Tool-master")
# Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
sys.path.insert(0, crt_path)


from cluster_reporting_tool import report
import numpy as np
import pandas as pd
import nibabel as nib
import xml.etree.ElementTree as ET
import glob

'''
This script read the logq value maps, threshold them and maps the links to atlas
And outputs a csv containing all the atlas mapped links and corresponding preproc value
'''

def get_roi_Num_Name_dict(atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX):
    '''
    Takes as input the Atlas labels path and ROI Number and outputs the ROI name for that atlas
    '''
    atlasDict = {}
    root = ET.parse(atlasLabelsPath).getroot()
    elem = root.find('data')
    for regionRow in elem.getchildren():
        # roiNumber  = int(regionRow.items()[2][1]) + 1 .items()
        # gives the items in arbitary order so indexing changes therefore use key= 'index'

        if ATLAS_XML_ZERO_START_INDEX:
            roiNumber = int(regionRow.get(key='index')) + 1
        else:
            roiNumber = int(regionRow.get(key='index'))

        roiName = regionRow.text
        atlasDict[roiNumber] = roiName

    return atlasDict

def generate_crt_csv(csv_path_regex, brain_path_regex, threshold, atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX, atlas_str ,out_file):

    atlasDict = get_roi_Num_Name_dict(atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX)

    atlas = atlas_str

    exec_once = True
    combined_df = pd.DataFrame()
    obj = None
    volumes = None

    for csv_filename,brain_filename in zip(glob.iglob(csv_path_regex, recursive=True),\
                        glob.iglob(brain_path_regex, recursive=True)):
        opt = csv_filename.split('/')[-1].split('_')[-1].split('.')[0]
        print('Option: ', opt)
        print(brain_filename)


        obj = report(brain_filename, atlas, threshold)
        volumes = nib.load(brain_filename).shape[-1]


        for volume in range(volumes):
            path, df = obj.report(volume=volume)
            if not df.empty:
                df = df.assign(ROI_Idx=pd.Series([volume+1]*df.shape[0]))
                df = df.assign(ROI_name=pd.Series([atlasDict[volume+1]]*df.shape[0]))
                # df = df.assign(Conectivity=pd.Series([-1]*df.shape[0]))
                df = df.assign(PreprocOption=pd.Series([opt]*df.shape[0]))
                combined_df = combined_df.append(df, ignore_index=True)
        combined_df.to_csv(out_file,index= False)




if __name__ == '__main__':
    csv_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/*.csv"
    brain_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/**/map_logq.nii.gz"
    threshold = 1.3
    atlasLabelsPath = crt_path + '/Full_brain_atlas_thr0-2mm/fullbrain_atlas.xml'
    ATLAS_XML_ZERO_START_INDEX = True
    atlas_str = 'fb'
    out_file = '../ABIDE2/ABIDE2_links_atlas_map_all_preproc_combined.csv'


    generate_crt_csv(csv_path_regex, brain_path_regex, threshold, \
                        atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX, atlas_str, out_file)
