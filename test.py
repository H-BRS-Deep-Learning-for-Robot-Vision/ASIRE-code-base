#!/usr/bin/env python3

import pandas as pd

image_data = pd.read_csv('/scratch/vkalag2s/ASIRE-code-base/image_data.csv')

image_data.columns = ["date", "filepath"]

new_dat2 = pd.read_csv('/scratch/vkalag2s/ASIRE-code-base/new_data.csv')

new_dat2['fp2'] = image_data['filepath']

new_dat2.to_csv('/scratch/vkalag2s/ASIRE-code-base/new_dat2.csv')
