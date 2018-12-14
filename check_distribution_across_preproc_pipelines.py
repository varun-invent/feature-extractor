import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.pyplot.switch_backend('agg')
import glob
import nibabel as nib
import pandas as pd
from scipy import stats
'''
This script generates the histograms representing the distribution of logq values
for each preproc pipeline
It also generates a csv file showing the mean, std and median of the logq values
for each preproc pipeline
'''
def check_distribution(csv_path_regex, brain_path_regex, out_file=None):

    mean_std_median_dict = {'Option':[], 'Mean':[], 'Std':[], 'Median':[]}
    for csv_filename,brain_filename in zip(glob.iglob(csv_path_regex, recursive=True),\
                        glob.iglob(brain_path_regex, recursive=True)):
        opt = csv_filename.split('/')[-1].split('_')[-1].split('.')[0]
        print('Option: ', opt)
        print(brain_filename)
        '''
        For each logq brain map, use all the values and create a histogram.
        '''


        brain_vec = nib.load(brain_filename).get_data().flatten()
        brain_vec = brain_vec[~np.isnan(brain_vec)]

        print('Finding stats')
        print('Calculating Mean')
        mean = np.mean(brain_vec)

        print('Calculating Std')
        std = np.std(brain_vec)

        # print('Calculating Mode')
        # mode = stats.mode(brain_vec)

        print('Calculating Median')
        median = np.median(brain_vec)

        print('Stats Calculated')

        mean_std_median_dict['Option'].append(opt)
        mean_std_median_dict['Mean'].append(mean)
        mean_std_median_dict['Std'].append(std)
        mean_std_median_dict['Median'].append(median)


        print('Plotting')
        plt.hist(brain_vec, bins='auto', range = (-2.5,2.5))#, density=True)
        plt.title(opt)
        plt.savefig('hist/Hist_%s'%opt)
        plt.clf()

        df = pd.DataFrame(data = mean_std_median_dict, columns = ['Option', 'Mean', 'Std', 'Median'])#, 'mode'])
        out_file = out_file + 'qvalue_stats.csv'
        df.to_csv(out_file)


if __name__ == '__main__':
    csv_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE1_4/fdrRes/**/*.csv"
    brain_path_regex = "/mnt/project2/home/varunk/fMRI/results/resultsABIDE1_4/fdrRes/**/**/map_logq.nii.gz"
    out_file = 'ABIDE1'
    check_distribution(csv_path_regex, brain_path_regex)
