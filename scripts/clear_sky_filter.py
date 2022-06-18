#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  19 17:07:57 2022

@author: Samer Chaaraoui
"""


import numpy as np
np.random.seed(1234) # set seed for randomizer to get the same split for train, val and test dataset

import pandas as pd
import matplotlib.pyplot as plt
import glob


from pvlib.location import Location
from pvlib import clearsky

### if days plots should be plotted and saved
plot_and_save_fig = True

### Location infromation of the measurment site. Information is from the paper of Pedro et. al. 2019. This is necessary for PVLIB clear-sky detection

latitude, longitude, tz, altitude, name = 38.642, -121.148, 'America/Los_Angeles', 100, 'Folsom'
tus = Location(latitude, longitude, tz, altitude, name)

### Since the pictures are not taken exactly on the minute, but the radiation data is measured on the minute, we have to assume that the image corresponds to the closest minute.
### Example 1: 12:31:29 -> 12:31:00
### Example 2: 09:12:51 -> 09:13:00
### This function adapts the timestamp index of the dataframe accordingly
def half_up_minute_idx(idx):
    m = (idx - idx.floor('1T')).total_seconds() < 30   # Round True Down, False Up
    return pd.Index(np.select([m], [idx.floor('1T')], default=idx.ceil('1T')))


filepaths_imagedata = sorted(glob.glob('/scratch/MAS_FB02_DLRV/ASI_Project/Images/*/*/*/*.jpg')) # gather all filepaths to the images to a list and sort them

### create a dataframe and set the index according the timestamp of the filename

image_data = pd.DataFrame(filepaths_imagedata)
image_data = image_data.set_index(pd.to_datetime([w[-19-8:-4-8] for w in filepaths_imagedata], format="%Y%m%d_%H%M%S"))

image_data.index = image_data.index.tz_localize('utc').tz_convert('America/Los_Angeles') # set the timezone from utc to los angeles timezone

### read the radiation data file
filepaths_raddata = '/scratch/MAS_FB02_DLRV/ASI_Project/Radiationdata/Folsom_irradiance.csv'
rad_data = pd.read_csv(filepaths_raddata, index_col='timeStamp', parse_dates=True, usecols=['timeStamp','ghi'])

rad_data.index = rad_data.index.tz_localize('utc').tz_convert('America/Los_Angeles') # set the timezone from utc to los angeles timezone

### linearly interpolate missing values 
rad_data_idx = pd.date_range(start=rad_data.index[0], end=rad_data.index[-1], freq='min')
rad_data = rad_data.reindex(rad_data.index.union(image_data.index)).interpolate(method='time').reindex(rad_data_idx)

### correct the timestamp index, as described above with function "half_up_minute_idx"
image_data.index = half_up_minute_idx(image_data.index)

image_data = image_data[~image_data.index.duplicated(keep='first')] # in case of duplicates due to "half_up_minute_idx"

dataset = np.unique(image_data.index.date)

total_days = dataset

print(total_days)

val_test_ratio = int(len(dataset)*0.1)

index = np.random.choice(dataset.shape[0], val_test_ratio, replace=False)

dates_val = dataset[index]
dataset = np.delete(dataset, index, axis=0)

index = np.random.choice(dataset.shape[0], val_test_ratio, replace=False)

dates_test = dataset[index]

dates_train = np.delete(dataset, index, axis=0)

## empty DataFrame for the clear-sky detection
clear_sky_bool_df = pd.DataFrame(index=rad_data_idx, columns=['clear_sky'], data=False)

steps_before=30
steps_after=30

for j in range(len(total_days)):
    print(j)
  
    start_ts = str(image_data.loc[total_days[j].strftime("%Y-%m-%d")].iloc[0].name)
    end_ts = str(image_data.loc[total_days[j].strftime("%Y-%m-%d")].iloc[-1].name)
    
    dateindex = image_data.loc[total_days[j].strftime("%Y-%m-%d")]
    dateindex = dateindex.rename(columns={0: "frame"})
    dateindex['available'] = 1
    dateindex = dateindex.reindex(pd.date_range(start_ts, end_ts, freq='min'))
    print(dateindex.isna().sum())
    try:
        rad_data_temp = rad_data.loc[dateindex.index]
    except KeyError:
        continue
    cs = tus.get_clearsky(dateindex.index)['ghi']
    cs_bool = clearsky.detect_clearsky(measured=rad_data_temp.squeeze(), clearsky=cs, times=cs.index, window_length=10, max_iterations=100).to_frame()
    cs_bool = cs_bool.rename(columns={0:'clear_sky'})
    clear_sky_bool_df.loc[cs_bool.index, :] = cs_bool[:]
    if plot_and_save_fig == True:   
        ax = rad_data_temp.plot()
        (cs_bool*500).plot(ax=ax)
        plt.savefig('/scratch/vkalag2s/ASIRE-code-base/clear_sky_images/'+total_days[j].strftime("%Y-%m-%d")+'.png')
        plt.close()
clear_sky_bool_df['file_paths'] = image_data[:,1]
clear_sky_bool_df['ghi'] = rad_data['ghi']

clear_sky_true = clear_sky_bool_df[clear_sky_bool_df['clear_sky'] == "true"]
clear_sky_false = clear_sky_bool_df[clear_sky_bool_df['clear_sky'] == "false"]

clear_sky_true.to_csv('/scratch/vkalag2s/ASIRE-code-base/clear_sky_true.csv')
clear_sky_true.to_csv('/scratch/vkalag2s/ASIRE-code-base/clear_sky_false.csv')