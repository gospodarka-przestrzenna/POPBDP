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
import time
from .tokens import Tokens
from ..config import DB_PATH 

# Configuration
# DB_PATH = "data.gpkg"
API_BASE_URL = "https://bdl.stat.gov.pl/api/v1/units"
REQUESTS_PER_SECOND_LIMIT = 30  # maksymalnie 10 zapytania na sekundę


class Teryt(object):
    def __init__(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teryt_codes (
                    short_code TEXT NOT NULL,
                    full_code TEXT NOT NULL,
                    parent_code TEXT,
                    name TEXT NOT NULL,
                    kind TEXT,
                    level INTEGER NOT NULL,
                    language TEXT NOT NULL
                );
            ''')
            # Indexes
            #the short code is mostly used for searching
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS teryt_codes_short_code_idx ON teryt_codes (short_code);
            ''')
            # we will search also by parent_code that is search for children
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS teryt_codes_parent_code_idx ON teryt_codes (parent_code);
            ''')    
            # unique are fullcode with language
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS teryt_codes_full_code_language_idx ON teryt_codes (full_code, language);
            ''')
            conn.commit()

    def _add_teryt_code(self, short_code, full_code, parent_code, name, kind, level, lang):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO teryt_codes (short_code, full_code, parent_code, name, kind, level, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (short_code, full_code, parent_code, name, kind, level, lang))
            conn.commit()

    def _fetch_teryt_page(self,page,lang):
        
        token = Tokens().get_random_token()
        params = {
            "format": "json",
            "page": page,
            "lang": lang,
            "page-size": 100
        }
        headers = {"X-ClientId": token}
        response = requests.get(API_BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ERROR {response.status_code}.TOKEN {token}")
            Tokens().mark_token_failed(token)

    def fetch_and_save_teryt_codes(self,lang):
        page = 0
        while True:
            data = self._fetch_teryt_page(page,lang)
            if not data:
                
                time.sleep(5)
                continue
            for code in data["results"]:
                full_code = code.get("id")
                short_code = full_code[2:4]+full_code[7:11]
                if short_code.startswith('1431'):
                    continue #skip this code this is old capital city code
                parent_code = code.get("parentId", None)
                name = code.get("name")
                kind = code.get("kind", None)
                level = code.get("level")
                self._add_teryt_code(short_code, full_code, parent_code, name, kind, level, lang)
            if "next" not in data["links"]:
                break
            page += 1
            time.sleep(1 / REQUESTS_PER_SECOND_LIMIT)
    
    def code_to_name(self,shorter_code, type, lang):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM teryt_codes WHERE short_code = ? AND kind = ? AND language = ?", (shorter_code, type, lang))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def childrens(self,full_code,do_merge,lang):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    short_code,
                    full_code,
                    parent_code,
                    name,
                    kind,
                    level,
                    language
                FROM teryt_codes 
                WHERE parent_code = ? AND language = ?""", (full_code, lang))
            result = cursor.fetchall()
            if not result:
                return None
            for row in result:
                grand_childrens = self.childrens(row[1],do_merge,lang)
                
                type = row[1][-1]
                if grand_childrens and (type  == '0' or 
                                  ((type == '3' or row[1] == '071412865011') and not do_merge)):
                    yield (*row,grand_childrens)
                else:
                    yield (*row,None)

    def expand_code_or_rerurn_self(self,code,merge=False):
        """
        Expand code to full code or return self

        Args:
            codes (str): code to expand
        """
        final_result = []
        
        childrens = self.childrens(code,'pl') # get any language as we are interested in the code
        for child in childrens:
            if merge and code[-1] != '0':  
                continue
                
            final_result.append(child[1]) #full code
        
        if len(final_result) == 0:
            return [code]
        return final_result

    def final_codes(self,codes,merge=False):
        """
        Expand code list to finest codes
        """
        # while none of the code has 0 at the end
        if not codes:
            return []
        final_result = []
        to_expand = []


        for code in codes:
            # child iterator
            childrens = self.childrens(code, merge, 'pl')
            for child in childrens:
                print("CHILD", child)
                (full_code,  grand_childrens) = (child[1], child[-1])
                print("CHILD", full_code, grand_childrens)
                if grand_childrens is None:
                    final_result.append(full_code)
                    
                else:
                    to_expand.append(full_code)
        
        print("TO EXPAND", to_expand)
        print("FINAL", final_result)
        
        final_result.extend(self.final_codes(to_expand,merge))

        return final_result



    def recreate_teryt_table(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DROP TABLE IF EXISTS teryt_codes;
            ''')
            conn.commit()
        self.__init__()
        self.fetch_and_save_teryt_codes("pl")
        self.fetch_and_save_teryt_codes("en")
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # as a final step we have to remove the old capital city code
            # and every kind 2 that we have  3 for 
            cursor.execute('''
                DELETE FROM 
                           teryt_codes as t1 
                WHERE t1.short_code LIKE '1431%' OR (
                    t1.kind = '2' AND
                    EXISTS (
                            SELECT name FROM teryt_codes as t2
                            WHERE t1.short_code = t2.short_code AND
                            t1.kind = '2' AND
                            t2.kind != '2'
                           )
                    )''');      
            conn.commit()