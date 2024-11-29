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


import sqlite3
import binascii
from .config import DB_PATH
from qgis.core import QgsVectorLayer, QgsField, QgsGeometry, QgsFeature, QgsProject
from qgis.PyQt.QtCore import QVariant
from .translations import _,gus_language
from .utils.teryt import Teryt    

class Layer(QgsVectorLayer):
    """
    Represents a QGIS memory layer for managing territorial data.
    Includes methods for adding features, attributes, and processing geometry.
    """
    def __init__(self, layer_name):
        """
        Initializes the layer with default fields and configurations.

        Args:
            layer_name (str): The name of the memory layer.
        """
        super().__init__("MultiPolygon?crs=EPSG:2180", layer_name, "memory")
        self.provider = self.dataProvider()

        # Index to map long unit codes to their corresponding features
        self.feature_index = {}  # {long_code: QgsFeature}

        # Maps column names to their respective index positions
        self.column_index = {
            "short_code": 0,
            "type": 1,
            "name": 2
        }

        # Add default attributes to the layer
        self.provider.addAttributes([
            QgsField(_("short_code"), QVariant.String),
            QgsField(_("type"), QVariant.String),
            QgsField(_("name"), QVariant.String)
        ])
        self.updateFields()

        # Tracks years and their corresponding column indices
        self.year_columns = {}

    def create_new_feature(self, unit_id):
        """
        Creates a new feature for the specified unit and adds it to the layer.

        Args:
            unit_id (str): The unique identifier of the unit.
            get_geom_n_type (function): Function to retrieve geometry and type.

        Returns:
            bool: True if the feature was created successfully, False otherwise.
        """
        shorter_code = unit_id[2:4] + unit_id[7:11]
        gus_type = unit_id[11]

        # Retrieve geometry and type for the unit
        print("create_new_feature",shorter_code+gus_type)
        geometry, bdot_type = self.get_geometry(shorter_code+gus_type)
        if geometry is None:
            return False

        # Create a new feature and set its attributes
        feature = QgsFeature()
        self.feature_index[unit_id[:11] + bdot_type] = feature

        feature.setGeometry(geometry)
        name = Teryt().code_to_name(shorter_code,gus_type, gus_language)
        if name is None:
            print(f"Name not found for code: {shorter_code+gus_type}")

        feature.setAttributes([shorter_code, bdot_type, name])

        # Add the feature to the provider
        self.provider.addFeature(feature)
        return True

    def add_GUS_data(self, unit_id, year, value, column_prefix):
        """
        Adds data for a specific unit and year to the layer.

        Args:
            unit_id (str): The unit identifier.
            year (str): The year for the data.
            value (float): The value to add.
            column_prefix (str): Prefix for the column name.
            get_geom_n_type (function): Geometry and type retrieval function.
        """
        year = str(year)

        if unit_id not in self.feature_index and unit_id[-1] == '2':
            # probably we add the data to '...3'
            print(f"Adding {unit_id} to '...3'")
            unit_id = unit_id[:-1] + '3'

        if unit_id not in self.feature_index:
            print(f"Dodawanie {unit_id} nie było przewidziane")
            return

        if year not in self.year_columns:
            self.year_columns[year] = []

        column = f"{column_prefix} ({year})"
        if column not in self.column_index:
            self.column_index[column] = len(self.column_index)
            self.provider.addAttributes([QgsField(column, QVariant.Double)])
            self.updateFields()

            for feature in self.feature_index.values():
                feature.resizeAttributes(len(self.column_index))
                self.provider.changeAttributeValues({feature.id(): {self.column_index[column]: value}})

        self.year_columns[year].append(self.column_index[column])
        feature = self.feature_index[unit_id]
        self.provider.changeAttributeValues({feature.id(): {self.column_index[column]: value}})

    # def get_gmina_geometry_merged(self, short_code, gus_type):
    #     """
    #     Retrieves merged geometry for a unit.

    #     Args:
    #         short_code (str): Short code of the unit.
    #         gus_type (str): GUS type of the unit.

    #     Returns:
    #         tuple: Geometry and type of the unit.
    #     """
    #     with sqlite3.connect(DB_PATH) as conn:
    #         cursor = conn.cursor()
    #         if gus_type in ['4', '5']:
    #             return None, None

    #         cursor.execute("""
    #             SELECT hex(geom), type
    #             FROM geometries
    #             WHERE code = ? 
    #         """, (short_code,))
    #         result = cursor.fetchone()
    #         if not result:
    #             raise ValueError(_("Geometry not found for code: {short_code} {gus_type}").format(short_code=short_code, gus_type=gus_type))

    #         hex_geom, type = result
    #         wkb_hex = hex_geom[80:]
    #         wkb_bytes = binascii.unhexlify(wkb_hex)
    #         geometry = QgsGeometry()
    #         geometry.fromWkb(wkb_bytes)
    #         return geometry, type

    def _hex_to_geometry(self, hex_geom):
        wkb_hex = hex_geom#[80:]
        wkb_bytes = binascii.unhexlify(wkb_hex)
        geometry = QgsGeometry()
        geometry.fromWkb(wkb_bytes)
        return geometry
    
    def get_geometry(self, short_code):

        gus_type  = short_code[-1]
        outline = short_code[:-1]

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hex(geometry),type
                FROM geometries
                WHERE code = ?
            """, (outline,))
            result = cursor.fetchall()
            if not result:
                raise ValueError(_("Geometry not found for code: {short_code} {gus_type}").format(short_code=short_code, gus_type=gus_type))
            
            if len(result) == 1:
                hex_geom,type = result[0]
                geometry = self._hex_to_geometry(hex_geom)
                assert type == gus_type
                return geometry, type

            elif len(result) == 2:
                geometry1,type1 = result[0]
                geometry2,type2 = result[1]

                assert '3' in [type1,type2]
                if type1 == '3':
                    urban_rural=self._hex_to_geometry(geometry1)
                    urban = self._hex_to_geometry(geometry2)
                else:
                    urban_rural=self._hex_to_geometry(geometry2)
                    urban = self._hex_to_geometry(geometry1)
            else:
                raise ValueError(_("To much geometreis_"))
            print ("UR")
            if gus_type == '3':
                return urban_rural, '3'
            if gus_type == '4':
                return urban, '4'
            if gus_type == '5':
                rural = urban_rural.difference(urban)
                return rural, '5'
        
        print("None")
        return None, None        
    # def get_gmina_geometry_splitted(self, short_code, gus_type):
    #     """
    #     Retrieves individual geometries for rural and urban areas.

    #     Args:
    #         short_code (str): Short code of the unit.
    #         gus_type (str): GUS type of the unit.

    #     Returns:
    #         tuple: Geometry and type of the unit.
    #     """
    #     with sqlite3.connect(DB_PATH) as conn:
    #         cursor = conn.cursor()
    #         if gus_type == '3':
    #             return None, None

    #         # Retrieve city geometry
    #         if gus_type in ['4', '5']:
    #             cursor.execute("""
    #                 SELECT hex(geom), type
    #                 FROM geometries
    #                 WHERE code = ?
    #             """, (short_code,))
    #             result = cursor.fetchone()
    #             if not result:
    #                 raise ValueError(_("Geometry not found for code: {short_code} {gus_type}").format(short_code=short_code, gus_type=gus_type))
    #             hex_geom, _ = result
    #             wkb_hex = hex_geom[80:]
    #             wkb_bytes = binascii.unhexlify(wkb_hex)
    #             city_geometry = QgsGeometry()
    #             city_geometry.fromWkb(wkb_bytes)

    #         # Retrieve commune geometry
    #         if gus_type in ['1', '2', '5']:
    #             cursor.execute("""
    #                 SELECT hex(geom), typ
    #                 FROM gminy
    #                 WHERE code = ?
    #             """, (short_code,))
    #             result = cursor.fetchone()
    #             if not result:
    #                 raise ValueError(_("Geometry not found for code: {short_code} {gus_type}").format(short_code=short_code, gus_type=gus_type))
    #             hex_geom, bdot_type = result
    #             wkb_hex = hex_geom[80:]
    #             wkb_bytes = binascii.unhexlify(wkb_hex)
    #             gmina_geometry = QgsGeometry()
    #             gmina_geometry.fromWkb(wkb_bytes)

    #         if gus_type == '4':
    #             return city_geometry, '4'
    #         if gus_type == '5':
    #             rural_geometry = gmina_geometry.difference(city_geometry)
    #             return rural_geometry, '5'

    #         return gmina_geometry, bdot_type

    def get_name(self, short_code, type):
        """
        Retrieves the name for a specific unit.

        Args:
            short_code (str): Short code of the unit.
            type (str): Type of the unit.

        Returns:
            str: The name of the unit.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name
                FROM teryt_codes
                WHERE short_code = ?
            """, (short_code + type,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(_("Name not found for code: {short_code} {type}").format(short_code=short_code, type=type))
            return result[0]

    def remove_unwanted_years_columns(self, years):
        """
        Removes columns corresponding to unwanted years.

        Args:
            years (list): List of years to retain.
        """
        to_delete = []
        for year, columns in self.year_columns.items():
            if year not in years:
                to_delete.extend(columns)

        self.year_columns = {year: columns for year, columns in self.year_columns.items() if year in years}
        self.provider.deleteAttributes(to_delete)
        self.updateFields()

        # Rebuild column index after deletion
        self.column_index = {field.name(): index for index, field in enumerate(self.fields())}
