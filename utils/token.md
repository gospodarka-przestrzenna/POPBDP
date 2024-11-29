# Tworzenie tabeli na tokeny


CREATE TABLE IF NOT EXISTS tokens (
    token TEXT PRIMARY KEY,
    last_failed_time INTEGER
);

# Insert do tabeli tokenów
INSERT INTO tokens (token, last_failed_time) VALUES (?, 0);

curl 'https://bdl.stat.gov.pl/api/v1/client?lang=pl' --data-raw 'Email=XYZ%40ABC.com'