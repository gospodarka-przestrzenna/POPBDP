import requests
import sqlite3
import time

# Konfiguracja bazy danych i API
DB_PATH = "data.gpkg"
API_BASE_URL_VARIABLES = "https://bdl.stat.gov.pl/api/v1/Variables"
REQUESTS_PER_MINUTE_LIMIT = 6
PAGE_SIZE = 100

# Funkcja do inicjalizacji tabeli zmiennych
def initialize_variables_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela zmiennych
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variables (
            id INTEGER PRIMARY KEY,
            subject_id TEXT,
            n1 TEXT,
            n2 TEXT,
            n3 TEXT,
            n4 TEXT,
            n5 TEXT,
            n6 TEXT,    
            level INTEGER,
            measure_unit_id INTEGER,
            measure_unit_name TEXT
        );
    ''')

    #conn.execute("UPDATE subjects SET status = 'pending' WHERE has_variables = 1")

    conn.commit()
    conn.close()

# Funkcja do pobierania tematów `pending` z `has_variables = true`
def fetch_pending_subjects_with_variables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subjects WHERE has_variables = 1 AND status = 'pending'")
    subjects = cursor.fetchall()
    conn.close()
    return [subject[0] for subject in subjects]

# Funkcja do pobierania i zapisywania zmiennych dla danego tematu
def fetch_and_save_variables_for_subject(subject_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    page = 0

    while True:
        # Budowanie URL z parametrem `subject-id`
        url = f"{API_BASE_URL_VARIABLES}?subject-id={subject_id}&lang=pl&format=json&page-size={PAGE_SIZE}&page={page}"

        time.sleep(60 / REQUESTS_PER_MINUTE_LIMIT)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(f"Pobrano stronę {page} dla tematu {subject_id}")
            # Zapis zmiennych z wyniku zapytania
            for item in data["results"]:
                cursor.execute('''
                    INSERT OR REPLACE INTO variables (id, subject_id, n1, n2,n3,n4,n5,n6, level, measure_unit_id, measure_unit_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?)
                ''', (
                    item["id"],
                    item["subjectId"],
                    item.get("n1"),
                    item.get("n2"),
                    item.get("n3"),
                    item.get("n4"),
                    item.get("n5"),
                    item.get("n6"),
                    item["level"],
                    item["measureUnitId"],
                    item["measureUnitName"]
                ))

            conn.commit()

            # Sprawdzenie, czy jest więcej stron
            if "next" not in data["links"]:
                # Aktualizacja statusu tematu na `ok`, gdy pobieranie zmiennych się zakończy
                cursor.execute("UPDATE subjects SET status = 'ok' WHERE id = ?", (subject_id,))
                conn.commit()
                break

            page += 1
            # Ograniczenie zapytań na minutę


        else:
            print(f"Błąd {response.status_code}. Ponawiam próbę za 60 sekund...")
            time.sleep(60)

    conn.close()

# Funkcja główna do uruchamiania procesu pobierania zmiennych
def main():
    initialize_variables_table()

    # Pobieranie wszystkich tematów `pending` z `has_variables = true`
    subjects_with_variables = fetch_pending_subjects_with_variables()

    # Przetwarzanie każdego tematu z `pending`
    for subject_id in subjects_with_variables:
        fetch_and_save_variables_for_subject(subject_id)

# Uruchomienie skryptu
if __name__ == "__main__":
    main()