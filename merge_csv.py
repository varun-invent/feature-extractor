import glob
import pandas as pd
import numpy as np

def merge_csv(path_regex, out_file):
    '''
    Merges various CSV files and append new column of ROI Index and Preproc type
    '''

    file_list = []

    combined_df = pd.DataFrame()

    for filename in glob.iglob(path_regex, recursive=True):
        opt = filename.split('/')[-1].split('_')[-1].split('.')[0]
        print(opt)
        df = pd.read_csv(filename)
        # Assigning Options column
        df = df.assign(option=pd.Series([opt]*len(df)))

        # Assigning ROI index column
        df = df.assign(ROI_idx=pd.Series(np.arange(1,275)))

        combined_df = combined_df.append(df, ignore_index=True)


        # import pdb; pdb.set_trace()
    combined_df.to_csv(out_file,index= False)


if __name__ == "__main__":
    # path_regex = "/home/varun/Projects/fmri/feature_extractor/data/**/*.csv"
    path_regex = '/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/*.csv'
    out_file='combined_ABIDE2.csv'
    merge_csv(path_regex,out_file)



# folder_path = "/home/varun/Projects/fmri/feature_extractor/"
#
# file_list = []
#
# combined_df = pd.DataFrame()
#
# for filename in glob.iglob(folder_path + 'data/**/*.csv', recursive=True):
#     opt = filename.split('/')[-1].split('_')[-1].split('.')[0]
#     print(opt)
#     df = pd.read_csv(filename)
#     # Assigning Options column
#     df = df.assign(option=pd.Series([opt]*len(df)))
#
#     # Assigning ROI index column
#     df = df.assign(ROI_idx=pd.Series(np.arange(1,275)))
#
#     combined_df = combined_df.append(df, ignore_index=True)
#
#
#     # import pdb; pdb.set_trace()
# combined_df.to_csv('combined.csv',index= False)
