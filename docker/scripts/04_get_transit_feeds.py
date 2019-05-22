import geopandas as gpd
import pandas as pd
import numpy as np
import requests as r
import urllib.request
import os
import json
from fiona.crs import from_epsg
from shapely.geometry import MultiPolygon, Polygon, mapping

# Importing ENV variables
geoid = str(os.environ.get('GEOID'))
type_geom = os.environ.get('TYPE')
api_key = os.environ.get('API_KEY')

# Setting output and input paths
buffer_path = '/resources/inputs/buffers/'
output_path = '/resources/outputs/' + geoid + '/'

# Reading in the appropriate buffered county
buffer_gdf = gpd.read_file(os.path.join(buffer_path, geoid + '.geojson'))
buffer_gdf = buffer_gdf.to_crs(epsg = 4326)

# Grabbing a list of feeds from the transit feeds API
print('Getting list of all feeds...')
feed_locations_url = 'https://api.transitfeeds.com/v1/getLocations?key=' + api_key
feed_locations_json = r.get(feed_locations_url).json()['results']['locations']

# Loading into a GeoDataFrame
print('Getting list of feeds in county buffer...')
feed_locations_df = pd.read_json(json.dumps(feed_locations_json))
feed_locations_gdf = gpd.GeoDataFrame(
        feed_locations_df,
        geometry=gpd.points_from_xy(
            feed_locations_df.lng,
            feed_locations_df.lat),
        crs=from_epsg(4326))

feeds_in_buff = gpd.sjoin(
        feed_locations_gdf, buffer_gdf,
        how='left', op='intersects')

feeds_in_buff = feeds_in_buff.loc[pd.notnull(feeds_in_buff['geoid'])]

# Get the URL of the latest feed version for all feeds in buffer
print('Getting feed download URLs...')
feeds = pd.DataFrame()
for loc_id in feeds_in_buff.id:
    feed_query_url = 'https://api.transitfeeds.com/v1/getFeeds?key=' + api_key + \
    '&location=' + str(loc_id) + '&descendants=1&page=1&limit=100&type=gtfs'
    feed_query_json = r.get(feed_query_url).json()['results']['feeds']
    feed_query_df = pd.read_json(json.dumps(feed_query_json))
    feeds = pd.concat([feeds, feed_query_df])

# Download all the feeds in the buffer
for full_id in feeds.id:
    print('Now downloading feed: ' + full_id)
    feed_url = 'https://api.transitfeeds.com/v1/getLatestFeedVersion?key=' + \
    api_key + '&feed=' + str(full_id)
    file_name = full_id.split('/')[0] + '.zip'
    urllib.request.urlretrieve(feed_url, os.path.join(output_path, file_name))
