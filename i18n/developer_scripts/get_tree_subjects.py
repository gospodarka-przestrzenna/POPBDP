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

# Konfiguracja bazy danych i API
DB_PATH = "data.gpkg"
API_BASE_URL_SUBJECTS = "https://bdl.stat.gov.pl/api/v1/subjects"
REQUESTS_PER_MINUTE_LIMIT = 4
PAGE_SIZE = 100

# Funkcja do inicjalizacji tabeli tematów
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela tematów (struktura drzewa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            parent_id TEXT,
            name TEXT NOT NULL,
            has_variables BOOLEAN,
            status TEXT DEFAULT 'pending' -- status dla odtworzenia sesji: pending, completed, failed
        );
    ''')

    conn.commit()
    conn.close()

# Funkcja do pobierania tematów głównych (bez `parent_id`)
def fetch_and_save_subjects_main_subjects():
    fetch_and_save_subjects(parent_id=None)

# Funkcja do pobierania pojedynczego `pending` tematu
def fetch_pending_subject():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subjects WHERE has_variables = 0 and status = 'pending' LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Funkcja do pobierania i zapisywania tematów z obsługą przerwań
def fetch_and_save_subjects(parent_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    page = 0

    while True:
        # Budowanie URL z odpowiednimi parametrami
        url = f"{API_BASE_URL_SUBJECTS}?lang=pl&format=json&page-size={PAGE_SIZE}&page={page}"
        if parent_id:
            url += f"&parent-id={parent_id}"

        time.sleep(60 / REQUESTS_PER_MINUTE_LIMIT)  # ograniczenie zapytań
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Pobrano stronę {page} z {parent_id}")
            for item in data["results"]:
                # Zapis tematu i ustawienie `pending` tylko dla tych, które mają `level` = 6
                if 6 in item["levels"]:
                    cursor.execute('''
                        INSERT OR REPLACE INTO subjects (id, parent_id, name, has_variables, status)
                        VALUES (?, ?, ?, ?, 'pending')
                    ''', (
                        item["id"],
                        parent_id,
                        item["name"],
                        item["hasVariables"],
                    ))

            conn.commit()

            # Sprawdzenie, czy jest więcej stron
            if "next" not in data["links"]:
                if parent_id:
                     # Aktualizacja statusu tematu na `ok`, gdy pobieranie zmiennych się zakończy
                    cursor.execute("UPDATE subjects SET status = 'ok' WHERE id = ?", (parent_id,))
                    conn.commit()
                break

            page += 1
            
        else:
            print(f"Błąd {response.status_code}. Ponawiam próbę za 60 sekund...")
            time.sleep(60)

    conn.close()

# Funkcja główna do uruchamiania procesu pobierania tematów
def main():
    initialize_database()

    # Jeśli tabela jest pusta, pobieramy tematy główne
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        fetch_and_save_subjects_main_subjects()
    conn.close()

    # Sprawdzanie i kontynuowanie tematów z `pending`
    pending_subject = fetch_pending_subject()
    while pending_subject:
        fetch_and_save_subjects(pending_subject)
        pending_subject = fetch_pending_subject()

# Uruchomienie skryptu
if __name__ == "__main__":
    main()