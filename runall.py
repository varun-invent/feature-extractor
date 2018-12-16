import os
import numpy as np

step1 = 0
step2 = 1
step3 = 0

'''
1. This will create seperate UC and OC Consistent conenctomes that contains
for each link, a score that specifies in how many preproc pipelines the link occured.
'''
# Set the ABIDE version you want to work on
ABIDE = 1
if step1:
    print("========================Step 1=====================================")
    print("Step 1: This will create seperate UC and OC Consistent conenctomes that contains \
    for each link, a score that specifies in how many preproc pipelines the link occured.")
    cmd = "python3 find_consistent_connectome.py %s"%ABIDE
    print(cmd)
    os.system(cmd)
    print("====================================================================")

#  Output filenames
out_file_OC='ABIDE%s/combined_brain_OC_ABIDE%s.nii.gz'%(ABIDE, ABIDE)
out_file_UC='ABIDE%s/combined_brain_UC_ABIDE%s.nii.gz'%(ABIDE, ABIDE)

'''
2. Map the above created OC and OC files to full brain (BN + CBLM) atlas and create
a CSV file. Use Multiple UC and OC thresholds. (8,8), (10,10) ... (16,16) and
create multiple CSV files.
'''
if step2:
    print("========================Step 2======================================")
    print("2. Map the above created OC and OC files to full brain (BN + CBLM) atlas and create \
    a CSV file. Use Multiple UC and OC thresholds. (8,8), (10,10) ... (16,16) and \
    create multiple CSV files.")
    #  Change the path to link_mapping_to_atlas folder
    os.chdir('link_mapping_to_atlas')
    print('Changed the directory to : ',os.getcwd())
    UC_brain_path = '../' + out_file_UC
    OC_brain_path = '../' + out_file_OC
    out_file_prefix = '../ABIDE%s/map_links_to_atlas/ABIDE%s_links_atlas_map'%(ABIDE, ABIDE)
    cmd = "python3 map_links_to_atlas.py %s %s %s"%(UC_brain_path, OC_brain_path, out_file_prefix)
    os.system(cmd)
    print(cmd)
    os.chdir('..') # Change the directory back to original
    print("====================================================================")

'''
3. Manually create pivot tables for each of the files created above.
Then run the follwing script to find the links common with the links of review
and create a new csv.
'''
if step3:
    print("====================================================================")
    #  Change the path to link_mapping_to_atlas folder
    os.chdir('link_mapping_to_atlas')
    print('Changed the directory to : ',os.getcwd())
    #  Using the same as used in Step 2 TODO: Modify script to pass it as args in Step 2
    # thresh_UC  = np.arange(8,17,2)
    # thresh_OC  = np.arange(8,17,2)
    thresh_UC = [1]
    thresh_OC = [1]

    thresh_UC_OC_list = list(zip(thresh_UC, thresh_OC))

    in_file1 = '../csv_input/BN_regions_review_links.csv'
    for thresh_UC_OC in thresh_UC_OC_list:
        in_file2 ='../ABIDE%s/map_links_to_atlas_pivot_tables/ABIDE%s_links_atlas_map_UC%s_OC%s\ -\ Pivot\ Table\ 1.csv'%(ABIDE,ABIDE,thresh_UC_OC[0],thresh_UC_OC[1])
        out_file_path = '../ABIDE%s/ABIDE%s_review_common_combined/ABIDE%s_review_common_combined_UC%s_OC%s.csv'%(ABIDE,ABIDE,ABIDE,thresh_UC_OC[0],thresh_UC_OC[1])

        cmd = "python3 find_common_links.py %s %s %s"%(in_file1, in_file2, out_file_path)
        print(cmd)
        os.system(cmd)


    os.chdir('..') # Change the directory back to original
    print("====================================================================")

'''
4. For each of the above creatd common file, Calculate the precision and recall
and then calculate the F-score.

Precision:
---------
a = Count of all the ABIDE links that have atleast one end point in review BN regions
b = Count of all the ABIDE links that were consistent (Not just common) with the review BN regions

Note: A replicated ABIDE link is consistent by default if the review link is inconsistent
precision (p) = b/a

Recall:
--------

c = Count of All the consistent replicated BN region links = b
d = Count of total BN review links

Note: A replicated ABIDE link is consistent by default if the review link is inconsistent

recall (r) = c/d (or) b/d

F-Score
------

f = 1 / ( (1/p) + (1/r) )

'''
