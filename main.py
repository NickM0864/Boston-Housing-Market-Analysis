import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from geo import *
import json
import plotly.express as px


#Preprocessing
plt.close('all')

pd.set_option('display.expand_frame_repr', False)
Housing_Data = pd.read_csv('/Users/nick/Documents/Boston housing/Craigslist_CT/CRAIGSLIST.CT-1.csv')
Housing_Data = Housing_Data.rename(columns={"COUNTY": "County", "TOWN": "Town"})
Housing_Data['County'].unique()
Housing_Data = Housing_Data[Housing_Data["County"] == "SUFFOLK"] #Filtering to only include Boston listings
Housing_Data['ListingsFreq_Cross'].count

Listings_Feb_Jun = Housing_Data[['ListingsFreq_Feb', 'ListingsFreq_Mar',
                                    'ListingsFreq_Apr','ListingsFreq_May','ListingsFreq_Jun']].plot.box(vert = False)

#Drop February and March data due to tiny sample size.
# This shouldn't impact the analysis because there is only two weeks of overlap between the time period and the start of coronavirus in America.
#Also dropping town and county columns as they're no longer descriptive.
Housing_Data[['ListingsFreq_Feb', 'ListingsFreq_Mar', 'ListingsFreq_Apr']].describe()
Housing_Data.drop(columns = ['ListingsFreq_Feb', 'ListingsFreq_Mar',
                             "MedianRent_Feb","MedianRent_Mar","Town","County"], axis =1, inplace = True)

#Changing median housing price to mean
Housing_Data.columns = Housing_Data.columns.str.replace('Median', 'Mean')

Listings_by_Month = ['ListingsFreq_Apr','ListingsFreq_May','ListingsFreq_Jun',
                     'ListingsFreq_Jul','ListingsFreq_Aug','ListingsFreq_Sep',
                     'ListingsFreq_Oct','ListingsFreq_Nov',"ListingsFreq_Dec"]

# Recalculating listing frequency after removing Feb/March
Housing_Data["ListingsFreq_Cross"]= Housing_Data[Listings_by_Month].sum(axis = 1)
Housing_Data["ListingsFreq_Cross"].describe
# Removing all neighborhoods with fewer than 125 listings. Reduced neighborhoods from 200 to 65.
Housing_Data = Housing_Data[Housing_Data['ListingsFreq_Cross'] > 125]


Listings_Apr_Dec = Housing_Data[['ListingsFreq_Apr', 'ListingsFreq_May', 'ListingsFreq_Jun',
                     'ListingsFreq_Jul','ListingsFreq_Aug','ListingsFreq_Sep',
                     'ListingsFreq_Oct','ListingsFreq_Nov',"ListingsFreq_Dec"]].plot.box(vert = False)

# Recalculating neighborhood mean rent after removing Feb/March.
# Removing February and March median rent data did not change the statistical averages significantly.
Housing_Data["MeanRent_Cross"].describe()
Mean_Rent_by_Month = Housing_Data[["MeanRent_Apr", "MeanRent_May", "MeanRent_Jun", "MeanRent_Jul",
                        "MeanRent_Aug","MeanRent_Sep","MeanRent_Oct","MeanRent_Nov","MeanRent_Dec"]]
Housing_Data["MeanRent_Cross"] = Mean_Rent_by_Month.mean(axis = 1)
Housing_Data["MeanRent_Cross"].describe()

Housing_Data.reset_index(inplace = True, drop = True)

#Calculate the percentage of neighborhoods with fewer than 5 listings per month, sorted by month.
#We see a general trend of fewer neighborhoods hitting the 5 listings per month threshold.
# November and December levels are particularly high, with 11% and 17% respectively of neighborhoods below 5 listings per month.
#Rental activity declines in the winter, so this most likely explains the general decline in listings.
listings_threshold = Housing_Data[Listings_by_Month][Housing_Data[Listings_by_Month] > 5]
percent_missing = listings_threshold.isnull().sum() * 100 / len(listings_threshold)
percent_missing
#To reduce the rental median variance, I remove 4 neighborhoods that /
# fall below the monthly listing thresholds for two distinct months.
threshold_mask = ~pd.isnull(listings_threshold)
threshold_count = np.apply_along_axis(np.count_nonzero, 1, threshold_mask)
Housing_Data['Count'] = threshold_count
Housing_Data['Count']
Housing_Data = Housing_Data[Housing_Data['Count'] > 7]
Housing_Data['Count']


#For the 61 neighborhoods that pass the overall threshold count, I null the rental-mean data for months with fewer than 5 listings.
rent_month_list = ["MeanRent_Apr", "MeanRent_May", "MeanRent_Jun", "MeanRent_Jul",
                  "MeanRent_Aug","MeanRent_Sep","MeanRent_Oct","MeanRent_Nov","MeanRent_Dec"]
column_name_zip = dict(zip(Listings_by_Month, rent_month_list))
threshold_mask = threshold_mask.rename(columns = column_name_zip)
rental_mean_bool = Housing_Data[threshold_mask]
rental_mean_with_na = rental_mean_bool[[ "MeanRent_Apr", "MeanRent_May", "MeanRent_Jun", "MeanRent_Jul",
                  "MeanRent_Aug","MeanRent_Sep","MeanRent_Oct","MeanRent_Nov","MeanRent_Dec"]]
Clean_Housing_Data = pd.concat([Housing_Data,rental_mean_with_na], axis = 1)
all_cols = set(range(0,len(Clean_Housing_Data.columns)))
keep_cols = all_cols - set(range(12,21+1))
Clean_Housing_Data= Clean_Housing_Data.iloc[:, list(keep_cols)]

# In November, 4 out of 61 qualifying neighborhoods had fewer than 5 listings, while in December, 7/61 had fewer than 5.
#Dropping their mean rental data from the overall mean to reduce possibility of outliers skewing mean.
# print(Clean_Housing_Data[[ "MeanRent_Apr", "MeanRent_May", "MeanRent_Jun", "MeanRent_Jul",
#                   "MeanRent_Aug","MeanRent_Sep","MeanRent_Oct","MeanRent_Nov","MeanRent_Dec"]].isna().sum())
Mean_Rent_for_agg = Clean_Housing_Data[[ "MeanRent_Apr", "MeanRent_May", "MeanRent_Jun", "MeanRent_Jul",
                  "MeanRent_Aug","MeanRent_Sep","MeanRent_Oct","MeanRent_Nov","MeanRent_Dec"]]
Clean_Housing_Data["MeanRent_Cross"] = Mean_Rent_for_agg.mean(axis = 1, skipna = True)
Clean_Housing_Data['MeanRent_Diff'] = ((Clean_Housing_Data["MeanRent_Cross"] - Housing_Data["MeanRent_Cross"]) / Housing_Data["MeanRent_Cross"]) * 100
#print(Clean_Housing_Data[Clean_Housing_Data['MeanRent_Diff'] > 0].describe())
#Removing low-sample size months affected 8 neighborhoods. Removal increased these neighbhorhoods' aggregate mean rent by 1.6% on average.

#Creating a 3 month average of mean rental price to track price trend
Clean_Housing_Data['Apr-Jun_Mean'] = Clean_Housing_Data.iloc[:,12:15].mean(axis = 1, skipna = True)
Clean_Housing_Data['Jul-Sep_Mean'] = Clean_Housing_Data.iloc[:,15:18].mean(axis = 1, skipna = True)
Clean_Housing_Data['Oct-Dec_Mean'] = Clean_Housing_Data.iloc[:,18:21].mean(axis = 1, skipna = True)
#Detrend seasonal rent variation - 2% peak trough in Boston (https://www.renthop.com/studies/national/best-time-of-year-to-rent)
Clean_Housing_Data['Apr-Jun_Mean'] /= 1.02
Clean_Housing_Data['Jul-Sep_Mean'] /= 1.02

Clean_Housing_Data['First Delta'] = ((Clean_Housing_Data['Apr-Jun_Mean'] - Clean_Housing_Data['Jul-Sep_Mean']) / Clean_Housing_Data['Apr-Jun_Mean']) * 100
Clean_Housing_Data['Second Delta'] = ((Clean_Housing_Data['Jul-Sep_Mean'] - Clean_Housing_Data['Oct-Dec_Mean']) / Clean_Housing_Data['Jul-Sep_Mean']) * 100


print(Clean_Housing_Data['First Delta'].describe())
print(Clean_Housing_Data['Second Delta'].describe())

Clean_Housing_Data.reset_index(inplace = True, drop = True)
    # In order to plot the neighborhood data over Boston, I convert merge the dataset with an existing geopandas frame that contains the coordinates of each neighborhood. \\
    #Then convert the frame into JSON for use in Plotly.
Geo_Housing_Data = Geohousing.merge(Clean_Housing_Data, how = 'left',
                                           left_on = 'CTID1', right_on = 'CT_ID_10')

Geo_Housing_Data.drop(columns = ['CTID1','MeanRent_Diff'], axis = 1, inplace = True)
Geo_Housing_Data[['CT_ID_10', 'ListingsFreq_Cross', 'ListingsFreq_Apr', 'ListingsFreq_May', 'ListingsFreq_Jun',
                  'ListingsFreq_Jul', 'ListingsFreq_Aug', 'ListingsFreq_Sep',
                  'ListingsFreq_Oct', 'ListingsFreq_Nov', "ListingsFreq_Dec","First Delta","Second Delta"]] = Geo_Housing_Data[['CT_ID_10','ListingsFreq_Cross', 'ListingsFreq_Apr', 'ListingsFreq_May', 'ListingsFreq_Jun',
                     'ListingsFreq_Jul','ListingsFreq_Aug','ListingsFreq_Sep',
                     'ListingsFreq_Oct','ListingsFreq_Nov',"ListingsFreq_Dec","First Delta","Second Delta"]].fillna(0.0).astype(np.float64, errors = 'ignore')
print(Geo_Housing_Data)
#Convert frame into JSON string object
json_raw = json.loads(Geo_Housing_Data.to_json())
json_Housing_Data = json.dumps(json_raw)

#GeoJSON
geosource = GeoJSONDataSource(geojson = json_Housing_Data)
fig = px.choropleth_mapbox(Geo_Housing_Data,
                           geojson=Geo_Housing_Data.geometry,
                           locations=Geo_Housing_Data.index,
                           color="First Delta",
                           center={"lat": 42.32, "lon": -71.0589},
                           mapbox_style="open-street-map",
                           zoom=10,
                           opacity = .3,
                           color_discrete_map= {-10:''},
                           range_color = [-10,25],
                           hover_name = Geo_Housing_Data.CT_ID_10,
                           title = 'Change in Mean Rent Price, April-December 2020')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig.show()

print(Clean_Housing_Data)

#plt.show()
