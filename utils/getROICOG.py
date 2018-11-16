import sys
import os

# Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
utils_path = os.path.abspath("utils")

# Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
sys.path.insert(0, utils_path)


import subprocess
from os.path import join as opj
import nibabel as nib
import numpy as np
from atlasUtility import queryAtlas
from scipy import ndimage
import argparse
import math

# filename = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
# roi = 20


class getROICOG:
    def __init__(self, atlas):
        self.brain_img = nib.load(atlas)
        self.brain_data = self.brain_img.get_data()

    def _pixDim(self):
        """
        Internal Function to nbe used within this script
        Returns the pixel dimension
        """
        if self.brain_img.header['pixdim'][1] == 2:
            pixdim = 2
        elif self.brain_img.header['pixdim'][1] == 1:
            pixdim = 1
        else:
            raise Exception('Unknown Pixel Dimension',
                            self.brain_img.header['pixdim'][1])

        return pixdim

    def _XYZ2MNI(self, CM):
        if self._pixDim() == 1:
            MNI = queryAtlas.XYZ2MNI1mm(list(CM))
        elif self._pixDim() == 2:
            MNI = queryAtlas.XYZ2MNI2mm(list(CM))
        # print("Center of Gravity:", MNI)
        return MNI

    def getCOG(self, roi, hemisphere=None):
        """
        Gives the Representative coordinate of the region

        For a 3D brain atlas:
        ---------------
        Assumption: Region's voxels are denoted by a constant that
        represents the label of that region. The representative coordinate is
        the COG of that region.

        For a 4D brain atlas:
        ---------------
        Representative coordinate is the peak coordinate. If there are multiple
        peak coordinates the representative coordinate is  the one that is
        closest to the centre of gravity of the ROI.
        If this also results in multiple representative coordinates, then the
        coordinate closest to the mid-line is taken.

        Note: Reason for selecting coordinate cosest to midline is just a
        huristic to resolve the multiple coordinates. It can be replaced by any
        other heuristic.

        Disclaimer:
        -----------
        For a 3d Brain atlas (like AAL), this procedure might result in a COG that lies outside the region.
        getAALCOG has the script that using this script and add some code on
        top to take care of this.

        Input: Atlas File 1mm
               ROI number
               hemisphere = L or R (optional)
        Output: list of MNI coordinates representing Centre of gravity
        Usage:
        >>> atlas= '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'
        >>> roi = 20
        >>> print(getCOG(roi))
        [21.48304821150856, -3.779160186625191, -17.954898911353034]
        """

        # brain_img = nib.load(atlas)
        # brain_data = brain_img.get_data()

        if len(self.brain_data.shape) == 3:  # 3D brain file
            roi_mask = np.zeros(self.brain_data.shape)
            roi_mask[np.where(self.brain_data == roi)] = 1
        else:  # 4D Brain File
            roi_mask = np.zeros(tuple(self.brain_data.shape[:3]))
            roi_mask = self.brain_data[:, :, :, roi]

        # import pdb;pdb.set_trace()
        size_x = roi_mask.shape[0]

        if hemisphere == 'L':
            # Set the voxes of the ROI on the right hemisphere to zero
            roi_mask[:math.floor(size_x / 2), :, :] = 0
        elif hemisphere == 'R':
            # Set the voxes of the ROI on the left hemisphere to zero
            roi_mask[math.floor(size_x / 2):, :, :] = 0

        if len(self.brain_data.shape) == 3:  # 3D brain file
            CM = ndimage.measurements.center_of_mass(roi_mask)
            MNI = self._XYZ2MNI(CM)
        else:  # 4D Brain File
            highest_prob_idx = np.where(roi_mask == np.max(roi_mask))
            MNI = []
            peak_list = []
            CM = ndimage.measurements.center_of_mass(roi_mask)
            dist = float(np.inf)
            # The loop finds the peak coordinate closest to the COG
            for i in range(len(highest_prob_idx[0])):
                peak = [highest_prob_idx[0][i], highest_prob_idx[1]
                        [i], highest_prob_idx[2][i]]
                # Find the peak closest to the COG
                current_dist = abs(CM[0] - peak[0]) + \
                    abs(CM[1] - peak[1]) + abs(CM[1] - peak[1])
                if current_dist < dist:
                    if len(peak_list) != 0:
                        peak_list = []
                    peak_list.append(peak)
                    dist = current_dist
                elif current_dist == dist:
                    peak_list.append(peak)
                    dist = current_dist

            # The above 'For loop' might result in miltiple peak coordinates (peak list) having same distance from COG
            # Check which of the peak list has least x coordinate i.e closest to midline (My heuristic) to select one peak
            x = float(np.inf)
            res = []
            for coordinates in peak_list:
                current_x = abs(coordinates[0])
                if current_x < x:
                    res = []
                    res.append(coordinates)
                elif current_x == x:
                    res.append(coordinates)
                else:
                    pass

            # Find the MNI coordinates of the peak coordinates
            MNI = []
            for res_peak in res:
                MNI.append(self._XYZ2MNI(res_peak))

        return MNI


if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--atlas", required=True,
                    help="Path to 1mm Atlas file")
    ap.add_argument("-r", "--roi", required=True,
                    help="ROI number")
    ap.add_argument("-hem", "--hemisphere", required=False,
                    help="Hemisphere")
    args = vars(ap.parse_args())

    atlas = args["atlas"]
    roi = int(args["roi"])

    if "hemisphere" in args:
        hemisphere = args["hemisphere"]

    obj = getROICOG(atlas)
    print(obj.getCOG(roi, hemisphere))
