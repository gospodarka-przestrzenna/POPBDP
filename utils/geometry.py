# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2024 Wawrzyniec Zipser, Maciej Kamiński (maciej.kaminski@pwr.edu.pl)
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
###############################################################################
__author__ = 'Wawrzyniec Zipser, Maciej Kamiński Politechnika Wrocławska'

import requests
import sqlite3
import geopandas as gpd
import pandas as pd
from io import BytesIO

DB_PATH = "data.gpkg"
wfs_url = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/PRG/WFS/AdministrativeBoundaries'

class Geometry(object):
    def __init__(self):
        pass
        # database schema
        # geometry is just simple WKB BLOB geometry
        
        # self.cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS geometries (
        #         code TEXT NOT NULL,
        #         type TEXT NOT NULL,
        #         geometry GEOMETRY NOT NULL
        #     );
        # ''')
        # Indexes


    def fetch_geometry_finest(self, code, type):
        type=int(type)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT type,geometry
                FROM geometries
                WHERE code = ?
            ''', (code, type))
            row = cursor.fetchone()
            if row is None:
                return None
        bdot_type,geometry = row
        bdot_type = int(bdot_type)
        if type in [1,2,4,8] and type == bdot_type:
            return geometry, bdot_type
        if bdot_type == 3 and type in [4,5]:
            # compute diff
            return geometry, type
        
        return None, None

    def fetch_geometry_merged(self, code, type):
        pass

    def fetch_commune_geometries(self):
        layer_name = 'ms:A03_Granice_gmin'
        params = {
            'service': 'WFS',
            'request': 'GetFeature',
            'version': '2.0.0',
            'typename': layer_name,
            'outputFormat': 'application/gml+xml; version=3.2',

        }
        response = requests.get(wfs_url, params=params)

        if response.status_code != 200:
            print('Failed to fetch geometries')
            return
        # Load the response into a GeoDataFrame
        gdf = gpd.read_file(BytesIO(response.content))

        # drop columns that are not needed
        gdf = gdf[['JPT_KOD_JE', 'geometry']]

        # Create a column 'code' from the first six characters
        gdf['code'] = gdf['JPT_KOD_JE'].str[:6]

        # Create a column 'type' from the seventh character
        gdf['type'] = gdf['JPT_KOD_JE'].str[6]

        # Remove the 'JPT_KOD_JE' column
        gdf = gdf.drop(columns=['JPT_KOD_JE'])
        
        gdf['geometry_wkb'] = gdf['geometry'].apply(lambda geom: geom.wkb)
        gdf = gdf.drop(columns=['geometry'])
        gdf = gdf.rename(columns={'geometry_wkb': 'geometry'})
        gdf_to_save = gdf[['code', 'type', 'geometry']]

        return gdf_to_save  
    
    def fetch_city_geometries(self):
        layer_name = 'ms:A04_Granice_miast'
        params = {
            'service': 'WFS',
            'request': 'GetFeature',
            'version': '2.0.0',
            'typename': layer_name,
            'outputFormat': 'application/gml+xml; version=3.2',

        }
        response = requests.get(wfs_url, params=params)

        if response.status_code != 200:
            print('Failed to fetch geometries')
            return
        # Load the response into a GeoDataFrame
        gdf = gpd.read_file(BytesIO(response.content))

        # drop columns that are not needed
        gdf = gdf[['KODJEDNO_1', 'geometry']]

        # Create a column 'code' from the first six characters
        gdf['code'] = gdf['KODJEDNO_1'].str[:6]

        # Create a column 'type' from the eight character after _
        gdf['type'] = gdf['KODJEDNO_1'].str[7]

        # Remove the 'KODJEDNO_1' column
        gdf = gdf.drop(columns=['KODJEDNO_1'])
        
        gdf['geometry_wkb'] = gdf['geometry'].apply(lambda geom: geom.wkb)
        gdf = gdf.drop(columns=['geometry'])
        gdf = gdf.rename(columns={'geometry_wkb': 'geometry'})
        gdf_to_save = gdf[['code', 'type', 'geometry']]

        return gdf_to_save  
    

    def fetch_geometries(self):
        communes = self.fetch_commune_geometries()
        cities = self.fetch_city_geometries()
            # Połącz DataFrame, 'communes' jako pierwszy
        combined_gdf = pd.concat([communes, cities], ignore_index=True)

        # Usuń duplikaty na podstawie 'code' i 'type', zachowując pierwsze wystąpienie (z 'communes')
        combined_gdf = combined_gdf.drop_duplicates(subset=['code', 'type'], keep='first')

        with sqlite3.connect(DB_PATH) as conn:
            combined_gdf.to_sql('geometries', conn, if_exists='replace', index=False)    
            # Utwórz indeks na kolumnie 'code'
            conn.execute("CREATE INDEX idx_code ON geometries (code);")

        # Utwórz unikalny indeks na parze 'code' i 'type'
            conn.execute("CREATE UNIQUE INDEX idx_code_type ON geometries (code, type);")