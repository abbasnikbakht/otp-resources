import geopandas as gpd
import pandas as pd
import zipfile
import urllib.request
import os
import json
from simpledbf import Dbf5
from fiona.crs import from_epsg
from shapely.geometry import MultiPolygon, Polygon, mapping

# Importing ENV variables
geoid = os.environ.get('GEOID')
year = os.environ.get('year')

buffer_path = '/resources/inputs/buffers/'
county_path = '/resources/inputs/shapefiles/counties/'
county_file = os.environ.get('county_file') + '.shp'
block_path = '/resources/inputs/shapefiles/blocks/'

# Getting list of states within the buffered county area
county_gdf = gpd.read_file(os.path.join(county_path, county_file))
county_gdf = county_gdf.to_crs(epsg = 4326)

buffer_gdf = gpd.read_file(os.path.join(buffer_path, str(geoid) + '.geojson'))
buffer_gdf = buffer_gdf.to_crs(epsg = 4326)

intersect_gdf = gpd.sjoin(county_gdf, buffer_gdf, how='left', op='intersects')
needed_states = set(intersect_gdf.loc[pd.notnull(intersect_gdf['geoid'])]['STATEFP10'])

print('States intersecting buffer: ' + str(geoid))
print(needed_states)

# Downloading and unzipping the tracts for each needed state
df = pd.DataFrame()

for fip in needed_states:
    base_url = "https://www2.census.gov/geo/tiger/TIGER" + \
    str(year) + "/TABBLOCK/" + str(year) + "/"
    base_file = "tl_" + str(year) + "_" + str(fip).zfill(2) + "_tabblock10"
    zip_file = base_file + ".zip"
    dbf_file = base_file + ".dbf"

    if not os.path.isfile(os.path.join(block_path, zip_file)):
        print('Downloading state: ' + str(fip))
        urllib.request.urlretrieve(base_url + zip_file,
            os.path.join(block_path, zip_file))

    if not os.path.isfile(os.path.join(block_path, dbf_file)):
        print('Extracting state: ' + str(fip))
        tract_zip = zipfile.ZipFile(os.path.join(block_path, zip_file))
        tract_zip.extractall(os.path.join(block_path))
        tract_zip.close()

    block_file = Dbf5(os.path.join(block_path, dbf_file)).to_dataframe()
    df = pd.concat([df, block_file])

df['INTPTLAT10'] = df['INTPTLAT10'].str.replace('+', '').astype(float)
df['INTPTLON10'] = df['INTPTLON10'].astype(float)

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
    df.INTPTLON10, df.INTPTLON10)).to_crs(epsg = 4326)
blocks_in_buff = gpd.sjoin(gdf, buffer_gdf, how='left', op='intersects')
blocks_in_buff = blocks_in_buff.loc[pd.notnull(blocks_in_buff['geoid']), ['GEOID10', 'geometry']]



print(blocks_in_buff.columns)

# Figure out how to merge lat/lon and pop
# Figure out how to calc pop-weighted tracts






# for needed states load files
# get centroids inside buffer gdf
# save centroids to CSV geoid, X, Y

