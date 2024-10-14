import requests
import sqlite3
import time

# Konfiguracja połączenia do bazy
DB_PATH = "data.gpkg"
API_BASE_URL = "https://bdl.stat.gov.pl/api/v1/units"
REQUESTS_PER_SECOND_LIMIT = 4  # maksymalnie 4 zapytania na sekundę
PAGE_SIZE = 100  # liczba rekordów na stronę

# Funkcja do inicjalizacji tabeli
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teryt_codes (
            id INTEGER PRIMARY KEY,
            full_code TEXT NOT NULL unique,
            parent_code TEXT,
            name TEXT NOT NULL,
            kind TEXT,
            level INTEGER NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Funkcja do pobierania kodów TERYT z API i zapisywania ich bezpośrednio do bazy
def fetch_and_save_teryt_codes():
    page = 0
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    while True:
        url = f"{API_BASE_URL}?format=json&page={page}&page-size={PAGE_SIZE}"
        response = requests.get(url)

        # Obsługa odpowiedzi serwera
        if response.status_code == 200:
            data = response.json()
            print(f"Pobrano stronę {page} ile: {len(data['results'])}")
            for code in data["results"]:
                # Pobieranie wartości z JSONa API
                full_code = code.get("id")
                parent_code = code.get("parentId", None)
                name = code.get("name")
                kind = code.get("kind", None)
                level = code.get("level")

                # Wstawienie do bazy lub aktualizacja w razie konfliktu
                conn.execute('''
                    INSERT INTO teryt_codes (short_code, full_code, parent_code, name, kind, level)
                    VALUES ( ?, ?, ?, ?, ?)
                ''', ( full_code, parent_code, name, kind, level))

                # let's see what we have in the database
                x = conn.execute('SELECT count(*) FROM teryt_codes')
                print(x.fetchone())
            conn.commit()
            # Sprawdzenie, czy jest następna strona
            if "next" not in data["links"]:
                break

            page += 1
            time.sleep(1 / REQUESTS_PER_SECOND_LIMIT)  # ograniczenie zapytań
        else:
            print(f"Błąd {response.status_code}. Ponawiam próbę za 2 sekundy...")
            time.sleep(2)

    conn.close()

# Główna funkcja skryptu
def main():
    initialize_database()
    fetch_and_save_teryt_codes()

# Uruchomienie skryptu
if __name__ == "__main__":
    main()