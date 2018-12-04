import pandas as pd
import numpy as np

'''
Next is:
1. Read the Links in review and extract the XML type names for BN regions.
2. Break each of the region names so that their hemisphere is another column.
3. Consider C as Both L and R while matching links.
4. For each link got here, check how many are replicated.

HOWTO:

in_file1 = Read the review links file
From the 2nd and 4th column extract the name of the region by name.split('_')[1].split(',')[0]
in_file2 = Read the ABIDE BN regions file
Split the 2 region name's columns into 4 columns -
 Two hemisphere columns by getting each hemisphere by name.split('_')[-1]
 And other by name.split('_')[0]

For each of the links (link_2) of in_file2
    Loop through each of the links (link_1) of in_file1
        if(link_1 == link2)
            dict[link_1] = dict[link_1] + 1

'''
