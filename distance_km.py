import requests
import pandas as pd


# Set pandas display options to show all columns and rows without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Your DataFrame creation code

# Define your list of locations (origins and destinations)
locations = [
    "Spanakou 6, Aspropirgos 19300, Greece",
    "Iliou 33, Athina 13122, Greece",
    "Spirou Theologou 1, Athina 13122, Greece",
    "Agiou Nikolaou 61, Athina 13123, Greece",
    "Kosti Palama 68, Athina 13451, Greece",
    "Anagenniseos 16, Athina 14233, Greece",
    "Iroon Politechniou 144, Acharnes 13674, Greece",
    "Timiou Stavrou 14, Kifisia 14564, Greece",
    "Protesilaou 92, Athina 13122, Greece",
    "Agiou Nikolaou 7, Kamatero 13451, Greece",
    "Sofokli Venizelou 110, Agii Anargiri 13561, Greece",
    "28is Oktovriou 46, Nea Ionia 14231, Greece",
    "Kritis 11, Kifisia 14563, Greece",
    "Tsimiski 54, Ilion 13121, Greece",
    "Leof. Marathonos 28, Anixi 14569, Greece",
    "Redestou 99, Nea Chalkidona 14343, Greece",
    "Tatoiou 1, Metamorfosi 14451, Greece",
    "Eleftheriou Venizelou 85, Nea Erythrea 14671, Greece",
    "Nikis 2, Marousi 14561, Greece",
    "Ioannou Soutsou 48, Athina 11474, Greece",
    "Elenas Venizelou 2, Athina 11521, Greece",
    "Iraklitou 14, Athina 10673, Greece",
    "Monis Petraki 12, Athina 11521, Greece",
    "Leof. Aleksandras 119, Athina 11475, Greece",
    "Erythrou Stavrou 2, Athina 11526, Greece",
    "Leof. Kifisias 5, Athina 11523, Greece",
    "Leof. Mesogion 264, Cholargos 15562, Greece",
    "Sevastoupoleos 150, Athina 11526, Greece",
    "Leof. Mesogion 107, Athina 11526, Greece",
    "Michalakopoulou 148, Athina 11527, Greece",
    "Fidippidou 35, Ampelokipoi 11527, Greece",
    "Children's Hospital Agia Sophia, Athina 11527, Greece",
    "Plateia Pedon 3, Athina 11527, Greece",
    "Grigoriou Kousidi 83, Zografou 15772, Greece",
    "Grigoriou Afksentiou 86, Athina 15771, Greece",
    "Papadiamantopoulou 15, Athina 11528, Greece",
    "Filolaou 113, Athina 11633, Greece",
    "Agion Apostolon 2, Metamorfosi 16232, Greece",
    "Kolokotroni 12, Vironas 16232, Greece",
    "Leof. Chrisostomou Smirnis 89, Vironas 16232, Greece",
    "Neas Efesou 21, Vironas 16231, Greece",
    "Leonidou 8, Athina 10437, Greece",
    "Menandrou 58, Athina 10432, Greece",
    "Menandrou 54, Athina 10431, Greece",
    "Ermou 82, Athina 10554, Greece",
    "Filellinon 2, Athina 10557, Greece",
    "Emmanouil Mpenaki 8, Athina 10564, Greece",
    "Akadimias 76, Athina 10678, Greece",
    "Themistokleous 3, Athina 10677, Greece",
    "Mavromichali 39, Athina 10680, Greece",
    "Patriarchou Ioakeim 50, Athina 10676, Greece",
    "Sisini 3, Athina 11528, Greece",
    "Leoforou Aleksandras 175, Athina 11522, Greece",
    "Dimitriou Soutsou 21, Athina 11521, Greece",
    "Leof. Galatsiou 50, Athina 11141, Greece",
    "Therianou 4, Athina 11473, Greece",
    "I. Foka 85, Athina 11142, Greece",
    "Patision 294, Athina 11255, Greece",
    "Iakovaton 43, Athina 11144, Greece",
    "Patision 366, Athina 11141, Greece",
    "Agorakritou 24, Athina 10446, Greece",
    "Emonos 65, Athina 10442, Greece",
    "Petras 6, Athina 10444, Greece",
    "25is Martiou 89, Petroupoli 13231, Greece",
    "Kiklaminon 7, Peristeri 12137, Greece",
    "25is Martiou 112, Petroupoli 13231, Greece",
    "25is Martiou 124, Petroupoli 13231, Greece",
    "25is Martiou 174, Petroupoli 13231, Greece",
    "Alkimou 74, Peristeri 12135, Greece",
    "Vasileos Aleksandrou 105, Peristeri 12131, Greece",
    "Prokopiou 11, Peristeri 12131, Greece",
    "Kifisou 132, Peristeri 12131, Greece",
    "Ethnarchou Makariou 60, Peristeri 12132, Greece",
    "Thrasimachou 14, Athina 10442, Greece",
    "Amphiarau 25, Athina 104 42, Greece",
    "Konstantinoupoleos 3, Peristeri 12132, Greece",
    "Lefktron 6, Peristeri 12133, Greece",
    "Stilianou Gonata 15, Peristeri 12133, Greece",
    "Lefkosias 24, Peristeri 12133, Greece"
]

# API key for Distance Matrix.AI API
API_KEY = 'cloQkazz1rmXNvxU16BNk7UdAzj7QFq5Itg8vAEJleAuUBq1aSjbxjadLqOtJxKs'

# Initialize an empty DataFrame for the distance matrix
distance_matrix_df = pd.DataFrame(index=locations, columns=locations)


# Iterate through all pairs of locations
for origin in locations:
    totalLocationsChecked = 0
    while len(locations) > totalLocationsChecked:
        # Make a request to the Distance Matrix.AI API to get the duration
        testd = "|".join(locations[totalLocationsChecked:totalLocationsChecked+15])
        url = f"https://api.distancematrix.ai/maps/api/distancematrix/json?origins={origin}&destinations={testd}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        print(data)

        if 'rows' in data and len(data['rows']) > 0:
            row = data['rows'][0]
            for element in row['elements']:
                if 'distance' in element:
                    distance = element['distance']['value'] / 1000  # Convert duration from seconds to minutes

                    # Populate the matrix DataFrame with the extracted durations
                    distance_matrix_df.at[origin, element["destination"]] = round(distance,1)

        totalLocationsChecked += 15

print("Distance Matrix DataFrame:")
print(distance_matrix_df)

distance_matrix_df.to_csv('distance_km.csv', index=True)

