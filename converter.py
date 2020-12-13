#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob, os

import utils

RAIN_DIRECTORY = './data/Rainfall/'
TEMP_DIRECTORY = './data/Temperature/'
DISTANCES_PATH = './distances.csv'

OUTPUT_DIR = './data/DailyAverages'

geo_df = pd.read_csv('./data/Geo/district_crosswalk_small.csv')

def getDailyAveragesWithLogger(rain_path, temp_path, distances_path, dist_id, threshold):
    print(f'getting daily averages for {dist_id}')
    return utils.getDailyAverages(rain_path, temp_path, distances_path, dist_id, threshold)

def writeDailyAverages(rain_path, temp_path, distances_path, output_path):

    district_series = geo_df['unique_dist_id'].apply(
        lambda dist_id: getDailyAveragesWithLogger(rain_path, temp_path, distances_path, dist_id, 100)
    )
    
    district_df = pd.concat(district_series.tolist())
    
    district_df.to_csv(output_path)

def main():
    rainTempPairs = list(zip(
        sorted(glob.glob(f"{RAIN_DIRECTORY}/*.csv")),
        sorted(glob.glob(f"{TEMP_DIRECTORY}/*.csv"))
    ))
    
    for rainPath, tempPath in rainTempPairs:
        print(f'getting daily averages from `{rainPath}, `{tempPath}...')
        year = rainPath.split('_')[-1].split('.')[0]
        print(f'year: {year}')
        output_path = f'{OUTPUT_DIR}/districtDailyAverage_{year}.csv'
        
        writeDailyAverages(rainPath, tempPath, DISTANCES_PATH, output_path)
        print('finished.')

if __name__ == "__main__":
    main()