import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import pandas as pd
from bokeh.plotting import save, figure
from bokeh.models import GeoJSONDataSource
Geohousing = gpd.read_file('/Users/nick/Documents/Boston housing/Craigslist_CT/CRAIGSLIST_CT.shp')
pd.set_option('display.max_columns', 30)
#print(Geohousing.columns)
Geohousing = Geohousing[Geohousing["COUNT"] == "SUFFOLK"].reset_index()
Geohousing = Geohousing[['CTID1', 'geometry']]
#Geohousing.plot()
#plt.show()
#print(Geohousing)
Geohousing['CTID1'] = Geohousing['CTID1'].astype('int64')
#print(Geohousing['CTID1'].dtype)
print(Geohousing['CTID1'])