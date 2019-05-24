import geopandas as gpd
import pandas as pd
import numpy as np
import zipfile
import urllib.request
import os
import json
from simpledbf import Dbf5
from fiona.crs import from_epsg
from shapely.geometry import MultiPolygon, Polygon, mapping

# Importing ENV variables
geoid = str(os.environ.get('GEOID'))
type_geom = os.environ.get('TYPE')
year = os.environ.get('year')

buffer_path = '/resources/inputs/buffers/'
county_path = '/resources/inputs/shapefiles/counties/'
block_path = '/resources/inputs/shapefiles/blocks/'
output_path = '/resources/graphs/' + geoid + '/'

county_file = os.environ.get('county_file') + '.shp'

# Getting list of states within the buffered county area
county_gdf = gpd.read_file(os.path.join(county_path, county_file))
county_gdf = county_gdf.to_crs(epsg = 4326)

buffer_gdf = gpd.read_file(os.path.join(buffer_path, geoid + '.geojson'))
buffer_gdf = buffer_gdf.to_crs(epsg = 4326)

intersect_gdf = gpd.sjoin(county_gdf, buffer_gdf, how='left', op='intersects')
needed_states = set(intersect_gdf.loc[pd.notnull(intersect_gdf['geoid'])]['STATEFP10'])

print('States intersecting buffer: ' + geoid)
print(needed_states)

# Downloading and unzipping the tracts for each needed state
loc_df = pd.DataFrame()
pop_df = pd.DataFrame()

for fip in needed_states:

    # Download block files with lat lon data
    loc_base_url = "https://www2.census.gov/geo/tiger/TIGER" + \
    str(year) + "/TABBLOCK/" + str(year) + "/"
    loc_base_file = "tl_" + str(year) + "_" + str(fip).zfill(2) + "_tabblock10"
    loc_zip_file = loc_base_file + ".zip"
    loc_dbf_file = loc_base_file + ".dbf"

    if not os.path.isfile(os.path.join(block_path, loc_zip_file)):
        print('Downloading block locations for state: ' + str(fip))
        urllib.request.urlretrieve(loc_base_url + loc_zip_file,
            os.path.join(block_path, loc_zip_file))

    if not os.path.isfile(os.path.join(block_path, loc_dbf_file)):
        print('Extracting block locations for state: ' + str(fip))
        tract_zip = zipfile.ZipFile(os.path.join(block_path, loc_zip_file))
        tract_zip.extractall(os.path.join(block_path))
        tract_zip.close()

    # Download block files with population data
    pop_base_url = "https://www2.census.gov/geo/tiger/TIGER" + \
    str(year) + "BLKPOPHU/"
    pop_base_file = "tabblock" + str(year) + "_" + str(fip).zfill(2) + "_pophu"
    pop_zip_file = pop_base_file + ".zip"
    pop_dbf_file = pop_base_file + ".dbf"

    if not os.path.isfile(os.path.join(block_path, pop_zip_file)):
        print('Downloading block populations for state: ' + str(fip))
        urllib.request.urlretrieve(pop_base_url + pop_zip_file,
            os.path.join(block_path, pop_zip_file))

    if not os.path.isfile(os.path.join(block_path, pop_dbf_file)):
        print('Extracting block populations for state: ' + str(fip))
        tract_zip = zipfile.ZipFile(os.path.join(block_path, pop_zip_file))
        tract_zip.extractall(os.path.join(block_path))
        tract_zip.close()

    loc_block_file = Dbf5(os.path.join(block_path, loc_dbf_file)).to_dataframe()
    loc_df = pd.concat([loc_df, loc_block_file])

    pop_block_file = Dbf5(os.path.join(block_path, pop_dbf_file)).to_dataframe()
    pop_df = pd.concat([pop_df, pop_block_file])


# Delete all unneeded block files to save space
print('Removing unncessary files...')
for item in os.listdir(block_path):
    if item.endswith(('.shp', '.shx', '.prj', '.shp.xml')):
        os.remove(os.path.join(block_path, item))

# Fix lat lon strings
print('Fixing lat/lon strings from DBFs...')
loc_df['INTPTLAT10'] = loc_df['INTPTLAT10'].str.replace('+', '').astype(float)
loc_df['INTPTLON10'] = loc_df['INTPTLON10'].astype(float)

# Find blocks in the buffer
print('Performing spatial intersection to find blocks in buffer...')
loc_gdf = gpd.GeoDataFrame(loc_df, geometry=gpd.points_from_xy(
    loc_df.INTPTLON10, loc_df.INTPTLAT10), crs=from_epsg(4326))
blocks_in_buff = gpd.sjoin(loc_gdf, buffer_gdf, how='left', op='intersects')
blocks_in_buff = blocks_in_buff.loc[pd.notnull(blocks_in_buff['geoid']), ['GEOID10', 'geometry']]

# Merge block pops with block points
print('Merging block locations and block populations...')
blocks_merged = blocks_in_buff.merge(
        pop_df[['BLOCKID10', 'POP10']],
        left_on = 'GEOID10',
        right_on = 'BLOCKID10',
        how = 'left')

# If type is block, clean up and save to CSV
if type_geom == 'BLOCK':
    print('Saving block centroids to CSV...')
    blocks_merged['X'] = blocks_merged.geometry.y
    blocks_merged['Y'] = blocks_merged.geometry.x
    blocks_merged = blocks_merged[['GEOID10', 'Y', 'X', 'POP10']]
    blocks_merged = blocks_merged.rename(
            index=str, columns={'GEOID10': 'GEOID', 'POP10': 'POP'})

    blocks_merged.to_csv(
            os.path.join(output_path, geoid + '-destinations.csv'), index=False)
    blocks_merged.loc[blocks_merged.GEOID.str.startswith(geoid, na=False)].to_csv(
            os.path.join(output_path, geoid + '-origins.csv'), index=False)

# If type is tract, find pop-weighted average of block centroids
# then clean up and save to CSV
elif type_geom == 'TRACT':
    print('Converting block centroids to Albers...')
    blocks_merged = blocks_merged.to_crs(epsg = 2163)
    blocks_merged['X'] = blocks_merged.geometry.x
    blocks_merged['Y'] = blocks_merged.geometry.y
    blocks_merged = blocks_merged[['GEOID10', 'Y', 'X', 'POP10']]
    blocks_merged = blocks_merged.rename(
            index=str, columns={'GEOID10': 'GEOID', 'POP10': 'POP'})

    print('Finding pop-weighted tract centroids...')
    blocks_merged['TRACT'] = blocks_merged['GEOID'].str.slice(0, 11)
    wm = lambda x: np.average(x, weights=blocks_merged.loc[x.index, "POP"] + 1)
    blocks_agg = blocks_merged.groupby('TRACT').agg(
            {'Y': wm, 'X': wm, 'POP': 'sum'}).reset_index()

    print('Saving tract centroids to CSV...')
    blocks_agg_gdf = gpd.GeoDataFrame(blocks_agg, geometry=gpd.points_from_xy(
        blocks_agg.X, blocks_agg.Y), crs=from_epsg(2163)).to_crs(4326)
    blocks_agg_gdf['X'] = blocks_agg_gdf.geometry.y
    blocks_agg_gdf['Y'] = blocks_agg_gdf.geometry.x
    blocks_agg_gdf = blocks_agg_gdf.drop(columns='geometry').rename(
            index=str, columns={'TRACT': 'GEOID'})

    blocks_agg_gdf.to_csv(
            os.path.join(output_path, geoid + '-destinations.csv'), index=False)
    blocks_agg_gdf.loc[blocks_agg_gdf.GEOID.str.startswith(geoid, na=False)].to_csv(
            os.path.join(output_path, geoid + '-origins.csv'), index=False)

else:
    pass

