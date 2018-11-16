import sys
import os

# Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
utils_path = os.path.abspath("utils")

# Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
sys.path.insert(0, utils_path)

import brainnetomeUtility as bu
import numpy as np
import nibabel as nib
import argparse
from tqdm import tqdm

"""
Argparse learnt from https://www.pyimagesearch.com/2018/03/12/python-argparse-command-line-arguments/
"""
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
	help="path to Brainnetome atlas")
# ap.add_argument("-o", "--output", required=True,
# 	help="path to output image")
args = vars(ap.parse_args())

# load the input image from disk
brain_image = nib.load(args["input"])
brain_data = brain_image.get_data()

# create the object of brainnetome atlas
atlas_path = os.path.abspath('brainnetomeAtlas/BNA-maxprob-thr0-1mm.nii.gz')
# atlasRegionsDescrpPath = '/home/varun/Projects/fmri/Autism-Connectome-Analysis-brain_connectivity/atlas/BNA_subregions.xlsx'
atlasRegionsDescrpPath = os.path.abspath('brainnetomeAtlas/BNA_subregions_machineReadable.xlsx')
q = bu.queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath, False)
mask = np.zeros(brain_data.shape)
mask[np.where(brain_data != 0)] = 1
# import pdb; pdb.set_trace()

x,y,z = brain_data.shape
inconsistent_roi = []
for i in tqdm(range(x)):
    for j in range(y):
        for k in range(z):
            if mask[i,j,k] == 1:
                print('X: %s, Y: %s, Z: %s'%(i,j,k))
                [mni_x, mni_y, mni_z] = q.XYZ2MNI1mm([i,j,k])
                roiNumber,lobe, gyrus, roiName = q.getAtlasRegions([mni_x, mni_y, mni_z])
                if roiNumber != 0:
                    if mni_x > 0 and float(roiNumber)%2.0 != 0 : # mni is positive and roi number is odd
                        print('Inconsistency found at ROI number %s and mni_x %s'%(roiNumber, mni_x))
                        inconsistent_roi.append(roiNumber)
                    elif mni_x < 0 and float(roiNumber)%2.0 == 0 :
                        print('Inconsistency found at ROI number %s and mni_x %s'%(roiNumber,mni_x))
                        inconsistent_roi.append(roiNumber)

print('Inconsistent ROIs ',inconsistent_roi)
