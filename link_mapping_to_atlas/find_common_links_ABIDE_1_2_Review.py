import pandas as pd
import numpy as np
import os
'''
This script takes as input ABIDE1_2 consistent combined table,
ABIDE1_Review_consistent_links table and ABIDE2_Review_consistent_links table
and compares the links and for each of the link in the above 3  files
finds the replication score. i.e. for each link A-B add the columns for each
presence - ABIDE1, ABIDE2 and Review.

HOWTO:

in_file1 = ABIDE_1_2_consistent_links. Read the index 0 and 1
in_file2 = ABIDE1_Review_consistent_links Read the index 0 and 1
in_file3 = ABIDE2_Review_consistent_links Read the index 0 and 1

Create a new Df and append it with the rows of in_file1 and add NA of size of columns
of in_file2 and 3.

Do for both in_file2 and in_file3
    For each of the links (link_2(3)) of in_file2(3)
    Loop through each of the links (link_1) of DF
        if(link_1 == link2)
            Add link2(3) ahead of link1(2)
        else:
            Add link2(3) ahead of link1(2)

'''
csv_input_path = os.path.abspath('../ABIDE2')
df = []

in_file1 = csv_input_path + '/ABIDE1_ABIDE2_Consistent_Combined.csv'
df_1 = pd.read_csv(in_file1, encoding = "ISO-8859-1",  error_bad_lines=False)
columns1 = list(df_1.columns)
columns1[0] = 'Reg1_ABIDE1_2'
df_1 = df_1.values

in_file2 = csv_input_path + '/ABIDE1_Review_Consistent_Combined.csv'
df_2 = pd.read_csv(in_file2, encoding = "ISO-8859-1",  error_bad_lines=False)
columns2 = list(df_2.columns)
columns2[0] = 'Reg1_ABIDE1_Rev'
df_2 = df_2.values

in_file3 = csv_input_path + '/ABIDE2_Review_Consistent_Combined.csv'
df_3 = pd.read_csv(in_file3, encoding = "ISO-8859-1", error_bad_lines=False )
columns3 = list(df_3.columns)
columns3[0] = 'Reg1_ABIDE2_Rev'
df_3 = df_3.values


#  Create a new DF
for row_idx_df_1 in range(df_1.shape[0]):
    base_link_name = [df_1[row_idx_df_1,0], df_1[row_idx_df_1,1]]
    rest_of_the_links = np.concatenate((df_1[row_idx_df_1], [np.nan]*(len(columns2) + len(columns3))), axis=None)
    new_row = np.concatenate((base_link_name, rest_of_the_links), axis=None)
    df.append(new_row)


df = np.array(df)
# Modify Columns 1
columns1 = np.concatenate((['Region1', 'Region2'],columns1),axis=None)
# Calculate replication score
count = 0

slice = np.arange(len(columns1) , len(columns1) + len(columns2))
for row_idx_df_2 in range(df_2.shape[0]):
    found = 0
    for row_idx_df_1 in range(df.shape[0]):
        if (df[row_idx_df_1,0] == df_2[row_idx_df_2,0]) and \
           (df[row_idx_df_1,1] == df_2[row_idx_df_2,1]):
           print('ABIDE I & 2 %s - ABIDE I %s'%(row_idx_df_1 + 2,row_idx_df_2 + 2))
           df[row_idx_df_1, slice] = df_2[row_idx_df_2]
           count = count + 1
           found = 1
    if found == 0:
        base_link_name = np.array([df_2[row_idx_df_2,0], df_2[row_idx_df_2,1]])
        # rest_of_the_links = np.array([np.nan]*(len(columns1) + len(columns2) + len(columns3)))
        # new_row = np.concatenate((base_link_name, rest_of_the_links), axis=None)
        new_row = np.array([np.nan]*(len(columns1) + len(columns2) + len(columns3)),  dtype=object)

        new_row[[0,1]] = base_link_name
        new_row[slice] = df_2[row_idx_df_2]
        # TODO: Append this new entry to the ndarray df
        df = np.append(df, [new_row], axis = 0 )

#  For ABIDE II
slice = np.arange(len(columns1) + len(columns2) , len(columns1) + len(columns2)+ len(columns3))
for row_idx_df_3 in range(df_3.shape[0]):
    found = 0
    for row_idx_df_1 in range(df.shape[0]):
        if (df[row_idx_df_1,0] == df_3[row_idx_df_3,0]) and \
           (df[row_idx_df_1,1] == df_3[row_idx_df_3,1]):
           print('ABIDE I & II %s - ABIDE II %s'%(row_idx_df_1 + 2,row_idx_df_3 + 2))
           df[row_idx_df_1, slice] = df_3[row_idx_df_3]
           count = count + 1
           found = 1
    if found == 0:
        base_link_name = np.array([df_3[row_idx_df_3,0], df_3[row_idx_df_3,1]])
        # rest_of_the_links = np.array([np.nan]*(len(columns1) + len(columns2) + len(columns3)))
        # new_row = np.concatenate((base_link_name, rest_of_the_links), axis=None)

        new_row = np.array([np.nan]*(len(columns1) + len(columns2) + len(columns3)),  dtype=object)
        new_row[[0,1]] = base_link_name
        new_row[slice] = df_3[row_idx_df_3]
        # TODO: Append this new entry to the ndarray df
        df = np.append(df, [new_row], axis = 0 )



# print(df)
concatenated_columns = np.concatenate((np.concatenate((columns1, columns2), axis=None), columns3), axis= None)

print('Replicable links: %s'%count)
out_file_path = 'ABIDE1_ABIDE2_Review_any_two_Consistent_Combined.csv'
new_df = df
new_df = pd.DataFrame(data=new_df, columns=concatenated_columns)
new_df.to_csv(out_file_path,index=False)




'''
Results:

Replicable links: 201

'''
