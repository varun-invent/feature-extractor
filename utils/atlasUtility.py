# coding: utf-8

import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm
import argparse



# In[66]:


# Improved
class queryAtlas:
    '''
    atlasPaths : List of paths to the nii files to be considered in order of preference
    atlasLabelsPaths : List of paths to the xml files containing labels to be considered in order of preference
    coord : List [x,y,z] of MNI coordinates
    Usage:
    >>> atlasPaths1  = ['hoAtlas/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz',\
               'hoAtlas/HarvardOxford-sub-maxprob-thr25-2mm.nii.gz',
               'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz']
    >>> atlasLabelsPaths1 = ['hoAtlas/HarvardOxford-Cortical.xml','hoAtlas/HarvardOxford-Subcortical.xml',\
                    'cerebellumAtlas/Cerebellum_MNIflirt.xml']
    >>> q1 = queryAtlas(atlasPaths1, atlasLabelsPaths1)
    >>> q1.getAtlasRegions([-6,62,-2])
    (1, 'Frontal Pole', 0)

    Also, this function supports the use of 4D probability map of the atlas to find the nearby
    maximim probability region in the vicinity of 3 voxel cube if the region at a particular voxel is not
    present in the atlas.
    Just provide a 4D nii.gz file path as atlas_path

    To include the HO_subcortical atlas's WM or Cerebral cortex regions
    in the region prediction set WM_HEMISPHERE_INFO=True while initializing the
    class object:
    >>> q1 = queryAtlas(atlasPaths1, atlasLabelsPaths1, True)




    '''
    def __init__(self,atlasPaths,atlasLabelsPaths,WM_HEMISPHERE_INFO=False,atlas_xml_zero_start_index=True):
        self.atlasPaths = atlasPaths
        self.atlasLabelsPaths = atlasLabelsPaths
        self.itr = [0,1,-1,2,-2,3,-3] # represents the neighbourhood to search the queryVoxel
        self.atlas_list = []
        self.pixdim_list = []
        self.WM_HEMISPHERE_INFO = WM_HEMISPHERE_INFO

        """ When the atlas labels xml file contains index starting from zero and
        increasing then this flag is set to True otherwise False. This is
        useful while creating the atlas region name dictionary in roiName().
        In the atlas provided in FSL such as Harvard oxford and cerebellum atlas
        , the index starts from zero and in incremented for each region whereas
        in AAL atlas, the index is same as label in Atlas
        """
        self.ATLAS_XML_ZERO_START_INDEX = atlas_xml_zero_start_index

        for index,atlasPath in enumerate(self.atlasPaths):

            _atlas = nib.load(atlasPath)
            atlas = _atlas.get_data()

            self.atlas_list.append(atlas)

            """
            Following Code to set the prob variable to True if user has
            entered probability maps and False if fixed labeled atlas is entered
            TODO Raise Exception if all the atlases do not have common dimensions.
            """
            atlas_shape_len = len(atlas.shape)
            if atlas_shape_len == 4:
                self.prob = True
            elif atlas_shape_len == 3:
                self.prob = False
            else:
                print('Exception: Atlas of unknown shape')
                raise Exception('Exception: Atlas of unknown shape. Exiting!')


            print('Atlas read')
            if _atlas.header['pixdim'][1] == 3:
                pixdim = 3
            elif _atlas.header['pixdim'][1] == 2:
                pixdim = 2
            elif _atlas.header['pixdim'][1] == 1:
                pixdim = 1
            else:
                print('Unknown Pixel Dimension', _atlas.header['pixdim'][1])
                raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )

            self.pixdim_list.append(pixdim)
            print('checked Pixel dimension')


    @staticmethod
    def MNI2XYZ1mm(mni):
        """
        Converts the given MNI coordinates to X,Y,Z cartesian coordinates corresponding to the 1mm atlas
        """
        x =  - mni[0] + 90
        y = mni[1] + 126
        z = mni[2] + 72
        return [x,y,z]

    @staticmethod
    def MNI2XYZ2mm(mni):
        """
        Converts the given MNI coordinates to X,Y,Z cartesian coordinates corresponding to the 2mm atlas
        """
        x =  math.floor((- mni[0] + 90)/2.0)
        y = math.floor((mni[1] + 126)/2.0)
        z = math.floor((mni[2] + 72)/2.0)
        return [x,y,z]

    @staticmethod
    def MNI2XYZ3mm(mni):
        """
        Converts the given MNI coordinates to X,Y,Z cartesian coordinates corresponding to the 2mm atlas
        """
        x =  math.floor((- mni[0] + 90)/3.0)
        y = math.floor((mni[1] + 126)/3.0)
        z = math.floor((mni[2] + 72)/3.0)
        return [x,y,z]

    @staticmethod
    def XYZ2MNI1mm(xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 1mm atlas
        """
        mni_x = - xyz[0] + 90
        mni_y = xyz[1] - 126
        mni_z = xyz[2] -72
        return [mni_x, mni_y, mni_z]


    @staticmethod
    def XYZ2MNI2mm(xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 2mm atlas
        """
        mni_x = - 2*xyz[0] + 90
        mni_y = 2*xyz[1] - 126
        mni_z = 2*xyz[2] -72
        return [mni_x, mni_y, mni_z]
    @staticmethod

    def XYZ2MNI3mm(xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 2mm atlas
        """
        mni_x = - 3*xyz[0] + 90
        mni_y = 3*xyz[1] - 126
        mni_z = 3*xyz[2] -72
        return [mni_x, mni_y, mni_z]

    def roiName(self, atlasLabelsPath, roiNum):
        '''
        Takes as input the Atlas labels path and ROI Number and outputs the ROI name for that atlas
        '''
        atlasDict = {}
        root = ET.parse(atlasLabelsPath).getroot()
        elem = root.find('data')
        for regionRow in elem.getchildren():
            # roiNumber  = int(regionRow.items()[2][1]) + 1 .items()
            # gives the items in arbitary order so indexing changes therefore use key= 'index'

            if self.ATLAS_XML_ZERO_START_INDEX:
                roiNumber = int(regionRow.get(key='index')) + 1
            else:
                roiNumber = int(regionRow.get(key='index'))

            roiName = regionRow.text
            atlasDict[roiNumber] = roiName

        return atlasDict[roiNum]

    def getAtlasRegions(self, coordMni):
        '''
        Takes as input MNI coordinates and returns a tuple (ROI_number, Region_name, Atlas_index_used)

        Algorithm:
        Loops over multiple atlases
            For each atlas get the maximum probability regions (2 here)
            Select the max prob region with its increment vector which will be used later to calculate the distance
            of each voxel fromt the query voxel.
            Discard the first one if it is WM or Cerebral cortex and select the second if it is not WW or CCortex.
            Save the [roiNumber, roiName ,final_coord ,final_itr, max_prob, index(representing atlas)] in an 'out' list
            (Traverse this list to find the closest max probabiliy region across atlases)
        Loop over the 'out' list
            select the atlases that contain the closest regions
        Loop over those regions to find the max probability region
        return roiNumber, roiName, atlasIndex

        '''
        roiNumber = None
        roiName = None


        atlasIndex = 0


        _roiNumber, _final_coord, _final_itr, _max_prob = [], None, None, None

        out = []
        for index,atlasPath in enumerate(self.atlasPaths):

            if roiNumber == None or self.prob == True:

                if self.pixdim_list[index] == 3:
                    x,y,z = self.MNI2XYZ3mm(coordMni)
                elif self.pixdim_list[index] == 2:
                    x,y,z = self.MNI2XYZ2mm(coordMni)
                elif self.pixdim_list[index] == 1:
                    x,y,z = self.MNI2XYZ1mm(coordMni)
                else:
                    raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )


                if self.prob == False:
                    roiNumber = self.atlas_list[index][x,y,z]
                    if roiNumber == 0: # Coordinate lies outside the atlas
                        _roiNumber, _final_coord, _final_itr, _max_prob = self.get_neighbouring_coordinates(x,y,z,self.itr,index)

                        if _roiNumber != None:
                            roiNumber=_roiNumber[0]
                            final_coord=_final_coord[0]
                            final_itr=_final_itr[0]
                            max_prob=_max_prob[0]
                        else:
                            roiNumber = None
                            continue
                    else:
                        final_coord = [x,y,z]
                        final_itr = [0,0,0]
                        max_prob = 1

                else:
                    # vec_of_prob = self.atlas_list[index][x,y,z,:]
                    # roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
                    # max_prob =  vec_of_prob[roiNumber - 1]
                    # if True:#max_prob == 0: # # Coordinate is outside the atlas
                    _roiNumber, _final_coord, _final_itr, _max_prob = self.get_neighbouring_coordinates(x,y,z,self.itr,index, largest= 3)

                    if _roiNumber == None:
                        continue

                    # Getting the Highest probability region from 2 largest returned
                    roiNumber=_roiNumber[0]
                    final_coord=_final_coord[0]
                    final_itr=_final_itr[0]
                    max_prob=_max_prob[0]
                    # else:
                    #     final_coord = [x,y,z]
                    #     final_itr = [0,0,0]
                    #     max_prob = 1



                if roiNumber != 0:
                    roiName = self.roiName(self.atlasLabelsPaths[index], roiNumber)

                    roiName  = roiName.strip()

                    # ----------------- When White Matter and Hemispheric information is not needed --------------------
                    # TODO Take as input from user about which ROI to ignore
                    if not self.WM_HEMISPHERE_INFO:

                        if self.prob == True:
                            if roiName == 'Right Cerebral White Matter' or roiName == 'Left Cerebral White Matter'\
                            or roiName == 'Left Cerebral Cortex' or roiName == 'Right Cerebral Cortex':
                                # Look for second largest in the same atlas
                                if len(_roiNumber) > 1: # If second highest prob region exists
                                    # Getting the second Highest probability region
                                    roiNumber=_roiNumber[1]
                                    final_coord=_final_coord[1]
                                    final_itr=_final_itr[1]
                                    max_prob=_max_prob[1]
                                    roiName = self.roiName(self.atlasLabelsPaths[index], roiNumber)
                                    roiName  = roiName.strip()
                                    if roiName == 'Right Cerebral White Matter'\
                                    or roiName == 'Left Cerebral White Matter'\
                                    or roiName == 'Left Cerebral Cortex'\
                                    or roiName == 'Right Cerebral Cortex':
                                        if len(_roiNumber) > 2: # If Third highest prob region exists
                                            roiNumber=_roiNumber[2]
                                            final_coord=_final_coord[2]
                                            final_itr=_final_itr[2]
                                            max_prob=_max_prob[2]
                                            roiName = self.roiName(self.atlasLabelsPaths[index], roiNumber)
                                            roiName  = roiName.strip()
                                            if roiName == 'Right Cerebral White Matter'\
                                            or roiName == 'Left Cerebral White Matter'\
                                            or roiName == 'Left Cerebral Cortex'\
                                            or roiName == 'Right Cerebral Cortex':
                                                roiNumber = None # Nothing is assigned
                                            else:
                                                # When the third Highest probability region is relevant
                                                out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])
                                    else:
                                        # When the second Highest probability region is relevant
                                        out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])



                                else:
                                    # Second highest probability region does not exist
                                    continue
                            else:
                                # Coordinate region is neither WM nor Hemispheric Info
                                out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])

                        else:
                            # 3D Brain atlas is present i.e prob == False
                            if roiName == 'Right Cerebral White Matter' or roiName == 'Left Cerebral White Matter'\
                            or roiName == 'Left Cerebral Cortex' or roiName == 'Right Cerebral Cortex':
                                roiNumber = None
                                continue
                            else:
                                out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])
                                roiNumber = None # To move to next atlas

                    # ------------------------------------------------------------------------------------------------------
                    else:
                        # WM_HEMISPHERE_INFO is True i.e. this info is required
                        if self.prob:
                            out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])
                        else:
                            out.append([roiNumber, roiName ,final_coord ,final_itr, max_prob, index])
                            roiNumber = None # To move to next atlas



                else:
                    # roiNumber is zero so set it to None and move to next atlas
                    roiNumber = None


        """
        Loop over the 'out' list
            select the atlases that contain the closest regions
        Loop over those regions to find the max probability region

        """
        # To find the minimum distance among all the arrays
        final_output_idx = 0
        final_min_dist = float('Inf')
        for idx,output in enumerate(out):

            dist = abs(output[3][0]) + abs(output[3][1]) + abs(output[3][2])
            if final_min_dist > dist:
                final_min_dist = dist

        final_max_prob = 0
        for idx,output in enumerate(out): # To find the max probability if there are multiple min arrays dist
            dist = abs(output[3][0]) + abs(output[3][1]) + abs(output[3][2])
            if dist == final_min_dist:
                if final_max_prob < output[4]:
                    final_max_prob = output[4]
                    final_output_idx = idx



        if len(out) == 0:
            roiNumber, roiName, atlasIndex = 0, None, None
        else:
            roiNumber, roiName, atlasIndex = out[final_output_idx][0], out[final_output_idx][1], out[final_output_idx][5]




        return int(roiNumber), roiName, atlasIndex


    def _XYZ_2_MNI(self,xyz_list,atlas_index):
        """
        Input: List of Lists. Each list is x,y,z is cartesian coordinates
        Converts the cartesian coordinates to MNI
        Output: List of Lists. Each list is x,y,z is MNI coordinates
        """
        mni_list = []
        for xyz in xyz_list:
            if self.pixdim_list[atlas_index] == 3:
                mni_list.append(self.XYZ2MNI3mm(xyz))
            elif self.pixdim_list[atlas_index] == 2:
                mni_list.append(self.XYZ2MNI2mm(xyz))
            elif self.pixdim_list[atlas_index] == 1:
                mni_list.append(self.XYZ2MNI1mm(xyz))
        return mni_list

    def _voxel_2_mm(self,voxel_coord_list,atlas_index):
        """
        Input: List of Lists. Each list is x,y,z displacement in terms of voxels
        Converts the number of voxels shift to mm shift. That is basically
        it converts the voxels to milimeter.
        Output: List of Lists. Each list is x,y,z displacement in terms of mm
        """
        mm_cord_list = []
        for voxel_coord in voxel_coord_list:
            if self.pixdim_list[atlas_index] == 3:
                mm_cord_list.append([i * 3 for i in voxel_coord]) # One Voxel = 3mm
            elif self.pixdim_list[atlas_index] == 2:
                mm_cord_list.append([i * 2 for i in voxel_coord]) # One Voxel = 2mm
            elif self.pixdim_list[atlas_index] == 1:
                mm_cord_list.append(voxel_coord)
        return mm_cord_list


    def get_neighbouring_coordinates(self,x,y,z, itr, atlas_index, largest=1):
        """
        Takes X,Y,Z brain coordinates in image space and finds the region according to the given atlas.
        Using the max(itr) number of voxels cube arounf the query voxel, it tries to find the most
        appropriate region according to the following criteria:

        The top 'largest' largest regions are extracted for each atlas at the given voxel.
        If the given voxel doesnot have any information in the atlas, then the nearby voxels are looked for region
        information. The result is the nearest voxel's region. The nearest voxel is found by employing a distance
        metric given by `dist = abs(xi) +  abs(yi)  + abs(zi)` where xi,yi,zi is the increments in the location of
        the neighbourhood of the voxel under query.

        Inputs:

        Outputs:
        final_roi_list: The top 2 ROI numbers
        final_coord_list: Corresponding MNI Coordinates given as a list of lists
            [[MNI_coordinates1],[MNI_coordinates2]]
        final_itr_list: List of increments to reach at the target voxel
        final_max_prob_list: List if probabilities of the corresponding regions selected

        Algorithm: (for prob = True)
        Loop over all voxel increments
            Loop over how many largest regions are needed
                Get the max region corresponding to the given voxel
                    If the max region lies inside the atlas
                        Make sure we are not far from the region we have already found (i.e. pritorizing over
                        the diatance feom the quesry voxel over the probability of the neighbouring voxels).
                            Populate the roi_list.
                        if roi_list is not empty
                            Pupulate the final_roi_list with the above got ROI_list
                            Similarly populate the other final lists


        """
        final_coord = [x,y,z]
        old_dist = float('Inf')
        final_itr = [0,0,0]
        final_roi = 0


        final_roi_list = []
        final_coord_list = []
        final_itr_list = []
        final_max_prob_list = []


        roi_list = []
        coord_list = []
        itr_list = []
        max_prob_list = []


        for xi in itr:
            for yi in itr:
                for zi in itr:
                    roi_list = []
                    coord_list = []
                    itr_list = []
                    max_prob_list = []
                    if self.prob:
                        vec_of_prob = np.array(
                        self.atlas_list[atlas_index][x-xi,y-yi,z-zi,:])
                        """
                        It's an array of multiple probability values. A new
                        array was created using np.array() as setting the largest val
                        in vec_of_prob to 0 was not allowing getting the name
                        of the same coordinates multiple times using the same
                        class object and was giving None second time
                        onwards. """
                    else:
                        vec_of_prob = np.array(
                        [self.atlas_list[atlas_index][x-xi,y-yi,z-zi]])
                        # It's an array of a single value i.e the ROI number
                        largest = 1
                        """Forced assignment as we are dealing with a
                        static atlas and not region probability maps """

                    for counter in range(largest):

                        roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
                        #TODO:
                        """
                        Take as input from the user the ROI_ignore list to ignore.
                        As the roiNumber in ROI_ignore:
                            continue #(keyword) This will make the program counter to jump to the next
                                     # iteration of loop. Need to check if it works.


                        """
                        max_prob =  vec_of_prob[roiNumber - 1]
                        if max_prob != 0: # the max roi lies inside the atlas
                            dist = abs(xi) +  abs(yi)  + abs(zi) # Distance metric
                            # check if the new distance 'dist' is less than the previously seen distance or not
                            if dist <= old_dist: #or final_itr == [0,0,0]
                                old_dist = dist
                                coord_list.append([x-xi, y-yi, z-zi])
                                final_itr = [xi,yi,zi]
                                itr_list.append([xi,yi,zi])
                                if self.prob:
                                    roi_list.append(roiNumber)
                                    max_prob_list.append(max_prob)
                                else:
                                    roi_list.append(max_prob) # In fixed atlas, the probability/label value of the voxel denotes the region name
                                    max_prob_list.append(1) # assign probability 1 to the fixed atlas region

                            vec_of_prob[roiNumber - 1] = 0 # to find second highest region

                    if len(roi_list) != 0:
                        final_roi_list = roi_list
                        final_coord_list = self._XYZ_2_MNI(coord_list, atlas_index)
                        final_itr_list = self._voxel_2_mm(itr_list, atlas_index)
                        final_max_prob_list = max_prob_list

        if len(final_roi_list) == 0:
            final_roi_list, final_coord_list, final_itr_list, final_max_prob_list = None, None, None, None

        return final_roi_list, final_coord_list, final_itr_list, final_max_prob_list




if __name__ == "__main__":


    # Parser to parse commandline arguments

    ap = argparse.ArgumentParser()



    ap.add_argument("-mni", "--mni", nargs='+', required=True,
        help="MNI Coordinates space seperated")

    ap.add_argument("-p", "--prob",  action='store_true', required=False,
        help="-p True for using the probability maps")

    args = vars(ap.parse_args())


    # Reading the arguments
    prob = args["prob"]

    # Converting the numbers read as string to integers

    MNI = list(map(int, args["mni"]))



    base_path = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/'

    if prob:
        atlas_paths = [
        base_path + 'hoAtlas/HarvardOxford-cort-prob-1mm.nii.gz',
        base_path + 'hoAtlas/HarvardOxford-sub-prob-1mm.nii.gz',
        base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-prob-1mm.nii.gz'
        ]
    else:
        atlas_paths = [
        base_path + 'hoAtlas/HarvardOxford-cort-maxprob-thr25-1mm.nii.gz',
        base_path + 'hoAtlas/HarvardOxford-sub-maxprob-thr25-1mm.nii.gz',
        base_path + 'cerebellumAtlas/Cerebellum-MNIflirt-maxprob-thr25-1mm.nii.gz'
        ]

    atlas_labels_paths = [
    base_path + 'hoAtlas/HarvardOxford-Cortical.xml',
    base_path + 'hoAtlas/HarvardOxford-Subcortical.xml',
    base_path + 'cerebellumAtlas/Cerebellum_MNIflirt.xml'
    ]

    obj = queryAtlas(atlas_paths,atlas_labels_paths)


    print(obj.getAtlasRegions(MNI))

    # Get the region from the above defined atlas

    cont = True
    while(cont):
        MNI = input('Type space seperated MNI (Or Type q to quit): ')
        if MNI == 'q':
            cont = False
            continue

        # Converting the numbers read as string to integers
        MNI = list(map(int, MNI.split()))
        print(obj.getAtlasRegions(MNI))

    # # In[72]:
    #
    # # atlasPath2 = ['juelichAtlas/Juelich-maxprob-thr25-1mm.nii.gz']
    # atlasPath2 = ['juelichAtlas/Juelich-maxprob-thr0-1mm.nii.gz']
    # # atlasPath2 = ['juelichAtlas/Juelich-prob-1mm.nii.gz']
    #
    # atlasLabelsPath2 = ['juelichAtlas/Juelich.xml']
    # q2 = queryAtlas(atlasPath2,atlasLabelsPath2,False)
    #
    # # In[73]:
    # q2.getAtlasRegions([33, -6, -6])
