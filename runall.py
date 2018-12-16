import subprocess
import os

step1 = 0
step2 = 1

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
    print("====================================================================")
