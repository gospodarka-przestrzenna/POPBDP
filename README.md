# QuickBDL
 - [Wprowadzenie po polsku](#pl)
 - [For English introduction click here](#en)
 
## PL
    Pobieranie obiektów polskich baz danych publicznych

### Opis
Ta wtyczka umożliwia pobieranie danych z GUS (Głównego Urzędu Statystycznego) w celu analizy i wizualizacji w środowisku QGIS. Użytkownik może wybrać interesujące go obszary terytorialne, wskaźniki statystyczne oraz zakres lat, dla których dane mają zostać pobrane. W rezultacie tworzona jest warstwa wektorowa, w której każda jednostka terytorialna jest reprezentowana jako geometria, a wybrane wskaźniki są przypisane jako atrybuty w kolumnach. Dzięki temu dane statystyczne można łatwo przetwarzać, analizować i prezentować w kontekście przestrzennym. Wtyczka wspiera integrację z serwisem API GUS oraz zapewnia dynamiczne tworzenie warstw na podstawie wybranych kryteriów. Jest to narzędzie przydatne zarówno dla analityków, jak i instytucji badawczych, które potrzebują łatwego dostępu do danych statystycznych w kontekście geograficznym.

#### Przed pierwszym uruchomieniem wtyczki
Aby wtyczka działała poprawnie, konieczne jest lokalne pobranie bazy danych obiektów przestrzennych. Baza ta jest uproszczoną i przyspieszoną kopią danych dostępnych w BDOT (Bank Danych Obiektów Topograficznych). Po instalacji wtyczka automatycznie sprawdzi, czy baza danych znajduje się w odpowiedniej lokalizacji. W przypadku jej braku zostanie ona pobrana z internetu. Proces ten wymaga aktywnego połączenia z siecią i może zająć kilka minut w zależności od szybkości łącza.
Uwaga: Wtyczka nie może działać bez internetu.
### Przykładowe użycie wtyczki
#### 1. Wybierz jednostki terytorialne, dla których chcesz pobrać dane

Pierwszym krokiem jest wybór interesujących jednostek terytorialnych. Wtyczka umożliwia wybór na różnych poziomach hierarchii administracyjnej, np. województwa, powiaty, gminy. Zaleca się wybieranie jednostek wyższego rzędu (np. powiatów zamiast pojedynczych gmin), aby ograniczyć liczbę zapytań do API i przyspieszyć proces pobierania danych.
<img width="804" alt="Zrzut ekranu 2024-11-25 o 12 50 50" src="https://github.com/user-attachments/assets/56d20c40-9ed8-404e-b864-d0d2fe33bfcd">

#### 2. Wybierz dane do pobrania
Następnie należy wybrać wskaźniki statystyczne, które mają zostać pobrane. Wskaźniki są grupowane tematycznie, co ułatwia ich odnalezienie. Możesz wybrać kilka wskaźników, które zostaną zapisane jako oddzielne kolumny w warstwie.
<img width="1000" alt="Zrzut ekranu 2024-11-25 o 12 54 26" src="https://github.com/user-attachments/assets/a85026c4-fd5b-4b6a-b179-ee9f0e94218f">

#### 3. Określ nazwy kolumn
Dla każdego wybranego wskaźnika należy określić nazwę kolumny, w której dane zostaną zapisane. Wtyczka automatycznie proponuje nazwy, jednak warto je skrócić do maksymalnie 20 znaków, aby zachować przejrzystość tabeli.
<img width="1003" alt="Zrzut ekranu 2024-11-25 o 12 56 35" src="https://github.com/user-attachments/assets/9e0436a7-03d8-4494-bdf7-86902cba75ab">
Dzięki temu nazwy kolumn będą czytelne i łatwe do wykorzystania w analizie danych.
<img width="1005" alt="Zrzut ekranu 2024-11-25 o 12 57 21" src="https://github.com/user-attachments/assets/5f1fd63b-59cc-43fa-855c-0f0f5b8836f0">

#### 4. Pobieranie danych
Po zatwierdzeniu wyboru wtyczka rozpocznie pobieranie danych z API GUS. Proces jest wyświetlany w formie paska postępu, a w razie potrzeby wtyczka obsługuje błędy sieciowe i ponawia nieudane próby połączenia.
<img width="600" alt="Zrzut ekranu 2024-11-25 o 12 59 20" src="https://github.com/user-attachments/assets/dde12eae-c675-4e72-b0af-1a6e057b3749">

#### 5. Wybierz lata, dla których chcesz analizować dane
Kolejnym krokiem jest wybór zakresu lat, dla których dane mają zostać pobrane. Domyślnie zaznaczony jest rok poprzedzający bieżący.
<img width="401" alt="Zrzut ekranu 2024-11-25 o 13 00 24" src="https://github.com/user-attachments/assets/b10b2ecb-c735-4353-9ff7-2bb3a1b52871">

#### 6. Dodanie danych do mapy
Po zakończeniu procesu pobierania dane zostaną dodane jako warstwa wektorowa do projektu QGIS. Każda jednostka terytorialna będzie przedstawiona jako geometria, a wybrane wskaźniki zostaną zapisane jako kolumny w tabeli atrybutów.
<img width="1402" alt="Zrzut ekranu 2024-11-25 o 13 01 45" src="https://github.com/user-attachments/assets/cc24a01c-071c-4a9b-8e42-25e60932bbb9">



## EN
    Downloading objects from the Polish Public Database
### Description

This plugin enables the retrieval of data from GUS (Central Statistical Office of Poland) for analysis and visualization within the QGIS environment. Users can select specific territorial areas, statistical indicators, and time ranges for which data should be fetched. As a result, a vector layer is created, where each territorial unit is represented as geometry, and the selected indicators are assigned as attributes in columns. This allows statistical data to be easily processed, analyzed, and presented in a spatial context. The plugin supports integration with the GUS API and provides dynamic layer creation based on user-selected criteria. It is a useful tool for analysts and research institutions that require seamless access to statistical data within a geographic context.


#### Before the First Use of the Plugin
To function correctly, the plugin requires a local spatial database. This database is a simplified and faster copy of data available in BDOT (Polish Topographic Object Database). After installation, the plugin automatically checks whether the database is available locally. If the database is missing, it will be downloaded from the internet. This process requires an active internet connection and may take a few minutes depending on the network speed.
Note: The plugin cannot function without an internet connection if the local database is not available.
### Example Usage of the Plugin

#### 1. Select Territorial Units for Data Retrieval
The first step is to choose the desired territorial units. The plugin allows selection at different levels of administrative hierarchy, such as voivodeships (provinces), counties, and communes. It is recommended to select higher-level units (e.g., counties instead of individual communes) to limit the number of API requests and speed up the data retrieval process.
<img width="804" alt="Screenshot 2024-11-25 at 12 50 50" src="https://github.com/user-attachments/assets/56d20c40-9ed8-404e-b864-d0d2fe33bfcd">

#### 2. Select the Data to Retrieve
Next, choose the statistical indicators to be fetched. Indicators are grouped thematically, making them easier to find. You can select multiple indicators, which will be saved as separate columns in the resulting layer.
<img width="1000" alt="Screenshot 2024-11-25 at 12 54 26" src="https://github.com/user-attachments/assets/a85026c4-fd5b-4b6a-b179-ee9f0e94218f">

#### 3. Specify Column Names
For each selected indicator, you need to specify a column name where the data will be stored. The plugin automatically suggests names, but it is advisable to keep them short (up to 20 characters) for better readability.
<img width="1003" alt="Screenshot 2024-11-25 at 12 56 35" src="https://github.com/user-attachments/assets/9e0436a7-03d8-4494-bdf7-86902cba75ab">
This ensures that column names are clear and easy to use in data analysis.
<img width="1005" alt="Screenshot 2024-11-25 at 12 57 21" src="https://github.com/user-attachments/assets/5f1fd63b-59cc-43fa-855c-0f0f5b8836f0">

#### 4. Data Retrieval
Once the selection is confirmed, the plugin begins retrieving data from the GUS API. The process is displayed with a progress bar, and the plugin handles network errors gracefully, retrying failed requests when necessary.
<img width="600" alt="Screenshot 2024-11-25 at 12 59 20" src="https://github.com/user-attachments/assets/dde12eae-c675-4e72-b0af-1a6e057b3749">

#### 5. Select Years for Data Analysis
In the next step, choose the range of years for which data should be retrieved. By default, the year preceding the current one is selected.
<img width="401" alt="Screenshot 2024-11-25 at 13 00 24" src="https://github.com/user-attachments/assets/b10b2ecb-c735-4353-9ff7-2bb3a1b52871">

#### 6. Add Data to the Map
After the retrieval process is complete, the data will be added as a vector layer to your QGIS project. Each territorial unit will be represented as a geometry, and the selected indicators will be stored as columns in the attribute table.
<img width="1402" alt="Screenshot 2024-11-25 at 13 01 45" src="https://github.com/user-attachments/assets/cc24a01c-071c-4a9b-8e42-25e60932bbb9">