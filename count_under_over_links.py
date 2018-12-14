import glob
import pandas as pd
import numpy as np
import merge_csv as mc
import nibabel as nib

'''
Counts the total number of over and underconencted links for each ROI for each
preproc step and stores it as a combined CSV file.
'''

def get_links_count(in_file, thresh):
    brain = nib.load(in_file).get_data()
    brain[np.abs(brain) < thresh] = 0
    if len(brain.shape) > 3:
        volumes = brain.shape[-1]
    else:
        volumes = 1

    uc_links_count_list = []
    oc_links_count_list = []
    for volume in range(volumes):
        brain_volume = brain[:,:,:,volume]
        idx = np.where(np.abs(brain_volume) >= thresh)
        uc_links_idx = np.where(brain_volume[idx] < 0)
        if len(uc_links_idx) != 0:
            uc_links_count_list.append(len(uc_links_idx[0]))
        else:
            uc_links_count_list.append(0)

        oc_links_idx = np.where(brain_volume[idx] > 0)
        if len(oc_links_idx) != 0:
            oc_links_count_list.append(len(oc_links_idx[0]))
        else:
            oc_links_count_list.append(0)

    return uc_links_count_list, oc_links_count_list

def merge_csv(csv_path_regex, brain_path_regex, threshold, out_file):
    file_list = []

    combined_df = pd.DataFrame()

    for csv_filename,brain_filename in zip(glob.iglob(csv_path_regex, recursive=True),\
                        glob.iglob(brain_path_regex, recursive=True)):
        opt = csv_filename.split('/')[-1].split('_')[-1].split('.')[0]
        print('Option: ', opt)
        print('Brain Filename:', brain_filename)
        df = pd.read_csv(csv_filename)
        # Assigning Options column
        df = df.assign(option=pd.Series([opt]*len(df)))

        # Assigning ROI index column
        df = df.assign(ROI_idx=pd.Series(np.arange(1,275)))

        # Assigning UC and OC link counts
        uc_links_count_list, oc_links_count_list = \
                            get_links_count(brain_filename, threshold)

        df = df.assign(UC_links_count=pd.Series(uc_links_count_list))
        df = df.assign(OC_links_count=pd.Series(oc_links_count_list))

        combined_df = combined_df.append(df, ignore_index=True)


        # import pdb; pdb.set_trace()
    combined_df.to_csv(out_file,index= False)


if __name__ == "__main__":
    # csv_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/**/*.csv"
    csv_path_regex = '/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/*.csv'

    # brain_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/**/**/map_logq.nii.gz"
    brain_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/**/map_logq.nii.gz"


    # csv_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/calc_residual1smoothing1filt1calc_residual_optionsconst/*.csv"
    # brain_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/calc_residual1smoothing1filt1calc_residual_optionsconst/**/map_logq.nii.gz"



    threshold = 1.3
    out_file='combined_ABIDE2_with_UC_OC.csv'
    merge_csv(csv_path_regex, brain_path_regex, threshold, out_file)
