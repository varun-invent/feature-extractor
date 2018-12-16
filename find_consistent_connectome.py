import glob
import pandas as pd
import numpy as np
import merge_csv as mc
import nibabel as nib
import sys
'''
1. Load all the 16 brain in memory. Threshold the 16 brains.
2. Create a result brain
3. Iterate through all the 16 brains and then create new brain which contains links,
with value of each link being the number of perprocessing pipelines it was present in.
'''


def find_consistent_links(brain_list_OC, brain_list_UC):
    combined_brain_OC = np.zeros(brain_list_OC[0].shape)
    combined_brain_UC = np.zeros(brain_list_UC[0].shape)

    for brain_OC, brain_UC in zip(brain_list_OC, brain_list_UC) :
        combined_brain_OC = combined_brain_OC + brain_OC
        combined_brain_UC = combined_brain_UC + brain_UC

    return combined_brain_OC, combined_brain_UC

def merge_brains(csv_path_regex, brain_path_regex, threshold,\
                out_file_OC, out_file_UC):
    opt_list = []
    brain_list_OC = []
    brain_list_UC = []

    combined_df = pd.DataFrame()

    for csv_filename,brain_filename in zip(glob.iglob(csv_path_regex, recursive=True),\
                        glob.iglob(brain_path_regex, recursive=True)):
        opt = csv_filename.split('/')[-1].split('_')[-1].split('.')[0]
        print('Option: ', opt)
        opt_list.append(opt)
        print('Brain Filename:', brain_filename)
        brain_img = nib.load(brain_filename)
        brain = brain_img.get_data()
        brain[np.isnan(brain)] = 0
        # brain[np.abs(brain) < threshold] = 0

        # Overconnectivity links
        brain_OC = np.zeros(brain.shape)
        brain_OC[brain >= threshold] = 1

        # Underconnectivity links
        brain_UC = np.zeros(brain.shape)
        brain_UC[brain <= -threshold] = -1

        brain_list_OC.append(np.array(brain_OC))
        brain_list_UC.append(np.array(brain_UC))

    combined_brain_OC, combined_brain_UC = find_consistent_links(brain_list_OC,brain_list_UC)

    brain_OC_with_header = nib.Nifti1Image(combined_brain_OC, affine=brain_img.affine,header = brain_img.header)
    nib.save(brain_OC_with_header,out_file_OC)

    brain_UC_with_header = nib.Nifti1Image(combined_brain_UC, affine=brain_img.affine,header = brain_img.header)
    nib.save(brain_UC_with_header,out_file_UC)

    # import pdb;pdb.set_trace()


if __name__ == "__main__":
    try:
        ABIDE = int(sys.argv[1])
    except:
        print('Usage python3 <script_name> <1 or 2>')

    print('Computing ABIDE %s UC and OC maps'%ABIDE)

    if ABIDE == 1:
        csv_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE1_4/fdrRes/**/*.csv"
        brain_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE1_4/fdrRes/**/**/map_logq.nii.gz"
    elif ABIDE == 2:
        csv_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/*.csv"
        brain_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE2_1/fdrRes/**/**/map_logq.nii.gz"
    else:
        raise Exception('Wrong ABIDE flag')

    print('Reading the following directories regex: ' )
    print(csv_path_regex)
    print(brain_path_regex)


    # csv_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/calc_residual1smoothing1filt1calc_residual_optionsconst/*.csv"
    # brain_path_regex = "/home/varun/Projects/fmri/feature_extractor/data/calc_residual1smoothing1filt1calc_residual_optionsconst/**/map_logq.nii.gz"



    threshold = 1.3
    out_file_OC='ABIDE%s/combined_brain_OC_ABIDE%s.nii.gz'%(ABIDE, ABIDE)
    out_file_UC='ABIDE%s/combined_brain_UC_ABIDE%s.nii.gz'%(ABIDE, ABIDE)

    merge_brains(csv_path_regex, brain_path_regex, threshold,out_file_OC,out_file_UC)

    print('Output Files')
    print(out_file_OC)
    print(out_file_UC)
