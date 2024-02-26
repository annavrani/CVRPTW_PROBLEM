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
    "26 Anatolikis Romilias, Thessaloniki, 54454, Greece",
    "3 Kolchidos, Kalamaria, 55131, Greece",
    "2 Markou Mpotsari, Thessaloniki, 54643, Greece",
    "10 Alonnisou, Thessaloniki, 54638, Greece",
    "7 Dimokratias, Panorama, 55236, Greece",
    "30 Andrea Papandreou, Kalamaria, 55133, Greece"
]

# API key for Distance Matrix.AI API
API_KEY = '4gjG1bO9H3SylqgStT3icoUbOdYAFfSOi4AKXmNAakoE1LRIBor5j2M7O2mq2HG2'

# Initialize an empty DataFrame for the distance matrix
distance_matrix_df = pd.DataFrame(index=locations, columns=locations)

# Iterate through all pairs of locations
for origin in locations:
    for destination in locations:
        # Make a request to the Distance Matrix.AI API to get the duration
        url = f"https://api.distancematrix.ai/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Parse the response and extract the duration information
        duration = None
        if 'rows' in data and len(data['rows']) > 0:
            row = data['rows'][0]
            if 'elements' in row and len(row['elements']) > 0:
                element = row['elements'][0]
                if 'duration' in element:
                    duration = element['duration']['value'] / 60  # Convert duration from seconds to minutes

        # Populate the matrix DataFrame with the extracted durations
        distance_matrix_df.at[origin, destination] = duration

# Display the distance matrix DataFrame
print("Distance Matrix DataFrame:")
print(distance_matrix_df)

distance_matrix_df.to_csv('distance_matrix.csv', index=True)