import geopandas as gpd
import zipfile
import os
import fiona
import json
from fiona.crs import from_epsg
from shapely.geometry import MultiPolygon, Polygon, mapping

buffer = os.getenv('BUFFER_SIZE_M', 100000)
schema = {
  'geometry': 'MultiPolygon',
  'properties': {'geoid': 'int'},
}

county_path = '/resources/inputs/shapefiles/counties/'
county_file = os.environ.get('county_file') + '.shp'
buffer_path = '/resources/inputs/buffers/'

# Convert shapefile CRS to Albers, buffer, then convert the buffered
# counties back to 83. Necessary for clipping with osmium

print("Now buffering all US counties by " + str(buffer) + "meters...")

gdf = gpd.read_file(os.path.join(county_path, county_file))
gdf = gdf.to_crs(epsg = 2163)
gdf['geometry'] = gdf.geometry.buffer(buffer)
gdf['geometry'] = [MultiPolygon([feature]) if type(feature) == Polygon \
    else feature for feature in gdf["geometry"]]
gdf = gdf.to_crs(epsg = 4326)

# Save each county as a separate GeoJSON to use as a boundary
# file for osmium clipping
for index, row in gdf.iterrows():
    with fiona.open(os.path.join(buffer_path, '{}.geojson'.format(row['GEOID10'])), 'w',
        crs=from_epsg(4326), driver='GeoJSON', schema=schema) as output:
        output.write({
            'geometry': mapping(row['geometry']),
            'properties': {'geoid': row['GEOID10']}
        })
