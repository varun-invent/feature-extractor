import numpy as np

import brainnetomeUtility as bu
import atlasUtility as au
import argparse

# -----------------------------------------------------------------------------
# TODO To go in config.json file
# -----------------------------------------------------------------------------
atlas_path = ('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
              'analysis/brainnetomeAtlas/BNA-prob-2mm.nii.gz')
atlasRegionsDescrpPath = ('/home/varun/Projects/fmri/Autism-survey-'
                          'connectivity-links-analysis/brainnetomeAtlas/'
                          'BNA_subregions_machineReadable.xlsx')

atlasPaths1  = [('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
                 'analysis/hoAtlas/HarvardOxford-sub-maxprob-thr0-1mm.nii.gz'),\
                ('/home/varun/Projects/fmri/Autism-survey-connectivity-links-'
                'analysis/hoAtlas/HarvardOxford-cort-maxprob-thr0-1mm.nii.gz'),\
                ('/home/varun/Projects/fmri/Autism-survey-connectivity'
                '-links-analysis/cerebellumAtlas/Cerebellum-MNIflirt-'
                'maxprob-thr0-1mm.nii.gz')]

atlasLabelsPaths1 = [('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/hoAtlas/HarvardOxford-Subcortical.xml'),\
                     ('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/hoAtlas/HarvardOxford-Cortical.xml'), \
                     ('/home/varun/Projects/fmri/Autism-survey-connectivity-'
                     'links-analysis/cerebellumAtlas/Cerebellum_MNIflirt.xml')]


base_path = '/home/varun/Projects/fmri/Autism-survey-connectivity-links-analysis/'

aal_atlas_path = [base_path +
'aalAtlas/AAL.nii.gz']
aal_atlas_labels_path = [base_path +
'aalAtlas/AAL.xml']

# -----------------------------------------------------------------------------

# Parser to parse commandline arguments

ap = argparse.ArgumentParser()

ap.add_argument("-a", "--atlas", required=True,
                help="b: BN Atlas, hoc: HO/Cerebellum Atlas, aal: AAL atlas")
ap.add_argument("-mni", "--mni", nargs='+', required=True,
                help="MNI Coordinates space seperated")

args = vars(ap.parse_args())

# Reading the arguments

atlas = args["atlas"]
# Converting the numbers read as string to integers
MNI = list(map(int, args["mni"]))

# Temporary variables to be used as proxy for objects

q = q1 = aal_atlas_obj = False

if atlas == 'b':
    q = bu.queryBrainnetomeROI(atlas_path, atlasRegionsDescrpPath)
elif atlas == 'hoc':
    q1 = au.queryAtlas(atlasPaths1,atlasLabelsPaths1)
elif atlas == 'aal':
    aal_atlas_obj = au.queryAtlas(aal_atlas_path,aal_atlas_labels_path, atlas_xml_zero_start_index = False )

else:
    raise Exception('Incorrect Atlas Option')

# Assigning the proxy to the object variable

print('Atlas Flag: ',atlas)

if q:
    obj = q
elif q1:
    obj = q1
elif aal_atlas_obj:
    obj = aal_atlas_obj


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
