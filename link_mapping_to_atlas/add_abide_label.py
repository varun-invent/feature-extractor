import pandas as pd
import numpy as np
'''
read the The file containing the BN Links:
in_file1 = /mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_Review_Consistent_Combined.csv
This file contains links that are replicated across ABIDE1 and review.


Read the csv containing BN links and corresponding paperIDs
in_file2 = /mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/raw_BN_regions_review_with_paper_id.csv

Read the csv containing distribution of ABIDE and create a dict of (paper_id, ABIDE}
in_file3 = /mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_distribution_in_review.csv

Loop over in_file1
For each BN link loop over the in_file3 and select the paperID where the link
matches and participants have ABIDE in the string

'''

# in_file1 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_Review_Consistent_Combined.csv'
in_file1 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_Review_Consistent_Combined_all_links_duplicate_clustered_others_clustered.csv'
in_file2 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/raw_BN_regions_review_with_paper_id.csv'

in_file3 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_distribution_in_review.csv'


ABIDE_Review_Consistent_Combined_df = pd.read_csv(in_file1)
ABIDE_Review_Consistent_Combined_mat = ABIDE_Review_Consistent_Combined_df.values

raw_BN_regions_review_with_paper_id_df = pd.read_csv(in_file2,  error_bad_lines=False)
raw_BN_regions_review_with_paper_id_mat = raw_BN_regions_review_with_paper_id_df.values

ABIDE_distribution_in_review_df = pd.read_csv(in_file3)
ABIDE_distribution_in_review_mat = ABIDE_distribution_in_review_df.values



# Create paper_ID participant dict
paperID_ABIDE_dict = {}
for row_idx_3 in range(ABIDE_distribution_in_review_mat.shape[0]):
    if 'ABIDE' in ABIDE_distribution_in_review_mat[row_idx_3][-1]:
        paperID_ABIDE_dict[ABIDE_distribution_in_review_mat[row_idx_3][0]] = 'ABIDE'
    else:
        paperID_ABIDE_dict[ABIDE_distribution_in_review_mat[row_idx_3][0]] = ' '


ABIDE_Review_Consistent_Combined_label_added = []
BN_idx_1 = [6,7,8,9]
BN_idx_2 = [0,1,2,3]
BN_paper_id_index = 4
for row_idx_1 in range(ABIDE_Review_Consistent_Combined_mat.shape[0]):
    row_1 = (''.join(ABIDE_Review_Consistent_Combined_mat[row_idx_1,BN_idx_1])).replace(',', '')
    for row_idx_2 in range(raw_BN_regions_review_with_paper_id_mat.shape[0]):
        if not pd.isnull(raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_idx_2]).any():
            # print(row_idx_2)
            row_2 = (''.join(raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_idx_2])).replace(',', '')
            if (row_1 == row_2):
                paperID = raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_paper_id_index]
                abide_label = paperID_ABIDE_dict[paperID]
                temp = np.concatenate((ABIDE_Review_Consistent_Combined_mat[row_idx_1,:], [abide_label, paperID]),axis=None)
                ABIDE_Review_Consistent_Combined_label_added.append(temp)
                print(temp)


filename = in_file1.split('/')[-1].split('.')[0]
out_file_path = filename + '_ABIDE_label_added.csv' 
# out_file_path = 'ABIDE_Review_Consistent_Combined_ABIDE_label_added.csv'
new_df = np.array(ABIDE_Review_Consistent_Combined_label_added)
new_df = pd.DataFrame(data=new_df, columns=np.concatenate((ABIDE_Review_Consistent_Combined_df.columns, ['ABIDE_Label', 'paperID']), axis=None))
new_df.to_csv(out_file_path,index=False)

'''
61 out of 131 links were repeated from ABIDE. Others - 70 links were original
'''
