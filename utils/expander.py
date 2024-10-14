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

from .teryt import Teryt
from .geometry import Geometry
from ..config import DB_PATH
from .translations import _, gus_language


class Expander(object):
    def __init__(self):
        pass
    
    def count_trailing_zeros(self,s):
        """
        Counts trailing zeros in a string. This is crucial for determining the level of the unit.

        Args:
            s (str): The string to analyze.

        Returns:
            int: The number of trailing zeros.
        """
        return len(s) - len(s.rstrip('0'))

    def expand_code(self, full_code) :
        """
        Expands a unit code to its children.

        Args:
            full_code (str): The full unit code.

        Returns:
            list: A list of tuples containing the full code, name, kind, and level of each child unit.
        """
        trailing_zeros = self.count_trailing_zeros(full_code)
        
        if trailing_zeros > 3:
            return self._expand_with_parent_code(full_code)
        elif trailing_zeros == 3:
            return self._expand_county(full_code)
        elif trailing_zeros == 0:
            return self._expand_with_parent_code(full_code)
        else:
            return None

    def _expand_with_parent_code(self, full_code):
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    full_code,
                    name,
                    kind,
                    level
                FROM teryt_codes
                WHERE parent_code = ? AND language = ?""", (full_code, gus_language))
            return cursor.fetchall()

    def _expand_county(self, full_code):
        voivodship = full_code[2:4]
        county = full_code[7:9]
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    code,
                    type
                FROM geometries
                WHERE code LIKE ?""", (voivodship + county + '%',))
            result = cursor.fetchall()
            
            if not result:
                return None
            
            final_result = []
            for row in result:
                
                if row[1] not in ['1','2','3']:
                    continue
                cursor.execute("""
                    SELECT 
                        full_code,
                        name,
                        kind,
                        level
                    FROM teryt_codes
                    WHERE short_code = ? AND kind = ? AND language = ?""", (row[0], row[1], gus_language))
                all_rows = cursor.fetchall()
                assert len(all_rows) == 1
                final_result.extend(all_rows)
            return final_result
        
    def expandable(self, full_code, do_merge):
        """
        Determines if a unit code is expandable.

        Args:
            full_code (str): The full unit code.
            do_merge (bool): Whether to merge the results.

        Returns:
            bool: True if the unit is expandable, False otherwise
        """
        if self.count_trailing_zeros(full_code) >= 3:
            return True
        elif self.count_trailing_zeros(full_code) == 0 and full_code[-1] == '3' and not do_merge:
            return True
        elif self.count_trailing_zeros(full_code) == 0 and full_code == '071412865011' and not do_merge:
            return True
        else:
            return False
    

    def codes_name_geometry(self, full_codes, do_merge):
        """
        Expands a list of unit codes to their children and retrieves their names and geometries.

        Args:
            full_codes (list): A list of full unit codes.
            do_merge (bool): Whether to merge the rural comunes inside.

        Returns:
            list: A list of tuples containing the full code, name, and geometry of each unit.
        """
        # code expands list as long as any item is expandable
        # later zips with geometry and name
        while any(self.expandable(code, do_merge) for code in full_codes):
            new_codes = []
            for code in full_codes:
                if self.expandable(code, do_merge):
                    for row in self.expand_code(code):
                        new_codes.append(row[0])
                else:
                    new_codes.append(code)
            full_codes = new_codes
        names = []
        geometries = []

        for full_code in full_codes:
            shorter_code = full_code[2:4]+full_code[7:11]
            kind = full_code[-1]

            names.append(Teryt().code_to_name(shorter_code,kind, gus_language))
            geometries.append(Geometry().geometry_from_code(shorter_code, kind))

        return zip(full_codes, names, geometries)
