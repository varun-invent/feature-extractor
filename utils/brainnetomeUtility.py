
# coding: utf-8


import pandas as pd
import nibabel as nib
import numpy as np
import math
import xml.etree.ElementTree as ET
from tqdm import tqdm
import argparse




class queryBrainnetomeROI:
    """
    Class queryBrainnetomeROI provides methods by which you can accomplish the following:
    - Given ROI number get [Lobe, Gyrus, Region and MNI Coordinates] using queryDict(ROI_number) or queryDict([ROI_numbers])
    - Given MNI coordinates get [Lobe, Gyrus, Region and MNI Coordinates] using getAtlasRegions([x,y,z])
    Usage:
    >>> atlas_path = 'BNA-maxprob-thr0-1mm.nii.gz' # path to the atlas file
    >>> atlasRegionsDescrpPath = 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx' # path to ROI description xlsx
    >>> q = queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)
    >>> q.queryDict(246)
    [array(['Subcortical Nuclei', 'Tha, Thalamus',
        'Tha_lPFtha, lateral pre-frontal thalamus', '13, -16, 7 '],
       dtype=object)]

    Also, this function supports the use of 4D probability map of the atlas to find the nearby
    maximim probability region in the vicinity of 3 voxel cube if the region at a particular voxel is not
    present in the atlas.
    Set prob = True  and provide a 4D nii.gz file path as atlas_path
    """
    def __init__(self, atlas_path, atlasRegionsDescrpPath):
        self.atlas_path = atlas_path



        _atlas = nib.load(self.atlas_path)
        self.atlas = _atlas.get_data()

        """
        Following Code to set the prob variable to True if user has
        entered probability maps and False if fixed labeled atlas is entered
        """
        atlas_shape_len = len(self.atlas.shape)
        if atlas_shape_len == 4:
            self.prob = True
        elif atlas_shape_len == 3:
            self.prob = False
        else:
            raise Exception('Exception: Atlas of unknown shape. Exiting!')



        print('Atlas read')
        if _atlas.header['pixdim'][1] == 2:
            self.pixdim = 2
        elif _atlas.header['pixdim'][1] == 1:
            self.pixdim = 1
        else:
            raise Exception('Unknown Pixel Dimension', _atlas.header['pixdim'][1] )

        print('checked Pixel dimension')

        self.numSeeds = None
        self.atlasRegionsDescrpPath = atlasRegionsDescrpPath


    def MNI2XYZ1mm(self, mni):
        x =  - mni[0] + 90
        y = mni[1] + 126
        z = mni[2] + 72
        return [x,y,z]

    def MNI2XYZ2mm(self, mni):
        x =  math.floor((- mni[0] + 90)/2.0)
        y = math.floor((mni[1] + 126)/2.0)
        z = math.floor((mni[2] + 72)/2.0)
        return [x,y,z]


    def XYZ2MNI1mm(self, xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 1mm atlas
        """
        mni_x = - xyz[0] + 90
        mni_y = xyz[1] - 126
        mni_z = xyz[2] -72
        return [mni_x, mni_y, mni_z]


    def XYZ2MNI2mm(self, xyz):
        """
        Converts the given X,Y,Z cartesian coordinates to MNI coordinates corresponding to the 2mm atlas
        """
        mni_x = - 2*xyz[0] + 90
        mni_y = 2*xyz[1] - 126
        mni_z = 2*xyz[2] -72
        return [mni_x, mni_y, mni_z]

    def brainnetomeQuery(self):
        """
        Extract the region names from excel file and creates a dictionary i.e. key value pair
        where Key is the ROI number and Value is the list of [Lobe, Gyrus, Region and MNI Coordinates]
        of the query ROI Number.

        """
        df = pd.read_excel(self.atlasRegionsDescrpPath)

        if self.prob:
            self.numSeeds = self.atlas.shape[3]
        else:
            self.numSeeds = int(np.max(self.atlas))

        df = df.as_matrix(['Lobe','Gyrus','Label ID.L', 'Label ID.R','Left and Right Hemisphere','Unnamed: 5', 'lh.MNI(X,Y,Z)', 'rh.MNI(X,Y,Z)'])
        seedInfo = np.empty((self.numSeeds + 1, 5),dtype=object)

        for lobe, gyrus, i,j,region,label,lcoord,rcoord in df:
            seedInfo[i,:] = i,lobe, gyrus, region.split('_')[0] + '_' + label, lcoord
            seedInfo[j,:] = j,lobe, gyrus, region.split('_')[0] + '_' + label, rcoord


        # Create a dictionary of seedInfo so that it can be accessed by roi number

        ROI_dictionary = {}
        for i in seedInfo[1:]:
            ROI_dictionary[i[0]] = i[1:]

        return ROI_dictionary



    def queryDict(self, lis): # lis: List that contains ROI numbers (1 to 246)
        """
        Used yhe dicrionary created by self.brainnetomeQuery() and ...
        Returns the list of [Lobe, Gyrus, Region and MNI Coordinates] of the query ROI Number
        """

        ROI_dictionary = self.brainnetomeQuery()
        return_regions = []

        # If input is a list of ROI numbers
        if isinstance(lis,list):
            for i in lis:
                try: return_regions.append(ROI_dictionary[i])
                except KeyError:
                    # returns List of None if ROI number is not found. ROI = [1,246]
                    return_regions.append([None,None,None,None])

        # If input is just a single ROI number
        else:
            i = lis
            try: return_regions.append(ROI_dictionary[i])
            except KeyError:
                return_regions.append([None,None,None,None])


        return return_regions

    def getAtlasRegions(self, coordMni):
        """
        Converts the MNI coordinates to image coordinates by using MNI2XYZ2mm() or MNI2XYZ1mm()
        It calls self.queryDict() in the background
        Returns the list of [Lobe, Gyrus, Region and MNI Coordinates] of the query MNI Coordinate.
        """

        if self.pixdim == 2:
            x,y,z = self.MNI2XYZ2mm(coordMni)
        elif self.pixdim == 1:
            x,y,z = self.MNI2XYZ1mm(coordMni)

        if self.prob == False:
            roiNumber = self.atlas[x,y,z]
            if roiNumber == 0: # Coordinate is outside the atlas
                itr = [0,1,-1,2,-2,3,-3]
                roiNumber, final_coord, final_itr = self.get_neighbouring_coordinates(x,y,z,itr)

        else:
            vec_of_prob = self.atlas[x,y,z,:]
            roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
            max_prob =  vec_of_prob[roiNumber-1]
            if max_prob == 0: # # Coordinate is outside the atlas
                itr = [0,1,-1,2,-2,3,-3]
                roiNumber, final_coord, final_itr = self.get_neighbouring_coordinates(x,y,z,itr)



        lobe, gyrus, roiName, _ = self.queryDict(roiNumber)[0]
        return int(roiNumber),lobe, gyrus, roiName

    def get_neighbouring_coordinates(self,x,y,z,itr):
        final_coord = [x,y,z]
        old_dist = float('Inf')
        final_itr = [0,0,0]
        final_roi = 0
        for xi in itr:
            for yi in itr:
                for zi in itr:
                    if self.prob:
                        vec_of_prob = self.atlas[x-xi,y-yi,z-zi,:]
                        # It's an array of multiple probability values
                    else:
                        vec_of_prob = np.array([self.atlas[x-xi,y-yi,z-zi]])
                        # It's an array of a single value i.e the ROI number

                    roiNumber = np.argmax(vec_of_prob) + 1 # [1 ... num_roi's]
                    max_prob =  vec_of_prob[roiNumber - 1]
                    if max_prob != 0: # the max roi lies inside the atlas
                        dist = abs(xi) +  abs(yi)  + abs(zi)
                        if dist < old_dist or final_itr == [0,0,0]:
                            old_dist = dist
                            final_coord = [x-xi, y-yi, z-zi] # Cartesian Coordinates
                            final_itr = [-xi,-yi,-zi] # Cartesian Coordinates


                            if self.prob:
                                final_roi = roiNumber
                            else:
                                final_roi = max_prob

        # To convert the Cartesian Coordinates to MNI
        if self.pixdim == 2:
            final_coord = self.XYZ2MNI2mm(final_coord)
            final_itr = [i * 2 for i in final_itr] # One Voxel = 2mm
        elif self.pixdim == 1:
            final_coord = self.XYZ2MNI1mm(final_coord)



        """
        Note:
        Due to the conversion of MNI to XYZ and back the precision is lost if
        the 2mm atlas is used. The precision lost is just +- 1mm. For example:
        Input MNI: [24 -13 30]
        Output:
            final_itr: [6, 0, -4] But,
            final_coord: [18, -14, 26]. There is an error in Y coordinate.

        """
        return final_roi, final_coord, final_itr






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
        atlas_path = base_path + 'brainnetomeAtlas/BNA-prob-2mm.nii'
    else:
        atlas_path = base_path + 'brainnetomeAtlas/BNA-maxprob-thr0-1mm.nii.gz'

    atlasRegionsDescrpPath = base_path + 'brainnetomeAtlas/BNA_subregions_machineReadable.xlsx'
    obj = queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)

    # Get the region from the above defined atlas
    print(obj.getAtlasRegions(MNI))
    cont = True
    while(cont):
        MNI = input('Type space seperated MNI (Or Type q to quit): ')
        if MNI == 'q':
            cont = False
            continue

        # Converting the numbers read as string to integers
        MNI = list(map(int, MNI.split()))
        print(obj.getAtlasRegions(MNI))
