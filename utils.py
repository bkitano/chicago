import pandas as pd
import numpy as np


def getDefinedRows(df):
    rows_with_data = pd.notna(df['latitude']) & pd.notna(df['longitude']) & pd.notna(df['day']) & pd.notna(df['month']) & pd.notna(df['year'])
    
    return rows_with_data

def getPointsWithinDistance(distances_df, centroid_id, threshold):
    return distances_df[np.logical_and(
        distances_df['km'] <= threshold, 
        distances_df['unique_dist_id'] == centroid_id
    )]

def getDataFromPoints(dataDf, pointsDf):
    df = pointsDf.merge(
        dataDf,
        how='outer',
        on=['latitude', 'longitude']
    ).dropna()
    
    return df
    

def getDailyAveragesFromData(dataDf):
    pointDataDf = dataDf
    pointDataDf['weight'] = 1./np.power(pointDataDf['km'], 2.)
    pointDataDf['weightedTemperature'] = (pointDataDf['temperature']*pointDataDf['weight'])
    pointDataDf['weightedRainfall'] = (pointDataDf['rainfall']*pointDataDf['weight'])
    
    keep_cols = ['day', 'month', 'weight', 'year', 'rainfall', 'weightedTemperature', 'weightedRainfall', 'unique_dist_id']
    districtDf = pointDataDf[keep_cols].groupby(by=['month','day', 'year', 'unique_dist_id']).sum()
    districtDf['weightedAverageTemperature'] = districtDf['weightedTemperature']/districtDf['weight']
    districtDf['weightedAverageRainfall'] = districtDf['weightedRainfall']/districtDf['weight']
    
    return districtDf.drop(columns=['weight', 'weightedTemperature', 'weightedRainfall']).reset_index()


def getDailyAverages(rain_path, temp_path, distances_path, centroid_id, threshold=100):
    
    # read from csv
    raw_rain_df = pd.read_csv(rain_path)
    raw_temp_df = pd.read_csv(temp_path)
    distances_df = pd.read_csv(distances_path)
    
    # filter only defined columns
    rain_df = raw_rain_df[getDefinedRows(raw_rain_df)]
    temp_df = raw_temp_df[getDefinedRows(raw_temp_df)]
    
    # merge df's
    on_columns = ['latitude', 'longitude', 'day', 'month', 'year']
    total_df = rain_df.merge(temp_df, how='outer', left_on=on_columns, right_on=on_columns)
    
    # get points
    pointDataDf = getDataFromPoints(
        total_df, 
        getPointsWithinDistance(distances_df, centroid_id, threshold)
    )
    dailyAveragesDf = getDailyAveragesFromData(pointDataDf)
    return dailyAveragesDf

def mergeCsvsInDirectory(path):
    all_files = glob.glob(path + "/*.csv")

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    mergedDf = pd.concat(li, axis=0, ignore_index=True)
    return mergedDf