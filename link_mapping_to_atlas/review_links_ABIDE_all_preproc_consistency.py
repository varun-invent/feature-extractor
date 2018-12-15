import pandas as pd
import numpy as np
import os
import collections

'''
This script reads all the BN links in review, and compares it with the combined
csv file of ABIDE all preprocessing steps.
For each link of review, it calculates, if there exists a corresponding link in
the excel sheet for that and for which preproc type.

Pseudo Code:
------------
in_file1 =  Read the Review links pivot table
in_file2 = Read the all links ABIDE all peproc combined csv

For each link1 in in_file1:
    For each link2 in in_file2:
        if link1 == link2:
            preproc_type = link2['preproc']
            link1['preproc_type'] = 1

Update: 15 December 2018
------------------------
Also add the confounds removed by each of the link the study belonged to

Pseudocode:
----------


'''
def add_all_preproc_and_ABIDE_labels(in_file1,in_file2,in_file3,in_file4):

    Review_ABIDE1_all_preproc_df = pd.read_csv(in_file1)
    Review_ABIDE1_all_preproc_mat = Review_ABIDE1_all_preproc_df.values

    raw_BN_regions_review_with_paper_id_df = pd.read_csv(in_file2,  error_bad_lines=False)
    raw_BN_regions_review_with_paper_id_mat = raw_BN_regions_review_with_paper_id_df.values

    ABIDE_distribution_in_review_df = pd.read_csv(in_file3)
    ABIDE_distribution_in_review_mat = ABIDE_distribution_in_review_df.values

    review_studyID_preproc_df = pd.read_csv(in_file4)
    columns4 = list(review_studyID_preproc_df.columns)[1:]
    review_studyID_preproc_mat = review_studyID_preproc_df.values


    # Create paper_ID participant dict
    paperID_ABIDE_dict = {}
    for row_idx_3 in range(ABIDE_distribution_in_review_mat.shape[0]):
        if 'ABIDE' in ABIDE_distribution_in_review_mat[row_idx_3][-1]:
            paperID_ABIDE_dict[ABIDE_distribution_in_review_mat[row_idx_3][0]] = 'ABIDE'
        else:
            paperID_ABIDE_dict[ABIDE_distribution_in_review_mat[row_idx_3][0]] = ' '


    #  Create paper_ID preproc dict
    paperID_preproc_dict = {}
    for row_idx_4 in range(review_studyID_preproc_mat.shape[0]):
        paperID = review_studyID_preproc_mat[row_idx_4,0]
        paperID_preproc_dict[paperID] = review_studyID_preproc_mat[row_idx_4,1:]



    Review_ABIDE1_all_preproc_label_added = []
    BN_idx_1 = [0,1,2,3]
    BN_idx_2 = [0,1,2,3]
    BN_paper_id_index = 4
    for row_idx_1 in range(Review_ABIDE1_all_preproc_mat.shape[0]):
        try:
            row_1 = (''.join(Review_ABIDE1_all_preproc_mat[row_idx_1,BN_idx_1])).replace(',', '')
        except TypeError:
            import pdb; pdb.set_trace()
        for row_idx_2 in range(raw_BN_regions_review_with_paper_id_mat.shape[0]):
            if not pd.isnull(raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_idx_2]).any():
                # print(row_idx_2)
                row_2 = (''.join(raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_idx_2])).replace(',', '')
                if (row_1 == row_2):
                    paperID = raw_BN_regions_review_with_paper_id_mat[row_idx_2, BN_paper_id_index]

                    # 1. Use the paperID to find the ABIDE label
                    abide_label = paperID_ABIDE_dict[paperID]

                    # 2. Use the floor(paperID) to find the Preproc pipeline
                    preproc_list = paperID_preproc_dict[np.floor(paperID)]

                    #  Add 1 and 2 to the final df

                    temp1 = [abide_label, paperID]
                    temp1.extend(preproc_list)

                    temp2 = np.concatenate((Review_ABIDE1_all_preproc_mat[row_idx_1,:],\
                                temp1),axis=None)
                    Review_ABIDE1_all_preproc_label_added.append(temp2)
                    print(temp2)



    filename = in_file1.split('/')[-1].split('.')[0]
    out_file_path = filename + 'all_preproc_ABIDE_label_added_UC_OC_both.csv'
    # out_file_path = 'Review_ABIDE1_all_preproc_ABIDE_label_added.csv'
    new_df = np.array(Review_ABIDE1_all_preproc_label_added)
    temp3 = ['ABIDE_Label', 'paperID']
    temp3.extend(columns4)

    new_columns = np.concatenate((Review_ABIDE1_all_preproc_df.columns,temp3), axis=None)
    new_df = pd.DataFrame(data=new_df, columns=new_columns)
    new_df.to_csv(out_file_path,index=False)

def set_preproc_flag_in_options_dict(options_dict):
    '''
    For each of the lists in the dict, do the followoing,
    If the list contains both unique -1 and 1, then set the list to 0
    If the list contains only -1 entries, then set list to -1
    Else, set it to 1
    '''
    _options_dict = collections.OrderedDict()
    for key,value in options_dict.items():
        if options_dict[key] != []:
            _options_dict[key] = np.unique(value).sum()
        else:
            _options_dict[key] = np.nan


    return _options_dict





def find_consistent_links(in_file1, in_file2):

    peak_value_idx = 1 # The peak value of a cluster region from CRT

    df_1 = pd.read_csv(in_file1, encoding = "ISO-8859-1",  error_bad_lines=False)
    columns1 = df_1.columns
    df_1 = df_1.values

    df = pd.DataFrame()

    name_1st_region = df_1[:,1]

    name_1st_region_refined_1 = []
    for name in name_1st_region:
        try:
            name_refined = name.split('_')[1].split(',')[0]
        except IndexError:
            name_refined = name

        name_1st_region_refined_1.append(name_refined)

    # Hemisphere
    hemis_1st_region_1 = df_1[:,0]


    name_2nd_region = df_1[:,3]
    name_2nd_region_refined_1 = []
    for name in name_2nd_region:
        try:
            name_refined = name.split('_')[1].split(',')[0]
        except IndexError:
            name_refined = name

        name_2nd_region_refined_1.append(name_refined)

    # Hemisphere
    hemis_2nd_region_1 = df_1[:,2]

    df_2 = pd.read_csv(in_file2, encoding = "ISO-8859-1", error_bad_lines=False )
    columns2 = df_2.columns
    df_2 = df_2.values

    options = np.sort(np.unique(list(df_2[:,-1])))
    print('Options: ',options)

    options_dict = collections.OrderedDict()
    for opt in options:
        options_dict[opt] = 0

    region_indices = [5,7]

    name_1st_region = df_2[:,region_indices[0]]
    name_1st_region_refined_2 = []
    hemis_1st_region_2 = []
    hemis = None
    for name in name_1st_region:
        try:
            name_refined = name.split('_')[0]
            hemis = name.split('_')[1]
        except IndexError:
            #  Cerebellum
            if name.split(' ')[0] == 'Left':
                hemis = 'L'
            elif name.split(' ')[0] == 'Right':
                hemis = 'R'
            else:
                hemis = 'C'
            name_refined = name
        # except AttributeError:
        #     print(name)
        name_1st_region_refined_2.append(name_refined)
        hemis_1st_region_2.append(hemis)


    name_2nd_region = df_2[:,region_indices[1]]
    name_2nd_region_refined_2 = []
    hemis_2nd_region_2 = []

    for name in name_2nd_region:
        try:
            name_refined = name.split('_')[0]
            hemis = name.split('_')[1]

        except IndexError:
            #  Cerebellum
            if name.split(' ')[0] == 'Left':
                hemis = 'L'
            elif name.split(' ')[0] == 'Right':
                hemis = 'R'
            else:
                hemis = 'C'
            name_refined = name

        name_2nd_region_refined_2.append(name_refined)
        hemis_2nd_region_2.append(hemis)

    replicated_df_hemis_region_joined = []
    consistent_df_all_preproc = []

    count = 0
    rep_links_review = []
    for row_idx_df_1 in range(df_1.shape[0]):
        for opt in options:
            # options_dict[opt] = 0
            #  Setting all option flags to default 0
            options_dict[opt] = []
            #  Setting all option flags to default []

        for row_idx_df_2 in range(df_2.shape[0]):
            win = False

            if (name_1st_region_refined_1[row_idx_df_1] == name_1st_region_refined_2[row_idx_df_2]) and \
            (name_2nd_region_refined_1[row_idx_df_1] == name_2nd_region_refined_2[row_idx_df_2]) :
                h11 = hemis_1st_region_1[row_idx_df_1]
                h12 = hemis_1st_region_2[row_idx_df_2]
                h21 = hemis_2nd_region_1[row_idx_df_1]
                h22 = hemis_2nd_region_2[row_idx_df_2]
                if 'C' in [h11, h12] and 'C' in [h21, h22]:
                    win = True
                elif 'C' in [h11, h12]:
                    if (hemis_2nd_region_1[row_idx_df_1] == hemis_2nd_region_2[row_idx_df_2]):
                        win = True
                elif 'C' in [h21, h22]:
                    if (hemis_1st_region_1[row_idx_df_1] == hemis_1st_region_2[row_idx_df_2]):
                        win = True
                elif (hemis_1st_region_1[row_idx_df_1] == hemis_1st_region_2[row_idx_df_2]) and \
                    (hemis_2nd_region_1[row_idx_df_1] == hemis_2nd_region_2[row_idx_df_2]):
                    win = True

                if win == True:
                    preproc_type = df_2[row_idx_df_2,-1]
                    # options_dict[preproc_type] = 1
                    if df_2[row_idx_df_2, peak_value_idx] > 0:
                        options_dict[preproc_type].append(1)
                    else:
                        options_dict[preproc_type].append(-1)


                    print(' Review %s - ABIDE I %s'%(row_idx_df_1 + 2 ,row_idx_df_2 + 2))
                    # rep_links_review.append((row_idx_df_2 + 2))
                    new_row_hemis_region_joined = np.concatenate((df_1[row_idx_df_1], df_2[row_idx_df_2]), axis=None)
                    replicated_df_hemis_region_joined.append(new_row_hemis_region_joined)
                    # count = count + 1

        options_dict = set_preproc_flag_in_options_dict(options_dict)
        # Finds the net connectivity and sets the fconnectivity flag as -1,0 or 1
        options_keys = list(options_dict.keys())
        options_values = list(options_dict.values())
        new_row_consistent_df_all_preproc = np.concatenate((df_1[row_idx_df_1,:], options_values),axis=None)
        consistent_df_all_preproc.append(new_row_consistent_df_all_preproc)


    # print('Replicable links: %s'%count)
    out_file_path = '../ABIDE1/Review_ABIDE1Review_ABIDE1_all_preproc_UC_OC_both.csv'
    new_df = np.array(consistent_df_all_preproc)
    new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns1, options), axis=None))
    new_df.to_csv(out_file_path,index=False)

    # Saving the replicated_df_hemis_region_joined to check is the code is matching links correctly

    out_file_path = '../ABIDE1/Review_ABIDE1_all_preproc_check_consistency_matches.csv'
    new_df = np.array(replicated_df_hemis_region_joined)
    new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns1, columns2), axis=None))
    new_df.to_csv(out_file_path,index=False)


if __name__ == '__main__':
    csv_input_path = os.path.abspath('../csv_input')
    # in_file1 = csv_input_path + '/BN_regions_review_links.csv'
    # in_file2 = csv_input_path + '/ABIDE1_links_atlas_map_all_preproc_combined.csv'
    # find_consistent_links(in_file1, in_file2)

    in_file1 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/Review_ABIDE1_all_preproc_UC_OC_both.csv'
    in_file2 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/raw_BN_regions_review_with_paper_id.csv'
    in_file3 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/ABIDE_distribution_in_review.csv'
    in_file4 = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/review_studyID_preproc.csv'

    add_all_preproc_and_ABIDE_labels(in_file1,in_file2,in_file3,in_file4)
