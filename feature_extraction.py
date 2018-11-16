#!/usr/bin/env python

# import sys
# import os
#
# # Using https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python
# utils_path = os.path.abspath("utils")
#
# # Using https://askubuntu.com/questions/470982/how-to-add-a-python-module-to-syspath/471168
# sys.path.insert(0, utils_path)


import numpy as np
from scipy.ndimage.measurements import label as lb
from scipy.ndimage.measurements import center_of_mass as com
import nibabel as nib
# from utils import getROICOG
from utils import atlasUtility as au
import argparse
import pandas as pd
from collections import OrderedDict

class feature_extractor:
    """
    This tool will take as input the brain map - a 3D file and an atlas name.
    User can set a threshold for example <1.3>
        Program finds clusters.
        For each cluster:
            Finds the span of cluster
            Check how many ROIs are covered by the cluster.
            For each ROI covered
            Find the number and percentage of voxels it covers and reports the
                      peak coordinate closest to COG of the voxels in that ROI.
            Also gives the name and coordinates of the peak coordinate of the
                                                                       cluster.

    """
    def __init__(self, contrast, atlas_dict, threshold, volume = 0):
        # Read Brain file:
        self.brain_img = nib.load(contrast)
        self.brain = self.brain_img.get_data()
        self.brain[np.isnan(self.brain)] = 0

        self.atlas_dict = atlas_dict
        # Read Atlas file
        self.atlas = nib.load(atlas_dict['atlas_path'][0]).get_data()

        self.thresh = threshold

        self.volume = volume

        #  List to store all the dictionaries belonging to each feature
        self.feature_dict_list = []

    def getNearestVoxel(self, roi_mask, COG):
        """
        Input:
        -----
        roi_mask - This is the brain 3D tensor in which the voxels
        belonging to some predefined region has non zero value and rest of the
        voxels has zero value.

        COG: It is a list or tuple of 3 cartesian coordinates (x, y, z)
        representing the COG.

        Output:
        ------
        The function returns the cartesian coordinates of the coordinate in the
        non zero region of roi_mask that is closest to the COG

        """

        roiCoord = np.where(roi_mask != 0)

        peak_list = []
        dist = float(np.inf)
        for [x, y, z] in zip(roiCoord[0], roiCoord[1], roiCoord[2]):
            peak = [x, y, z]
            current_dist = abs(x - COG[0]) + abs(y - COG[1]) + abs(z - COG[2])
            if current_dist < dist:
                if len(peak_list) != 0:
                    peak_list = []
                peak_list.append(peak)
                dist = current_dist
            elif current_dist == dist:
                peak_list.append(peak)
                dist = current_dist

        # The above 'For loop' might result in miltiple peak coordinates(peak list)
        # having same distance from COG Check which of the peak list has least
        # x coordinate i.e closest to midline (My heuristic) to select one peak

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

        # # Find the MNI coordinates of the peak coordinates
        # MNI = []
        # for res_peak in res:
        #     MNI.append(queryAtlas.XYZ2MNI2mm(res_peak))
        #
        # return MNI

        if len(res) > 1:
            raise Exception('Multiple candidates for Representative \
            coordinates. Please report to the author of the tool about this!')

        return res[0]

    def _pixDim(self):
        """
        Internal Function to be used within this script
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
            MNI = au.queryAtlas.XYZ2MNI1mm(list(CM))
        elif self._pixDim() == 2:
            MNI = au.queryAtlas.XYZ2MNI2mm(list(CM))
        # print("Center of Gravity:", MNI)
        return MNI

    def extract(self, volume = None, threshold = None):
        # To take care if user has given a 4D contrast
        if volume != None:
            self.volume = volume

        if len(self.brain.shape) > 3:
            brain = np.array(self.brain[:,:,:,self.volume])
        else:
            brain = np.array(self.brain)

        if threshold != None:
            self.thresh = threshold

        # Total number of brain voxels
        num_brain_voxels = len(np.where(brain != 0)[0])


        """
        Brain_zero is used later to calculate the center of gravity of the
        cluster voxels overlapping with atlas voxels
        """

        brain_zero = np.zeros(brain.shape)

        # Apply thresholding
        brain[(brain < self.thresh) & (brain > -self.thresh)] = 0

        # Find clusters
        clusters, num_clusters = lb(brain)

        print('######### Num of clusters: ',num_clusters)
        df_report = pd.DataFrame()

        # List to store cluster size information
        full_cluster_voxels_percentage_list = []

        # c. Report the name of the region

        atlas_path = self.atlas_dict['atlas_path']
        atlas_labels_path = self.atlas_dict['atlas_labels_path']
        atlas_xml_zero_start_index = \
                           self.atlas_dict['atlas_xml_zero_start_index']

        aal_atlas_obj = au.queryAtlas(atlas_path, atlas_labels_path,
                  atlas_xml_zero_start_index=atlas_xml_zero_start_index)


        for cluster_number in range(1,num_clusters + 1):
            # Coordinates that are present in cluster given by cluster_number
            cluster_indices = np.where(clusters == cluster_number)

            # Number of voxels belonging to the cluster -> cluster_number
            num_cluster_voxels = len(cluster_indices[0])

            # Percentage of total brain voxels in a cluster
            full_cluster_voxels_percentage = \
                                    num_cluster_voxels * 100 / num_brain_voxels

            # To create a list to be added to dataframe
            full_cluster_voxels_percentage_list.append(
                                                full_cluster_voxels_percentage)

            # Find the atlas labels/regions that the cluster spans
            atlas_regions_labels = np.unique(self.atlas[cluster_indices])
            # print(atlas_regions_labels)

            # iterate over all the labes/regions
            for label in atlas_regions_labels:
                # Lists to be used for dataFrame creation
                cog_value_list = []
                number_overlapping_cluster_voxels_list = []
                overlapping_cluster_voxels_percentage_list = []
                MNI_cog_list = []
                cog_region_name_list = []

                cog_unweighted_value_list = []
                cog_weighted_value_list = []
                cog_weighted_value_list = []
                MNI_cog_unweighted_list = []
                MNI_cog_weighted_list = []
                cog_region_name_weighted_list = []
                cog_region_name_unweighted_list   = []


                # Find all the coordinates of the labels

                # Skipping the Label 0
                if label == 0:
                    continue

                atlas_label_indices = np.where(self.atlas == label)

                """ Find the cluster coordinates overlapping the label/region
                under consideration """

                # Changing the form of cluster indices to (x,y,z) tuple

                cluster_indices_zip = zip(cluster_indices[0], cluster_indices[1]
                                      , cluster_indices[2])

                cluster_indices_tuple_list = list(cluster_indices_zip)

                # Changing the form of atlas indices to (x,y,z) tuple

                atlas_label_indices_zip = \
                zip(atlas_label_indices[0], atlas_label_indices[1],
                                            atlas_label_indices[2])



                atlas_label_indices_tuple_list = list(atlas_label_indices_zip)

                # Number of voxels belonging to the atlas region
                num_atlas_region_voxels = len(atlas_label_indices_tuple_list)

                # 1. Find intersecion of the above two lists
                overlapping_coordinates = \
                list(set(cluster_indices_tuple_list).intersection(
                                           set(atlas_label_indices_tuple_list)))

                """
                2. Make an brain array and initialize the overlapping
                coordinates with the values from brain

                # Transform coordinates list to list of indices as
                returned by np.where()
                # Ref: https://stackoverflow.com/questions/12974474/
                how-to-unzip-a-list-of-tuples-into-individual-lists

                """
                overlapping_indices_zip =  zip(*overlapping_coordinates)

                overlapping_indices_tuple_list = list(overlapping_indices_zip)
                #
                # # Number of voxels in the overlap of cluster and atlas region
                # number_overlapping_cluster_voxels = \
                #                             len(overlapping_coordinates)
                #
                # # Creating list to be added to dataframe
                # number_overlapping_cluster_voxels_list.append(
                #                               number_overlapping_cluster_voxels)
                #
                # #Percentage of voxels in the overlap of cluster and atlas region
                # overlapping_cluster_voxels_percentage = \
                # number_overlapping_cluster_voxels*100 / num_atlas_region_voxels
                #
                # # Creating list to be added to dataframe
                # overlapping_cluster_voxels_percentage_list.append(
                #                           overlapping_cluster_voxels_percentage)
                #
                # # Assigning the overlap to the empty brain to find COG later
                # brain_zero[overlapping_indices_tuple_list] = \
                #                            brain[overlapping_indices_tuple_list]
                #
                # """
                # 3. Then use the already created functions to do the following:
                #     a. Find the representative coordinate of the intersection
                #
                # Create a dummy atlas (roi_mask) with just one region and label
                # that as 1
                #
                # Ref: https://stackoverflow.com/questions/32322281/
                # numpy-matrix-binarization-using-only-one-expression
                # """
                #
                # roi_mask_for_unweighted_cog = np.where(brain_zero != 0, 1, 0)
                # roi_mask_for_weighted_cog = brain_zero
                #
                #
                # cog_unweighted = com(roi_mask_for_unweighted_cog)
                # cog_weighted = com(roi_mask_for_weighted_cog)
                #
                # # convert the coordinates to int (math.floor)
                # cog_unweighted = tuple(map(int, cog_unweighted))
                # cog_weighted = tuple(map(int, cog_weighted))
                #
                # """
                # If the COG lies outside the overlapping coordinates then find
                # the coordinate that lies on the overlapping region and is
                # closest to the COG.
                # """
                #
                # if not roi_mask_for_unweighted_cog[cog_unweighted]:
                #     cog_unweighted = \
                #               tuple(self.getNearestVoxel(roi_mask_for_unweighted_cog,
                #                                    cog_unweighted))
                #
                # if not roi_mask_for_weighted_cog[cog_weighted]:
                #     cog_weighted= \
                #               tuple(self.getNearestVoxel(roi_mask_for_weighted_cog,
                #                                    cog_weighted))
                #
                # print('COM Unweighted', cog_unweighted)
                # print('COM Weighted', cog_weighted)
                #
                # # Finding the values at the cluster representative coordinates
                # cog_unweighted_value = brain[cog_unweighted]
                # cog_weighted_value = brain[cog_weighted]
                #
                # # Lists to be added to dataframe
                # cog_unweighted_value_list.append(cog_unweighted_value)
                # cog_weighted_value_list.append(cog_weighted_value)
                #
                # # b. Convert the cartesian coordinates to MNI
                # MNI_cog_unweighted = self._XYZ2MNI(cog_unweighted)
                # MNI_cog_weighted = self._XYZ2MNI(cog_weighted)
                #
                # # Convert the list of coordinates to string to get rid of:
                # # Exception: Data must be 1-dimensional
                #
                #
                # str_cog_unweighted = ''
                # for i in MNI_cog_unweighted:
                #     str_cog_unweighted = str_cog_unweighted + ' ' + str(i)
                #
                # str_cog_weighted = ''
                # for i in MNI_cog_weighted:
                #     str_cog_weighted = str_cog_weighted + ' ' + str(i)
                #
                #
                #
                # # Lists to be added to dataframe
                # MNI_cog_unweighted_list.append(str_cog_unweighted)
                # MNI_cog_weighted_list.append(str_cog_weighted)
                #
                #
                # # c. Report the name of the region
                #
                #
                #
                # # Names of the regions of COG
                # cog_region_name_weighted = \
                #               aal_atlas_obj.getAtlasRegions(MNI_cog_weighted)[1]
                # cog_region_name_unweighted = \
                #             aal_atlas_obj.getAtlasRegions(MNI_cog_unweighted)[1]
                #
                # print('Region name weighted COG: ',cog_region_name_weighted)
                #
                # print('Region name unweighter COG: ',cog_region_name_unweighted)
                #
                # # List created to be added to dataframe
                # cog_region_name_weighted_list.append(cog_region_name_weighted)
                # cog_region_name_unweighted_list.append(cog_region_name_unweighted)
                #
                # #  To choose from weighted and unweighted COG options
                # WEIGHTED = True
                #
                # if WEIGHTED:
                #     MNI_cog_list = MNI_cog_weighted_list
                #     cog_region_name_list = cog_region_name_weighted_list
                #     cog_value_list = cog_weighted_value_list
                # else:
                #     pass
                #
                # # Sort the Regions bsed on cog value
                #
                # # Get the indices of elements after they are sorted
                # sorted_indices = np.argsort(cog_value_list)
                #
                # #  Sort the lists according to the above sorted_indices
                # cog_value_list = np.array(cog_value_list)[sorted_indices]
                # number_overlapping_cluster_voxels_list = \
                # np.array(number_overlapping_cluster_voxels_list)[sorted_indices]
                #
                # overlapping_cluster_voxels_percentage_list = \
                # np.array(overlapping_cluster_voxels_percentage_list)[sorted_indices]
                #
                # MNI_cog_list = np.array(MNI_cog_list)[sorted_indices]
                # cog_region_name_list = np.array(cog_region_name_list)[sorted_indices]


                """
                TODO:
                Convert MNI coordinates from list to string (x,y,z)
                The next error that I will have to deal with is unequal length
                arrays. For that append each list with spaces.
                Then care about ordering the dictionary.
                """
                # Creating a dictionary to create dataframe
                df_dict = OrderedDict()
                df_dict['ROI Index'] = [self.volume]
                df_dict['Cluster Number'] = [cluster_number]
                df_dict['Cluster Label'] = [label]
                #
                # df_dict['Max Value'] = cog_value_list
                # df_dict['Num Voxels'] = number_overlapping_cluster_voxels_list
                # df_dict['Percentage of Voxel' ] = \
                #                      overlapping_cluster_voxels_percentage_list
                # df_dict['MNI Coordinates'] = MNI_cog_list
                # df_dict['Region Name'] = cog_region_name_list
                df_dict['overlapping_indices_tuple_list'] = overlapping_indices_tuple_list

                self.feature_dict_list.append(df_dict)

                # df = pd.DataFrame(df_dict)
                #
                # df_report = df_report.append(df)

                # Empty the lists to be filled again
                cog_value_list = []
                number_overlapping_cluster_voxels_list = []
                overlapping_cluster_voxels_percentage_list = []
                MNI_cog_list = []
                cog_region_name_list = []

        #
        #         """
        #         TODO:
        #         The order of the columns is not maintained
        #         Test again about the validity of results. The number of voxels
        #         is very low. Check it!
        #
        #         DONE:
        #         Store each of the coordinates in cog_list, names in
        #         name_list, values in value_list, number of voxels etc.
        #         Find the max of the value_list and corresponding name in
        #         name_list and also calculate other details and store them in
        #         lists.
        #
        #         Create a distionary with all the above created lists.
        #
        #         Create a empty data frame and add the above created dictionary
        #         in it.
        #
        #         ATLAS NAME
        #         SIZE (MM)
        #
        #         In one For loop create the details about cluster1 and store them
        #         in lists as said above. As said above, add these lists in a
        #         dictionary.
        #         Then this dictionary is added to a dataframe.
        #
        #         The table should look like the following:
        #
        #         ROI1 Cluster1 MaxValue COG Region Total_#_voxels %_voxels
        #                       MaxValue COG Region #_voxels %_voxles_overlap
        #                       Value2   COG Region #_voxels %_voxles_overlap
        #                       Value3   COG Region #_voxels %_voxles_overlap
        #                       .        .
        #                       .        .
        #                       .        .
        #              Cluster2 MaxValue COG Region Total_#_voxels
        #                        MaxValue COG Region #_voxels %_voxles_overlap
        #                        Value2   COG Region #_voxels %_voxles_overlap
        #                        Value3   COG Region #_voxels %_voxles_overlap
        #                        .        .
        #                        .        .
        #                        .        .
        #
        #         """
        #
        #
        #
        #         pass
        #
        #         brain_zero.fill(0)
        #
        #             # d. Number and Percentage of voxels overlapping the region
        #             # e. Peak coordinate of the cluster
        # df_report.to_csv('ClusterReport.csv', index = False)
        # # TODO Test the function
    def get_feature_dict_list(self):
        return self.feature_dict_list

if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--contrast", required=False,
                    help="Path to contrast file")
    ap.add_argument("-a", "--atlas", required=False,
                    help="Path to Atlas file")
    ap.add_argument("-t", "--thresh", required=False,
                    help="Threshold")
    ap.add_argument("-v", "--vol", required=False,
                    help="Total number of volumes")


    args = vars(ap.parse_args())



    base_path = '/home/varun/Projects/fmri/feature_extractor/'


    if args["contrast"] != None:
        contrast = args["contrast"]
    else:
        contrast = '/media/varun/LENOVO5/BackupDhyanam/fdr_and_results/' + \
        'motionRegress1filt1global0smoothing1_eyes_closed/map_logp.nii.gz'
        contrast = 'map_logq_2mm.nii.gz'
    print('Using contrast %s' % contrast)

    if args["atlas"] != None:
        atlas = args["atlas"]
    else:
        # atlas = '/home/varun/Projects/fmri/' + \
        # 'Autism-survey-connectivity-links-analysis/aalAtlas/AAL.nii.gz'
        atlas = 'AAL'
    print("Using atlas %s" % atlas)

    if args["thresh"] != None:
        threshold = float(args["thresh"])
    else:
        threshold = 1.3

    print("Using threshold of %s" % threshold)

    if args["vol"] != None:
        volume = int(args["vol"])
    else:
        volume = 0

    print("Using Volume_index %s" % str(volume))


    if atlas == 'AAL':
        atlas_path = [base_path + 'aalAtlas/AAL.nii.gz']
        atlas_labels_path = [base_path + 'aalAtlas/AAL.xml']
        atlas_xml_zero_start_index  =  False
    elif atlas == 'fb':
        atlas_path = [base_path +
        'Full_brain_atlas_thr0-2mm/fullbrain_atlas_thr0-2mm.nii.gz']
        atlas_labels_path = [base_path +
        'Full_brain_atlas_thr0-2mm/fullbrain_atlas.xml']
        atlas_xml_zero_start_index  =  True

    atlas_dict = {
    'atlas_path': atlas_path,
    'atlas_labels_path': atlas_labels_path,
    'atlas_xml_zero_start_index': atlas_xml_zero_start_index
    }


    crl_obj = feature_extractor(contrast, atlas_dict, threshold)

    if volume > 0:
        for i in range(volume):
            crl_obj.extract(volume=i)
    else:
        crl_obj.extract(volume=0)

    get_feature_dict_list = crl_obj.get_feature_dict_list()
