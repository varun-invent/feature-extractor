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
in_file1 =  Read the Review links pivot table
in_file2 = Read the all links ABIDE all peproc combined csv

For each link1 in in_file1:
    For each link2 in in_file2:
        if link1 == link2:
            preproc_type = link2['preproc']
            link1['preproc_type'] = 1

'''
def find_consistent_links(in_file1, in_file2):

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
            options_dict[opt] = 0
            #  Setting all option falgs to default 0
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
                    options_dict[preproc_type] = 1
                    print(' Review %s - ABIDE I %s'%(row_idx_df_1 + 2 ,row_idx_df_2 + 2))
                    # rep_links_review.append((row_idx_df_2 + 2))
                    new_row_hemis_region_joined = np.concatenate((df_1[row_idx_df_1], df_2[row_idx_df_2]), axis=None)
                    replicated_df_hemis_region_joined.append(new_row_hemis_region_joined)
                    # count = count + 1
        options_keys = list(options_dict.keys())
        options_values = list(options_dict.values())
        new_row_consistent_df_all_preproc = np.concatenate((df_1[row_idx_df_1,:], options_values),axis=None)
        consistent_df_all_preproc.append(new_row_consistent_df_all_preproc)


    # print('Replicable links: %s'%count)
    out_file_path = '../ABIDE1/Review_ABIDE1_all_preproc.csv'
    new_df = np.array(consistent_df_all_preproc)
    new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns1, options), axis=None))
    new_df.to_csv(out_file_path,index=False)

    # Saving the replicated_df_hemis_region_joined to check is the code is matching links correctly

    out_file_path = '../ABIDE1/ABIDE1_Review_ABIDE1_all_preproc_check_consistency_matches.csv'
    new_df = np.array(replicated_df_hemis_region_joined)
    new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns1, columns2), axis=None))
    new_df.to_csv(out_file_path,index=False)


if __name__ == '__main__':
    csv_input_path = os.path.abspath('../csv_input')
    in_file1 = csv_input_path + '/BN_regions_review_links.csv'
    in_file2 = csv_input_path + '/ABIDE1_links_atlas_map_all_preproc_combined.csv'
    find_consistent_links(in_file1, in_file2)
