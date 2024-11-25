# POPBDP
Pobieranie obiektów polskich baz danych publicznych
Downloading objects from the Polish Public Database


 - *PL:* Ta wtyczka umożliwia pobieranie danych z GUS (Głównego Urzędu Statystycznego) w celu analizy i wizualizacji w środowisku QGIS. Użytkownik może wybrać interesujące go obszary terytorialne, wskaźniki statystyczne oraz zakres lat, dla których dane mają zostać pobrane. W rezultacie tworzona jest warstwa wektorowa, w której każda jednostka terytorialna jest reprezentowana jako geometria, a wybrane wskaźniki są przypisane jako atrybuty w kolumnach. Dzięki temu dane statystyczne można łatwo przetwarzać, analizować i prezentować w kontekście przestrzennym. Wtyczka wspiera integrację z serwisem API GUS oraz zapewnia dynamiczne tworzenie warstw na podstawie wybranych kryteriów. Jest to narzędzie przydatne zarówno dla analityków, jak i instytucji badawczych, które potrzebują łatwego dostępu do danych statystycznych w kontekście geograficznym.
- *EN:* This plugin enables the retrieval of data from GUS (Central Statistical Office of Poland) for analysis and visualization within the QGIS environment. Users can select specific territorial areas, statistical indicators, and time ranges for which data should be fetched. As a result, a vector layer is created, where each territorial unit is represented as geometry, and the selected indicators are assigned as attributes in columns. This allows statistical data to be easily processed, analyzed, and presented in a spatial context. The plugin supports integration with the GUS API and provides dynamic layer creation based on user-selected criteria. It is a useful tool for analysts and research institutions that require seamless access to statistical data within a geographic context.

# przed pierwszym uruchomieniem plugin musi pobrać niezbędne dane i się zainicjalizować


# Przykładowe działanie (EN: Example worflow)


# Wybirz jednostki terytorialne dla których chcesz pobrać dane (EN: Get the desired teritorial units)

Wybierz jednostki na możliwe wyysokim ale nie za wysokm poziome. Lepiej jest wybrać pojedynczą jednostkę wyższego rzedu niż wiele mniejszych. Ograniczy to ilość zapytan do API

<img width="804" alt="Zrzut ekranu 2024-11-25 o 12 50 50" src="https://github.com/user-attachments/assets/56d20c40-9ed8-404e-b864-d0d2fe33bfcd">

# Wybiez jakie chcesz dane 

<img width="1000" alt="Zrzut ekranu 2024-11-25 o 12 54 26" src="https://github.com/user-attachments/assets/a85026c4-fd5b-4b6a-b179-ee9f0e94218f">

Po tym musisz podać nazwę kolumny do której będą wpisane dane. Zeby koluman nie była zbyt długa proponowana nazwa nie powinna być dłuższa niż 20 znaków. 

<img width="1003" alt="Zrzut ekranu 2024-11-25 o 12 56 35" src="https://github.com/user-attachments/assets/9e0436a7-03d8-4494-bdf7-86902cba75ab">

Nazwa zostanie zaproponowana ale powinna być krótka

<img width="1005" alt="Zrzut ekranu 2024-11-25 o 12 57 21" src="https://github.com/user-attachments/assets/5f1fd63b-59cc-43fa-855c-0f0f5b8836f0">

Można wybrać kilka zmiennych do wyświetlenia

<img width="1003" alt="Zrzut ekranu 2024-11-25 o 12 58 37" src="https://github.com/user-attachments/assets/72a8217d-34d9-4779-91b7-5bb38b0218fe">

# Pobieranie danych 

Dane zostaną pobrane 

<img width="600" alt="Zrzut ekranu 2024-11-25 o 12 59 20" src="https://github.com/user-attachments/assets/dde12eae-c675-4e72-b0af-1a6e057b3749">

# wybierz lata dla których dane chcesz analizować

<img width="401" alt="Zrzut ekranu 2024-11-25 o 13 00 24" src="https://github.com/user-attachments/assets/b10b2ecb-c735-4353-9ff7-2bb3a1b52871">

# Dane zostaną dodane do obszaru

<img width="1402" alt="Zrzut ekranu 2024-11-25 o 13 01 45" src="https://github.com/user-attachments/assets/cc24a01c-071c-4a9b-8e42-25e60932bbb9">
