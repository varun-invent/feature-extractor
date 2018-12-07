import pandas as pd
import numpy as np
import os
'''
Next is:
1. Read the Links in review and extract the XML type names for BN regions.
2. Break each of the region names so that their hemisphere is another column.
3. Consider C as Both L and R while matching links.
4. For each link got here, check how many are replicated.

HOWTO:

in_file1 = Read the review links file
From the 2nd and 4th column extract the name of the region by name.split('_')[1].split(',')[0]
in_file2 = Read the ABIDE BN regions file
Split the 2 region name's columns into 4 columns -
 Two hemisphere columns by getting each hemisphere by name.split('_')[-1]
 And other by name.split('_')[0]

For each of the links (link_2) of in_file2
    Loop through each of the links (link_1) of in_file1
        if(link_1 == link2)
            dict[link_1] = dict[link_1] + 1

'''
csv_input_path = os.path.abspath('../csv_input')
in_file1 = csv_input_path + '/BN_regions_review_links.csv'
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

in_file2 = csv_input_path + '/UC_OC_links_atlas_map_pivot_table.csv'
df_2 = pd.read_csv(in_file2, encoding = "ISO-8859-1", error_bad_lines=False )
columns2 = df_2.columns
df_2 = df_2.values


name_1st_region = df_2[:,0]
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


name_2nd_region = df_2[:,1]
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
replicated_df_hemis_region_seperate = []

count = 0
rep_links_review = []
for row_idx_df_2 in range(df_2.shape[0]):
    for row_idx_df_1 in range(df_1.shape[0]):
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
                if (row_idx_df_2 + 2) not in rep_links_review:
                    print('ABIDE I %s - Review %s'%(row_idx_df_2 + 2,row_idx_df_1 + 2))
                    rep_links_review.append((row_idx_df_2 + 2))
                    new_row_hemis_region_joined = np.concatenate((df_2[row_idx_df_2], df_1[row_idx_df_1]), axis=None)
                    replicated_df_hemis_region_joined.append(new_row_hemis_region_joined)
                    count = count + 1
print('Replicable links: %s'%count)
out_file_path = 'ABIDE_Review_Consistent_Combined.csv'
new_df = np.array(replicated_df_hemis_region_joined)
new_df = pd.DataFrame(data=new_df, columns=np.concatenate((columns2, columns1), axis=None))
new_df.to_csv(out_file_path,index=False)

'''
Results:

Numbers are the row number (Index 1 is the header. Data starts from Index 2 of CSV)
The following shows which row number of ABIDE1 is replicated with which row number of Review.
ABIDE I 3 - Review 683
ABIDE I 18 - Review 33
ABIDE I 20 - Review 700
ABIDE I 21 - Review 190
ABIDE I 38 - Review 1436
ABIDE I 74 - Review 594
ABIDE I 82 - Review 1212
ABIDE I 83 - Review 1216
ABIDE I 84 - Review 1210
ABIDE I 96 - Review 121
ABIDE I 97 - Review 246
ABIDE I 98 - Review 682
ABIDE I 99 - Review 672
ABIDE I 100 - Review 23
ABIDE I 101 - Review 701
ABIDE I 102 - Review 145
ABIDE I 122 - Review 374
ABIDE I 149 - Review 629
ABIDE I 150 - Review 628
ABIDE I 178 - Review 727
ABIDE I 199 - Review 1436
ABIDE I 210 - Review 1440
ABIDE I 238 - Review 1285
ABIDE I 239 - Review 1287
ABIDE I 251 - Review 1286
ABIDE I 285 - Review 659
ABIDE I 286 - Review 659
ABIDE I 287 - Review 18
ABIDE I 288 - Review 210
ABIDE I 289 - Review 662
ABIDE I 303 - Review 1302
ABIDE I 304 - Review 1302
ABIDE I 306 - Review 208
ABIDE I 307 - Review 210
ABIDE I 309 - Review 1307
ABIDE I 396 - Review 594
ABIDE I 397 - Review 595
ABIDE I 398 - Review 595
ABIDE I 399 - Review 596
ABIDE I 431 - Review 1211
ABIDE I 432 - Review 1215
ABIDE I 440 - Review 1208
ABIDE I 441 - Review 1208
ABIDE I 445 - Review 1209
ABIDE I 446 - Review 1209
ABIDE I 447 - Review 1210
ABIDE I 460 - Review 1213
ABIDE I 465 - Review 1214
ABIDE I 487 - Review 33
ABIDE I 494 - Review 86
ABIDE I 501 - Review 89
ABIDE I 503 - Review 90
ABIDE I 504 - Review 2
ABIDE I 513 - Review 223
ABIDE I 516 - Review 679
ABIDE I 523 - Review 680
ABIDE I 525 - Review 139
ABIDE I 537 - Review 144
ABIDE I 538 - Review 4
ABIDE I 539 - Review 13
ABIDE I 540 - Review 161
ABIDE I 542 - Review 199
ABIDE I 543 - Review 180
ABIDE I 624 - Review 373
ABIDE I 638 - Review 1030
ABIDE I 655 - Review 867
ABIDE I 703 - Review 837
ABIDE I 713 - Review 804
ABIDE I 723 - Review 826
ABIDE I 724 - Review 822
ABIDE I 739 - Review 634
ABIDE I 742 - Review 632
ABIDE I 749 - Review 630
ABIDE I 759 - Review 631
ABIDE I 772 - Review 1259
ABIDE I 775 - Review 1257
ABIDE I 905 - Review 1442
ABIDE I 1021 - Review 108
ABIDE I 1026 - Review 130
ABIDE I 1029 - Review 108
ABIDE I 1032 - Review 106
ABIDE I 1034 - Review 130
ABIDE I 1042 - Review 236
ABIDE I 1044 - Review 238
ABIDE I 1048 - Review 227
ABIDE I 1062 - Review 150
ABIDE I 1063 - Review 142
ABIDE I 1092 - Review 1119
ABIDE I 1093 - Review 1120
ABIDE I 1128 - Review 1075
ABIDE I 1149 - Review 1534
ABIDE I 1150 - Review 1537
ABIDE I 1153 - Review 1536
ABIDE I 1186 - Review 1535
ABIDE I 1207 - Review 778
ABIDE I 1225 - Review 1278
Replicable links: 96

These replicated links might contain Links A-B and B-A. These links in the ABIDE analysis
have an important role to play. As the analysis is Seed-voxel and not seed-seed, a symmetric
result is not guranteed. But if we get a symetricity, then that specifies a strong connection between two regions.

Things to experiment:
0.1 How many Links are both A-B and B-A.
Answer: 79 pairs of A-B and B-A i.e 79 links were bidirectional
using file - ABIDE_Review_Consistent_Combined_all_links_duplicate_clustered_others_clustered.csv got using
experiments.py I came to know that out of the 96 replicable links, 52 are single links and 44 are A-B and B-A links
i.e. 22 pairs

Question: Are the above pairs consistent? That is, Is the connectivity of A-B == B-A

After mapping the ABIDE Links to raw BN review links, I got a csv with 139 links. The number increased coz
one ABIDE link might have mapped to multiple raw BN links. This gave me - for every ABIDE link what all links were
reported in the literature and with what type of participants.





1. How many of the replicated links were underconencted, overconnected or inconsistent
2. How many of the replicate links had been replicated multiple times in Review (BN regions + CBLM)
   and how many are first time replicated
3. How many replicated review links are not from ABIDE and how many are?
4. How many links from ABIDE are A-B and B-A that are replicated with review?
5. How many links from ABIDE are A-B and B-A that are not replicated with review?

'''
