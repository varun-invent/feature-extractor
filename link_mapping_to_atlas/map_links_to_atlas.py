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
from multiprocessing import Pool
import multiprocessing.managers



'''
Read UC brain
Read OC brain
Set Threshold for UC and OC brains
Calculate number of UC and OC links

For each Brain loop over the volumes and generate the CSV report for each of the
volume
'''
def map_links_to_atlas(input_list):
    atlas = 'fb'

    thresh_UC,  thresh_OC = input_list[0]
    UC_brain_path, OC_brain_path, out_file_prefix = input_list[1]
    print('Working with UC %s and OC %s'%(thresh_UC, thresh_OC))

    _volumes = 274
    volumes = nib.load(UC_brain_path).shape[-1]
    if _volumes != volumes:
        raise Exception('Volumes not 274')


    threshold = thresh_UC
    contrast = UC_brain_path
    obj = report(contrast, atlas, threshold)

    combined_df = pd.DataFrame()

    for volume in range(volumes):
        path, df = obj.report(volume=volume)
        if not df.empty:
            df = df.assign(ROI_Idx=pd.Series([volume+1]*df.shape[0]))
            df = df.assign(ROI_name=pd.Series([atlasDict[volume+1]]*df.shape[0]))
            df = df.assign(Conectivity=pd.Series([-1]*df.shape[0]))
            combined_df = combined_df.append(df, ignore_index=True)

    threshold = thresh_OC
    contrast = OC_brain_path
    obj = report(contrast, atlas, threshold)

    # combined_df = pd.DataFrame()
    for volume in range(volumes):
        path, df = obj.report(volume=volume)
        if not df.empty:
            df = df.assign(ROI_Idx=pd.Series([volume+1]*df.shape[0]))
            df = df.assign(ROI_name=pd.Series([atlasDict[volume+1]]*df.shape[0]))
            df = df.assign(Conectivity=pd.Series([1]*df.shape[0]))
            combined_df = combined_df.append(df, ignore_index=True)

    out_file = out_file_prefix + '_UC%s_OC%s.csv'%(thresh_UC,thresh_OC)
    combined_df.to_csv(out_file,index= False)
    print('Done with UC %s and OC %s'%(thresh_UC, thresh_OC))



def calc_links_count(brain, thresh):
    '''
    Calculates the number of links in brain i.e. number of significant voxels with
    value above thresh.
    '''
    brain_data = nib.load(brain).get_data()
    brain_data[np.abs(brain_data) < thresh] = 0
    return np.abs((brain_data != 0).sum())

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

# def main(UC_brain_path, OC_brain_path):
#     atlasLabelsPath = crt_path + '/Full_brain_atlas_thr0-2mm/fullbrain_atlas.xml'
#     ATLAS_XML_ZERO_START_INDEX = True
#
#     atlasDict = get_roi_Num_Name_dict(atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX)


if __name__ == '__main__':
    # UC_brain_path = '../ABIDE1/combined_brain_UC_ABIDE1.nii.gz'
    # OC_brain_path = '../ABIDE1/combined_brain_OC_ABIDE1.nii.gz'
    # out_file_prefix = 'ABIDE1/ABIDE1_links_atlas_map'

    UC_brain_path = sys.argv[1]
    OC_brain_path = sys.argv[2]
    out_file_prefix = sys.argv[3]

    atlasLabelsPath = crt_path + '/Full_brain_atlas_thr0-2mm/fullbrain_atlas.xml'
    ATLAS_XML_ZERO_START_INDEX = True

    atlasDict = get_roi_Num_Name_dict(atlasLabelsPath, ATLAS_XML_ZERO_START_INDEX)

    # thresh_UC = 10
    # thresh_OC = 10
    #
    # atlas = 'fb'
    #
    # print('Number of UC links common in at least %s preproc pipelines is %s '%\
    #                     (thresh_UC, calc_links_count(UC_brain_path, thresh_UC)))
    #
    # print('Number of OC links common in at least %s preproc pipelines is %s '%\
    #                     (thresh_OC, calc_links_count(OC_brain_path,thresh_OC)))
    #
    # '''
    # Results:
    # -------
    # Number of UC links common in at least 10 preproc pipelines is 13756
    # Number of OC links common in at least 6 preproc pipelines is 2552
    #
    # Number of OC links common in at least 10 preproc pipelines is 306
    #
    # Number of UC links common in at least 17 preproc pipelines is 1120
    # Number of OC links common in at least 17 preproc pipelines is 0
    #
    #
    #
    # '''


    # out_file = map_links_to_atlas(thresh_UC, UC_brain_path, thresh_OC, OC_brain_path, out_file_prefix)

    thresh_UC  = np.arange(8,17,2)
    thresh_OC  = np.arange(8,17,2)

    thresh_UC_OC = list(zip(thresh_UC, thresh_OC))
    print('Using the following (UC, OC) thresholds:')
    print(thresh_UC_OC)

    #  Set of args that does not change and is used by all the workers
    fixed_args = [UC_brain_path, OC_brain_path, out_file_prefix]

    input_list = []
    for tupl in thresh_UC_OC:
        input_list.append((list(tupl), fixed_args))

    # Create pool of 8 workers i.e. 8 processors will be utilized
    pool = Pool(8)

    # Execute the function - function_perform_action() with the inputs from input_list
    pool.map(map_links_to_atlas, input_list)




    # volumes = 274
    #
    # threshold = thresh_UC
    # contrast = UC_brain_path
    # obj = report(contrast, atlas, threshold)
    #
    # combined_df = pd.DataFrame()
    #
    # for volume in range(volumes):
    #     path, df = obj.report(volume=volume)
    #     if not df.empty:
    #         df = df.assign(ROI_Idx=pd.Series([volume+1]*df.shape[0]))
    #         df = df.assign(ROI_name=pd.Series([atlasDict[volume+1]]*df.shape[0]))
    #         df = df.assign(Conectivity=pd.Series([-1]*df.shape[0]))
    #         combined_df = combined_df.append(df, ignore_index=True)
    #
    # threshold = thresh_OC
    # contrast = OC_brain_path
    # obj = report(contrast, atlas, threshold)
    #
    # # combined_df = pd.DataFrame()
    # for volume in range(volumes):
    #     path, df = obj.report(volume=volume)
    #     if not df.empty:
    #         df = df.assign(ROI_Idx=pd.Series([volume+1]*df.shape[0]))
    #         df = df.assign(ROI_name=pd.Series([atlasDict[volume+1]]*df.shape[0]))
    #         df = df.assign(Conectivity=pd.Series([1]*df.shape[0]))
    #         combined_df = combined_df.append(df, ignore_index=True)
    #
    # out_file = '../ABIDE1/UC_OC_ABIDE1_links_atlas_mapUC%s_OC%s.csv'%(thresh_UC,thresh_OC)
    # combined_df.to_csv(out_file,index= False)

    '''
    Results
    1098 UC and 434 OC links after mapping to to an BN atlas
    '''
    '''
    Next is:
    1. Read the Links in review and extract the XML type names for BN regions.
    2. Break each of the region names so that their hemisphere is another column.
    3. Consider C as Both L and R while matching links.
    4. For each link got here, check how many are replicated.
    '''
