import folium
m = folium.Map(location=[42.32,-71.0589], tiles='openstreetmap', zoom_start=10)
folium.Choropleth(
    geo_data=json_Housing_Data,
    name="choropleth",
    data=json_Housing_Data,
    columns=['CT_ID_10','First Delta'],
    key_on="feature.CT_ID_10",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Unemployment Rate (%)",
).add_to(m)

folium.LayerControl().add_to(m)


m.save('boston.html')


from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Slider, HoverTool
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column
from bokeh.tile_providers import get_provider, Vendors
#Color palette from ColorBrewer
palette = brewer['OrRd'][5]
palette = palette[::-1]

#Create numerical scale
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')

tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}

#Adds interactive hovering
hover = HoverTool(tooltips = [ ('Neighborhood','@CT_ID_10'),('Mean Rent Change - Spring to Summer', '@{First Delta}'),
                               ('Mean Rent Change - Summer to Winter', '@{Second Delta}')])


p = figure(title = 'Change in Mean Rent Price, April-December 2020', plot_height = 600 , plot_width = 950,
           toolbar_location = None, tools = [hover], sizing_mode = 'scale_width')
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Legend scale
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
p.add_layout(color_bar, 'below')
#Plotting data
p.patches('xs','ys', source = geosource,fill_color = {'field' :'First Delta',
        'transform' : color_mapper},line_color = 'black', line_width = 0.25, fill_alpha = 1)

tile_provider = get_provider(Vendors.OSM)
p.add_tile(tile_provider)



show(p)