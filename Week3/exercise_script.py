import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import pandas as pd


# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


plt.ion()

# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file('data_files/Counties.shp')
print(counties.head())
counties.crs
counties_utm = counties.to_crs(epsg=32629)
print(counties_utm.head())
counties_utm.crs

wards = gpd.read_file('data_files/NI_Wards.shp')
wards.crs
wards_utm = wards.to_crs(epsg=32629)
print(wards_utm.head())
wards_utm.crs

# your analysis goes here...
join = gpd.sjoin(wards_utm, counties_utm, how='inner', lsuffix='left', rsuffix='right')
print(join)

summary = join.groupby(['CountyName'])['Population'].sum()

print(summary)

# identify wards located in more than one county

clipped = []
for county in counties_utm['CountyName'].unique():
    tmp_clip = gpd.clip(wards_utm, counties_utm[counties_utm['CountyName'] == county])
    for i, row in tmp_clip.iterrows():
        tmp_clip.loc[i, 'Population'] = row['geometry'].length
        tmp_clip.loc[i, 'CountyName'] = county
    clipped.append(tmp_clip)

    clipped_gdf = gpd.GeoDataFrame(pd.concat(clipped))
    clip_total = clipped_gdf['Population'].sum()

    print(clip_total)
# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = generate_handles([''], ['none'], edge='r')

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
# fig.savefig('sample_map.png', dpi=300, bbox_inches='tight')
