import pandas as pd
import numpy as np
import os
def label_duplicate_links(in_file, node1_idx_reverse = [1,0],\
                            src_equals_dest_idx = 8, experiment_str='all_links_duplicate_clustered'):
        '''
        This function finds all the links B-A for the link A-B
        Input:
        -----
        in_file: CSV file coming from pivit table. It has no two rows that are exactly
        same.
        node1_idx_reverse: index B-A for A-B

        Output:
        ------
        out_file_path:  is the path of the csv with the duplicates assigned same
        label.

        '''
        df = pd.read_csv(in_file)
        df_mat = df.values
        new_df = []
        # final_df = pd.DataFrame(columns=df.columns)
        i = 0
        label = 0
        for idx1 in range(df_mat.shape[0]):
            node1_idx = node1_idx_reverse + list(range(len(node1_idx_reverse),\
                                                            len(df.columns)))
            found_duplicate = False
            if df_mat[idx1,src_equals_dest_idx]:
                i = i+1
                _label = None
                # Assign a label and append to df
                if experiment_str == 'all_links_duplicate_clustered':
                    label = label + 1
                    _label = label
                elif experiment_str == 'all_links_duplicate_clustered_others_clustered' or\
                     experiment_str == 'no_duplicates_others_clustered':
                    _label = 'Single'

                new_df.append(np.append(df_mat[idx1,:], _label))
                print(i,'Single:',np.append(df_mat[idx1,:], _label))
                continue

            if pd.notna(df_mat[idx1,node1_idx_reverse[0]]) or\
             pd.notna(df_mat[idx1,node1_idx_reverse[int(len(node1_idx_reverse)/2)]]):

                for idx2 in range(idx1, df_mat.shape[0]):
                    if (df_mat[idx1,node1_idx] == df_mat[idx2,:]).all() and \
                    not df_mat[idx1,src_equals_dest_idx]:
                        label = label + 1
                        i = i+1
                        new_df.append(np.append(df_mat[idx1,:], label))
                        print('-----------------------------------------------')
                        print(i,':',np.append(df_mat[idx1,:], label))

                        if experiment_str != 'no_duplicates_others_clustered':
                            i = i+1
                            new_df.append(np.append(df_mat[idx2,:], label))
                            print(i,':',np.append(df_mat[idx2,:], label))

                        print('-----------------------------------------------')
                        df_mat[idx2,:] = [np.nan]*len(df_mat[idx2,:])
                        df_mat[idx2,src_equals_dest_idx] = False # So that the Equal case does not with nan
                        found_duplicate = True

                if not found_duplicate:
                    _label = None
                    # Assign a label and append to df
                    if experiment_str == 'all_links_duplicate_clustered':
                        label = label + 1
                        _label = label
                    elif experiment_str == 'all_links_duplicate_clustered_others_clustered' or\
                         experiment_str == 'no_duplicates_others_clustered':
                        _label = 'Single'

                    new_df.append(np.append(df_mat[idx1,:], _label))
                    i = i + 1
                    print(i,': Single',np.append(df_mat[idx1,:], _label))


        in_file_name = os.path.splitext(in_file)[0]
        out_file_path = in_file_name + '_' + experiment_str + '.csv'
        new_df = np.array(new_df)
        new_df = pd.DataFrame(data=new_df, columns=np.append(df.columns, 'Label'))
        new_df.to_csv(out_file_path,index=False)

        return out_file_path, new_df



if __name__ == "__main__":
    in_file = '/mnt/project1/home1/varunk/fMRI/feature-extractor/csv_input/UC_OC_links_atlas_map_pivot_table.csv'
    node1_idx_reverse = [1,0]
    src_equals_dest_idx = 5

    experiment_str1 = 'all_links_duplicate_clustered'
    experiment_str2 = 'all_links_duplicate_clustered_others_clustered'
    experiment_str3 = 'no_duplicates_others_clustered'

    experiment_str_list = [experiment_str1,experiment_str2,experiment_str3]
    for experiment_str in experiment_str_list:
        out_file, new_df = label_duplicate_links(in_file, node1_idx_reverse, src_equals_dest_idx, experiment_str)
        print(new_df)

    '''
    Results:
    --------
    0.1 How many Links are both A-B and B-A.
    Answer: 79 pairs of A-B and B-A i.e 79 links were bidirectional
    TODO:
    Question: Are the above pairs consistent? That is, Is the connectivity of A-B == B-A


    1. How many of the replicated links were underconencted, overconnected or inconsistent
    2. How many of the replicate links had been replicated multiple times in Review (BN regions + CBLM)
       and how many are first time replicated
    3. How many replicated review links are not from ABIDE and how many are?
    4. How many links from ABIDE are A-B and B-A that are replicated with review?
    5. How many links from ABIDE are A-B and B-A that are not replicated with review?

    '''
