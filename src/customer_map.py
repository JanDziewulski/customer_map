#Install Pckg
import pandas as pd
import folium
import googlemaps
from password import api_key

gmaps_client = googlemaps.Client(api_key)

def read_customers():
    """Odczytuje klientów z pliku *.csv następnie korzystając z API Google Maps odszukuje firmy po nazwie
    DataFrame jest czyszczony z firm, dla któwych nie znaleziono lokalizacji w Google Maps.
    Dla reszty pobierane są współrzędne geograficzne lng, lat
    ------------
    Aktualna skuteczność poprawnego rozpoznania 53/100

    """


    df = pd.read_csv('../csv/customers.csv') #wczytywanie danych z pliku csv
    cmp = list(df['Firma']) #zamiana kolumny Firma na listę w celu łatwiejszego iterowania
    geo_list = []
    for i in range(len(cmp)):
        geocode_result = gmaps_client.geocode(cmp[i]+'Polska'+'CNC'+'Obróbka skrawaniem'+'Frezowanie')
        geo_list.append(geocode_result)
        if geocode_result == []:
            df = df[df['Firma'] != cmp[i]] #usuwanie Nazwy firmy której nie znaleziono w geocode_results

    geo_list_recognized = [x for x in geo_list if x != []] #czyszczenie wyników zwracających pustą listę

    lng_list = [] #tworzenie pustych list
    lat_list = []

    for j in range(len(geo_list_recognized)):
        lng_list.append(geo_list_recognized[j][0]['geometry']['location']['lng'])
        lat_list.append(geo_list_recognized[j][0]['geometry']['location']['lat'])


    df_final = df.assign(lng=lng_list,lat =lat_list) #dodawanie kolumn do DataFrame

    return df_final #zwrócenie DataFrame

def map_maker():
    """
    Na postawie współrzędnych geograficznych dla poszczególnych firm tworzona jest mapa z lokalizacją
    :retu
    html object
    """
    df = read_customers()
    lat = list(df['lat'])
    lng = list(df['lng'])
    cmp = list(df['Firma'].str.upper())

    map = folium.Map(location=[52.22977,21.01178],
                     tiles='cartodbpositron',
                     zoom_start=12)

    fg = folium.FeatureGroup(name='CAMWorks')



    for lt, ln, c in zip(lat,lng,cmp):
        fg.add_child(folium.CircleMarker(location=[lt,ln],
                                         radius=10,
                                         popup=str(c),
                                         fill_color='red',
                                         color='grey',
                                         fill_opacity=0.7))

    map.add_child(fg)
    map.save('CAMWORKS.html')

def center_map():
    sw = df[['lat', 'lng']].min().values.tolist()# funkcja służaca do centrowania pinesek na mapie
    ne = df[['lat', 'lng']].max().values.tolist()
    map.fit_bounds([sw, ne])

if __name__ == '__main__':
    map_maker()
