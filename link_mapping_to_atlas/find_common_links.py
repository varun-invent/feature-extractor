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
df_1 = pd.read_csv(in_file1, encoding = "ISO-8859-1",  error_bad_lines=False).values

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

in_file2 = csv_input_path + '/UC_OC_links_atlas_map.csv'
df_2 = pd.read_csv(in_file2, encoding = "ISO-8859-1", error_bad_lines=False ).values


name_1st_region = df_2[:,5]
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


name_2nd_region = df_2[:,7]
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
                if (row_idx_df_1 + 2) not in rep_links_review:
                    print('ABIDE I %s - Review %s'%(row_idx_df_2 + 2,row_idx_df_1 + 2))
                    rep_links_review.append((row_idx_df_1 + 2))
                    count = count + 1
print('Replicable links: %s'%count)

'''
Results:

Numbers are the row number (Index 1 is the header. Data starts from Index 2 of CSV)
The following shows which row number of ABIDE1 is replicated with which row number of Review.
ABIDE I 3 - Review 1213
ABIDE I 12 - Review 1214
ABIDE I 16 - Review 631
ABIDE I 40 - Review 246
ABIDE I 81 - Review 634
ABIDE I 112 - Review 19
ABIDE I 112 - Review 672
ABIDE I 113 - Review 1317
ABIDE I 116 - Review 89
ABIDE I 132 - Review 629
ABIDE I 133 - Review 1114
ABIDE I 140 - Review 703
ABIDE I 141 - Review 1324
ABIDE I 144 - Review 121
ABIDE I 205 - Review 358
ABIDE I 206 - Review 1002
ABIDE I 245 - Review 632
ABIDE I 269 - Review 98
ABIDE I 393 - Review 679
ABIDE I 395 - Review 52
ABIDE I 396 - Review 86
ABIDE I 452 - Review 826
ABIDE I 458 - Review 139
ABIDE I 460 - Review 185
ABIDE I 464 - Review 700
ABIDE I 465 - Review 1323
ABIDE I 482 - Review 69
ABIDE I 488 - Review 1308
ABIDE I 491 - Review 664
ABIDE I 492 - Review 804
ABIDE I 524 - Review 680
ABIDE I 532 - Review 1440
ABIDE I 535 - Review 662
ABIDE I 538 - Review 1286
ABIDE I 540 - Review 822
ABIDE I 552 - Review 485
ABIDE I 567 - Review 701
ABIDE I 587 - Review 504
ABIDE I 720 - Review 837
ABIDE I 738 - Review 556
ABIDE I 767 - Review 1446
ABIDE I 889 - Review 374
ABIDE I 900 - Review 1259
ABIDE I 901 - Review 1212
ABIDE I 907 - Review 208
ABIDE I 907 - Review 1305
ABIDE I 910 - Review 683
ABIDE I 911 - Review 44
ABIDE I 915 - Review 1436
ABIDE I 918 - Review 779
ABIDE I 918 - Review 782
ABIDE I 919 - Review 656
ABIDE I 923 - Review 596
ABIDE I 924 - Review 630
ABIDE I 940 - Review 733
ABIDE I 951 - Review 1209
ABIDE I 966 - Review 595
ABIDE I 970 - Review 1302
ABIDE I 971 - Review 659
ABIDE I 976 - Review 13
ABIDE I 978 - Review 233
ABIDE I 978 - Review 670
ABIDE I 998 - Review 4
ABIDE I 1017 - Review 1096
ABIDE I 1018 - Review 1518
ABIDE I 1020 - Review 1332
ABIDE I 1021 - Review 671
ABIDE I 1023 - Review 345
ABIDE I 1025 - Review 2
ABIDE I 1032 - Review 343
ABIDE I 1033 - Review 33
ABIDE I 1117 - Review 1203
ABIDE I 1336 - Review 1535
ABIDE I 1361 - Review 238
ABIDE I 1361 - Review 696
ABIDE I 1362 - Review 108
ABIDE I 1371 - Review 1120
ABIDE I 1371 - Review 1124
ABIDE I 1374 - Review 1090
ABIDE I 1382 - Review 828
ABIDE I 1389 - Review 258
ABIDE I 1402 - Review 1119
ABIDE I 1408 - Review 1412
ABIDE I 1418 - Review 1048
ABIDE I 1426 - Review 548
ABIDE I 1428 - Review 315
ABIDE I 1434 - Review 1420
ABIDE I 1473 - Review 1352
ABIDE I 1491 - Review 741
ABIDE I 1502 - Review 858
ABIDE I 1512 - Review 778

I was able to replicate 91 links
These replicated links might contain Links A-B and B-A. These links in the ABIDE analysis
have an important role to play. As the analysis is Seed-voxel and not seed-seed, a symmetric
result is not guranteed. But if we get a symetricity, then that specifies a strong connection between two regions.

Things to experiment:
0.1 How many Links are both A-B and B-A.
Answer: 79 pairs of A-B and B-A i.e 79 links were bidirectional
Question: Are the above pairs consistent? That is, Is the connectivity of A-B == B-A

1. How many of the replicated links were underconencted, overconnected or inconsistent
2. How many of the replicate links had been replicated multiple times in Review (BN regions + CBLM)
   and how many are first time replicated
3. How many replicated review links are not from ABIDE and how many are?
4. How many links from ABIDE are A-B and B-A that are replicated with review?
5. How many links from ABIDE are A-B and B-A that are not replicated with review?

'''
