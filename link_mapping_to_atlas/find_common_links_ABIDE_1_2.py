import pandas as pd
import numpy as np
import os
'''
This script takes as input ABIDE 1 and 2 pivot tables and compares the link and
finds the matching link.

HOWTO:

in_file1 = Read the ABIDE 1 pivot table
Extract the names of regions from index 0 and 1
in_file2 = Read the ABIDE 2 pivot table

For each of the links (link_1) of in_file1
    Loop through each of the links (link_2) of in_file2
        if(link_1 == link2)
            dict[link_1] = dict[link_1] + 1

'''
csv_input_path = os.path.abspath('../ABIDE2')

in_file1 = csv_input_path + '/UC_OC_ABIDE1_links_atlas_map_pivot_table.csv'
df_1 = pd.read_csv(in_file1, encoding = "ISO-8859-1",  error_bad_lines=False)
columns1 = df_1.columns
df_1 = df_1.values

in_file2 = csv_input_path + '/UC_OC_ABIDE2_links_atlas_map_pivot_table.csv'
df_2 = pd.read_csv(in_file2, encoding = "ISO-8859-1", error_bad_lines=False )
columns2 = df_2.columns
df_2 = df_2.values


count = 0
replicated_df = []
for row_idx_df_1 in range(df_1.shape[0]):
    for row_idx_df_2 in range(df_2.shape[0]):
        if (df_1[row_idx_df_1,0] == df_2[row_idx_df_2,0]) and \
           (df_1[row_idx_df_1,1] == df_2[row_idx_df_2,1]):
           print('ABIDE I %s - ABIDE II %s'%(row_idx_df_1 + 2,row_idx_df_2 + 2))
           new_row = np.concatenate((df_1[row_idx_df_1], df_2[row_idx_df_2]), axis=None)
           replicated_df.append(new_row)
           count = count + 1
print('Replicable links: %s'%count)
out_file_path = 'ABIDE1_ABIDE2_Consistent_Combined.csv'
new_df = np.array(replicated_df)
new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns1, columns2), axis=None))
new_df.to_csv(out_file_path,index=False)




'''
Results:

Replicable links: 201

'''
