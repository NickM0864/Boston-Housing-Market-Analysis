import numpy as np
import pandas as pd
import os
from geo import Geohousing
import requests

dcid_list = Geohousing['CTID1']
median_income_dict = dict()

#Run scraper if CSV doesn't exist
file_path_str = 'median_income.csv' #Relative path
if not os.path.exists(file_path_str):
    for id in dcid_list:
        median_income_get = requests.get(url = f'https://api.datacommons.org/stat/value?place=geoId/{id}&stat_var=Median_Income_Household')
        median_income_str = median_income_get.text
        median_income_dict[id] = median_income_str
else:
    median_income_df = pd.DataFrame.from_dict(median_income_dict, orient = 'index').reset_index()
    median_income_df.columns = ['CT_ID', 'Median_Income']
    median_income_df['Median_Income'] = median_income_df['Median_Income'].str.extract('(\d+)').astype(int)
    format_dict = {'Median_Income':'${0:,.0f}'}
    median_income_df.style.format(format_dict)
    #print(median_income_df['Median_Income'].value_counts())
    median_income_df[median_income_df['Median_Income'] == 5] = pd.NA
    print(median_income_df['Median_Income'].isna().sum())
    median_income_df['Median_Income_Percentile_Rank'] = median_income_df['Median_Income'].rank(pct = True).round(2)
    median_income_df['Median_Income_Percentile_Rank'] = pd.Series(["{0:.2f}%".format(val * 100) for val
                                                                   in median_income_df['Median_Income_Percentile_Rank']],
                                                                  index = median_income_df.index)
    # median_income_df['C'] = np.where(
    #     df['A'] == df['B'], 0, np.where(
    #     df['A'] >  df['B'], 1, -1))

    print(median_income_df)
    median_income_csv = median_income_df.to_csv('~/PycharmProjects/pythonProject/median_income.csv', index = True)








#print(median_income_get.text)
# post = requests.post(url = "https://api.datacommons.org/node/property-values", headers = headers, data = '{"dcids": "geoId/25025000601", "property":"places"}')
# stat_vars = post.json()
# print(stat_vars)
#print(stat_vars['places']['geoId/25025000601']['statVars'][5])
# dumped = json.loads(stat_vars, indent=4)
# print(dumped['places']['geoId/25025000601']['statVars'][0]['Median_Income_Household'])
