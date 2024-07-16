# common.py:

import pandas as pd
import numpy as np      # For numerical operations
from datetime import datetime
import requests         # For API call
import json             # For API call
import dash             # For app
from dash import dcc, html, dash_table      # For app layout
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go           # For Plotly charts
import folium               # For map
from io import StringIO     # To loadd JSON to dataframe


### GET YOUR DATA BITS
# Define key constants
BASE_URL = "http://environment.data.gov.uk/hydrology/id"
BASE_STATIONS_URL = "http://environment.data.gov.uk/hydrology/id/stations"
MIN_DATE_STR = "2023-10-01"
MAX_DATE_STR = "2024-02-29"
MIN_DATE = datetime.strptime(MIN_DATE_STR, '%Y-%m-%d')
MAX_DATE = datetime.strptime(MAX_DATE_STR, '%Y-%m-%d')
DATE_FILTERS = {
    'Babet': ('2023-10-18', '2023-10-31', 'red'),
    'Ciaran': ('2023-11-01', '2023-11-08', 'blue'),
    'Elin & Fergus': ('2023-12-09', '2023-12-17', 'black'),
    'Gerrit': ('2023-12-26', '2024-01-02', 'pink'),
    'Henk': ('2024-01-02', '2024-01-11', 'green'),
    'Isha & Jocelyn': ('2024-01-21', '2024-01-27', 'orange'),
    'Early February': ('2024-02-09', '2024-02-12', 'cornflowerblue'),
    'Late February': ('2024-02-22', '2024-02-25', 'gray')
}

## Load data
# Metadata spreadsheet
sites_of_interest_merge = pd.read_csv('sites_of_interest_merge.csv')

# Historic records
gaugeboard_data = pd.read_csv('gaugeboard_data.csv')

# Adding to use all WMD Gauges from Harry's list
wmd_gauges = pd.read_csv('All_WMD_gauges_FETA.csv')
WISKI_IDS = wmd_gauges['Site number'].dropna().tolist()
WISKI_IDS = [f"{name}" for name in WISKI_IDS]

# Function to modify IDs for the Wye
def modify_ids(ids):
    modified_ids = []
    for id in ids:
        if id.startswith('55'):
            modified_ids.append('0' + id)
        else:
            modified_ids.append(id)
    return modified_ids

# Apply the function
modified_wiski_ids = modify_ids(WISKI_IDS)
WISKI_IDS = modified_wiski_ids

# Isolate threshold/max values from metadata spreadsheet
threshold_values = sites_of_interest_merge[sites_of_interest_merge['Threshold'].notnull()]
threshold_values.loc[:, 'Threshold'] = threshold_values['Threshold'].astype(float) # Ensure original is modified, removing SettingWithCopyWarning
threshold_dict = threshold_values.set_index('Gauge')['Threshold'].to_dict()

### MAKE YOUR FUNCTIONS
# Fetch data for a single station
def fetch_station_data(wiski_id):
    try:
        url_endpoint = f"{BASE_STATIONS_URL}?wiskiID={wiski_id}"
        response = requests.get(url_endpoint)
        response.raise_for_status()
        data = response.json()

        if not data.get('items'):
            print(f"No station found with the WISKI ID {wiski_id}")
            return None

        station = data['items'][0]
        label_field = station.get('label')
        name = str(label_field[1] if isinstance(label_field, list) else label_field)
        wiski_id = {wiski_id}
        river_name = station.get('riverName')
        river_name = river_name[0] if isinstance(river_name, list) else river_name
        latitude = station.get('lat')
        longitude = station.get('long')

        measure_url = f"{BASE_URL}/measures?station.wiskiID={wiski_id}&observedProperty=waterLevel&periodName=15min"
        response = requests.get(measure_url)
        response.raise_for_status()
        measure = response.json()

        if not measure.get('items'):
            print(f"No level measures found for {name} (WISKI ID: {wiski_id})")
            return None

        measure_id = measure['items'][0]['@id']
        readings_url = f"{measure_id}/readings?mineq-date={MIN_DATE_STR}&maxeq-date={MAX_DATE_STR}"
        response = requests.get(readings_url)
        response.raise_for_status()
        readings = response.json()
        readings_items = readings.get('items', [])

        if not readings_items:
            print(f"No readings found for {name} (WISKI ID: {wiski_id})")
            return None

        df = pd.DataFrame.from_dict(readings_items)
        df['dateTime'] = pd.to_datetime(df['dateTime'])

        return {
            'name': name,
            'date_values': df[['dateTime', 'value']],
            'river_name': river_name,
            'lat': latitude,
            'long': longitude
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for WISKI ID {wiski_id}: {e}")
        return None

# Fetch data for all stations
def fetch_all_station_data():
    data_dict = {}
    processed_ids = {}
    unprocessed_ids = {}

    for wiski_id in WISKI_IDS:
        station_data = fetch_station_data(wiski_id)
        if station_data:
            data_dict[station_data['name']] = station_data
            processed_ids[wiski_id] = station_data['name']
        else:
            unprocessed_ids[wiski_id]

    print(unprocessed_ids)
    return data_dict, processed_ids, unprocessed_ids

# Find maximum values for each filter
def find_max_values(df, filters):
    max_values = {}
    for filter_name, date_range in filters.items():
        min_date, max_date, color = date_range
        condition = (df['dateTime'] >= min_date) & (df['dateTime'] <= max_date)
        filtered_df = df[condition].dropna()  # Drop rows with NaN values
        if not filtered_df.empty:
            max_value_row = filtered_df.loc[filtered_df['value'].idxmax(), ['dateTime', 'value']]
            max_value_row['value'] = round(max_value_row['value'], 2)  # Round the maximum value to 2 decimal places
            max_values[filter_name] = max_value_row
    return max_values

# Find and store maximum values for all stations
def find_and_store_max_values(data_dict):
    max_values = {}
    for station_name, station_data in data_dict.items():
        df = station_data.get('date_values')
        if df is not None:
            max_values[station_name] = find_max_values(df, DATE_FILTERS)
    return max_values

#Generate storm info for the peak table
def generate_storm_info():
    storm_info = []
    for storm, (start_date, end_date, _) in DATE_FILTERS.items():
        formatted_start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d %b %Y')
        formatted_end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d %b %Y')
        storm_info.append(html.Div([
            html.P(f"{storm}: {formatted_start_date} to {formatted_end_date}", style={'font-size': '14px'}),
        ]))
    return storm_info

# Create a table for all the sites
def process_peak_table_all(max_values, sites_of_interest_merge):
    # Create an empty DataFrame
    df_list = []

    # Iterate through the outer dictionary
    for station, inner_dict in max_values.items():
        # Iterate through the inner dictionary
        for storm, values in inner_dict.items():
            # Extract dateTime and value from the Series object
            if values is not None:
                date_time = values.get('dateTime')
                value = values.get('value')
            else:
                date_time, value = None, None

            # Create a new row as a dictionary
            row_dict = {'Station': station, 'Storm': storm, 'DateTime': date_time, 'Value': value}
            # Append the row dictionary to the list
            df_list.append(row_dict)

    # Create the DataFrame
    df = pd.DataFrame(df_list)

    # Pivot the DataFrame
    pivot_df = df.pivot_table(index='Station', columns='Storm', values=['DateTime', 'Value'], aggfunc='first')

    # Flatten the multi-level columns
    pivot_df.columns = [f'{col[0]}_{col[1]}' for col in pivot_df.columns]

    # Create a new DataFrame with the flat structure
    flat_df = pd.DataFrame()

    # Iterate through the original DataFrame columns and create flat structure
    for storm in df['Storm'].unique():
        flat_df[f'{storm}_DateTime'] = pivot_df[f'DateTime_{storm}'].dt.strftime('%d-%b-%Y %H:%M')
        flat_df[f'{storm}_Value'] = pivot_df[f'Value_{storm}']

    # Reset index if necessary
    flat_df.reset_index(inplace=True)

# Merge with 'sites_of_interest_merge' DataFrame
    peak_table_all = pd.merge(flat_df, wmd_gauges[['Region', 'River','Gauge','Order']], left_on='Station', right_on='Gauge', how='outer')

    columns_to_move = ['Order','Region', 'River']
    new_order = columns_to_move + [col for col in peak_table_all.columns if col not in columns_to_move]
    peak_table_all = peak_table_all[new_order]
    peak_table_all.drop(columns=['Gauge'], inplace=True)
    peak_table_all = peak_table_all.sort_values(by=['Order'], ascending=[True])
    peak_table_all.set_index('Order', inplace=True)
    peak_table_all = peak_table_all.drop_duplicates(subset=['Station'])
    
    return df, peak_table_all

# Do the comparison to the gaugeboard data
def gaugeboard_comparison(gaugeboard_data, df):
    # Format gaugeboard data datetimes
    gaugeboard_data['Date'] = pd.to_datetime(gaugeboard_data['Date'], format='%d/%m/%Y').dt.date

    # Rename 'Gauge' column to 'Station' in gaugeboard
    gaugeboard_data.rename(columns={'Gauge': 'Station'}, inplace=True)

    # Add a new column 'Storm' filled with nulls in gaugeboard
    gaugeboard_data['Storm'] = None

    # Change 'datetime' column to 'date' in df
    df['DateTime'] = df['DateTime'].dt.date
    df.rename(columns={'Value': 'Level'}, inplace=True)
    df.rename(columns={'DateTime': 'Date'}, inplace=True)

    comparison_concat = pd.concat([gaugeboard_data, df], ignore_index=True)

    comparison_concat['Station'] = comparison_concat['Station'].replace({
        'Bewdley us': 'Bewdley',
        'SAXONS LODE US': 'Saxons Lode',
        'Buildwas Us': 'Buildwas'
    })

    # Group the DataFrame by 'station' and sort each group by 'level' from highest to lowest
    sorted_df = comparison_concat.groupby('Station', as_index=False).apply(lambda x: x.sort_values(by='Level', ascending=False))

    # Add a new column 'Ranking' for each group indicating the rank of each level
    sorted_df['Ranking'] = sorted_df.groupby('Station').cumcount() + 1

    # Add a new column for difference from peak
    sorted_df['Difference_from_peak'] = sorted_df.groupby('Station')['Level'].transform(lambda x: round(x.max() - x, 2))

    # Convert 'Date' column to datetime format after sorting
    sorted_df['Date'] = pd.to_datetime(sorted_df['Date'])

    # Add a new column for difference from peak
    sorted_df['Years_since_peak'] = sorted_df.groupby('Station').apply(
        lambda group: round(abs((group['Date'] - group.loc[group['Level'].idxmax(), 'Date']).dt.days / 365.25))
        ).reset_index(level=0, drop=True)
    
    # Reset the index to flatten the DataFrame
    sorted_df.reset_index(drop=True, inplace=True)

    # Display the sorted DataFrame
    sorted_df.head(20)

    # Count the number of rows for each unique value in 'Station' column
    station_counts = sorted_df['Station'].value_counts()

    # Filter out stations with 8 or fewer records
    stations_to_keep = station_counts[station_counts > 8].index

    # Filter the DataFrame to keep only the stations with more than 8 records
    filtered_df = sorted_df[sorted_df['Station'].isin(stations_to_keep)]

    # Display the filtered DataFrame
    filtered_df['Station'].unique()

    ranked_df = filtered_df[filtered_df['Storm'].notna()]
    ranked_df.head(20)

    top_ten = ranked_df[ranked_df['Ranking'] <= 10]
    top_ten = top_ten.sort_values(by='Ranking')
    top_ten['Date'] = pd.to_datetime(top_ten['Date'], format='%d/%m/%Y')  
    top_ten['Date'] = top_ten['Date'].dt.strftime('%d-%b-%Y')
    
    return top_ten, filtered_df

# Make a top 10 list for the station selected
def station_top_ten(selected_station):
    if selected_station:
        # Filter for the selected station
        station_df = filtered_df[filtered_df["Station"] == selected_station]
        # Get the top 10 values for that station
        top_ten_df = station_df.nlargest(n=10, columns= 'Level')
        top_ten_df['Date'] = pd.to_datetime(top_ten_df['Date'], format='%d/%m/%Y')  
        top_ten_df['Date'] = top_ten_df['Date'].dt.strftime('%d-%b-%Y')
        return top_ten_df
    else:
        return pd.DataFrame()

# Make the historic level plots
def plot_historic_levels(filtered_df, selected_station, threshold_dict):
    # Check if 'Station' column is present in filtered_df
    if 'Station' not in filtered_df.columns:
        # Return an empty figure if 'Station' column is not present
        return go.Figure()
    
    # Check if the selected station is valid
    if selected_station and selected_station in filtered_df['Station'].unique():
        # Filter the DataFrame for the specified station name
        station_df = filtered_df[filtered_df["Station"] == selected_station]
        
        # Filter the DataFrame for top 3 values
        top_3_values = station_df.nlargest(n=3, columns='Level')
        
        # Filter the DataFrame for rows where 'Storm' is not None
        storm_not_none = station_df[station_df["Storm"].notnull()]
        
        # Concatenate the two DataFrames
        result_df = pd.concat([top_3_values, storm_not_none])

        # Determine the maximum level in the data
        max_level = result_df['Level'].max()
        
        # Round up to the nearest whole number
        max_level = np.ceil(max_level)
        
        # Create a new figure
        fig = go.Figure()
        
        # Iterate over each row in the filtered DataFrame
        for index, row in result_df.iterrows():
            # Assign colors based on Ranking
            if row['Ranking'] == 1:
                color = 'red'
            elif row['Ranking'] == 2:
                color = 'orange'
            elif row['Ranking'] == 3:
                color = 'yellow'
            else:
                color = 'blue'  # Default color
            
            # Format the date string
            formatted_date = row['Date'].strftime('%d-%b-%Y')
            
            # Add a trace for each row
            fig.add_trace(go.Scatter(x=[1, 2], y=[row['Level'], row['Level']], mode='lines+markers', line=dict(color=color), 
                                     name=f"{formatted_date} {row['Storm'] if pd.notnull(row['Storm']) else ''}",
                                     text=[f"Date: {formatted_date}<br>Level: {row['Level']}<br>Storm: {row['Storm'] if pd.notnull(row['Storm']) else 'Historic'}"] * 2,
                                     hoverinfo='text'))
        
        # Add manual trace for the line at typical max range
        if selected_station in threshold_dict:
            typical_max_range = threshold_dict[selected_station]
            fig.add_trace(go.Scatter(x=[1, 2], y=[typical_max_range, typical_max_range], mode='lines+markers', line=dict(color='lightskyblue'), 
                                     name='Typical max range', text=f"Typical max range: {typical_max_range}", hoverinfo='text'))
        
        # Update layout...
        fig.update_layout(
            xaxis=dict(
                showticklabels=False,
                range=[0.5, 2.5]
            ),
            yaxis=dict(
                title={'text': 'Level<br><span style="font-size: 80%;">(metres above gaugeboard datum)</span>',
                        'standoff': 0},
                rangemode='tozero',  # Ensure y-axis starts at zero
                tickmode='linear',   # Use linear ticks
                tick0=0,             # Start tick at zero
                dtick=1,             # Set tick interval to 1
                tickvals=np.arange(0, max_level + 1),  # Set tick values to whole numbers up to max_level
                range=[0, max_level],  # Set y-axis range to start from 0 and end at max_level
            ),
            title={
                'text': f"Historic levels for {selected_station}",
                'x': 0.5,  # Set x position to center
                'y': 0.95   # Adjust y position as needed
            },
            legend=dict(
                title='Recorded levels and dates',
                x=1.2,  # Increase distance from right edge
            ),

            plot_bgcolor='white'
        )
        
        fig.update_yaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey'
        )
        
        return fig
    else:
        # If the selected station is not valid or no station is selected, return an empty figure
        return go.Figure()

# Function to load station data from JSON file
def load_station_data_from_json(file_path):
    try:
        # Load data from JSON file
        with open(file_path, "r") as json_file:
            data_dict = json.load(json_file)
        
        # Convert date_values from JSON strings to DataFrames
        for station_data in data_dict.values():
            station_data['date_values'] = pd.read_json(StringIO(station_data['date_values']))

        return data_dict
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

# Define a list of colors to use as a palette
color_palette = [
    'blue', 'green', 'cadetblue', 'orange', 'purple', 'pink', 'gray', 'beige', 
    'lightblue', 'red', 'lightred', 'lightgray', 'darkblue', 'darkgreen', 'darkred', 'darkpurple'
]

# Function to create Folium map with markers for stations
def create_map(data_dict, selected_station=None):
    # Create Folium map centred on Hagley (roughly in centre of WMD)
    m = folium.Map(location=[52.4083, -2.2272], zoom_start=10)
    
    # Extract unique river names from the data_dict, filtering out None values
    river_names = [station_data.get('river_name') for station_data in data_dict.values()]

    # Remove None values
    river_names = [name for name in river_names if name is not None]

    # Create a set of unique river names
    unique_rivers = sorted(set(river_names))
    print("River Names:", unique_rivers)

    # Create river-color mapping by assigning colors from the palette
    river_color_mapping = {river: color_palette[i % len(color_palette)] for i, river in enumerate(unique_rivers)}

    # Add markers for all stations
    for station_name, station_data in data_dict.items():
        lat = station_data.get('lat', None)
        long = station_data.get('long', None)
        river_name = station_data.get('river_name', None)
        popup_content = f"<b>{station_name}</b><br>{river_name}"
        
        if lat is not None and long is not None:
            # Ensure river_name is a string
            river_name = str(river_name)
            
            # Select marker color based on river name
            marker_color = river_color_mapping.get(river_name, 'gray')  # Default to gray if river name not found
            # Add marker for station with selected color
            folium.Marker(location=[lat, long], popup=popup_content, 
                          icon=folium.Icon(icon = "info-sign", color=marker_color, icon_color="white")).add_to(m)
            m.get_root().header.add_child(folium.Element("<style>.leaflet-popup-content { width: 100px; text-align: center; }</style>"))

    # Adjust zoom level and center map if a station is selected
    if selected_station:
        station_data = data_dict[selected_station]
        lat = station_data.get('lat', None)
        long = station_data.get('long', None)

        if lat is not None and long is not None:
            # If latitude and longitude are available for the selected station, center the map on that station
            m.location = [lat, long]
            m.zoom_start = 10  # Adjust the zoom level as needed

    # Convert Folium map to HTML
    map_html = m.get_root().render()

    return map_html





def gif_with_text(gif_src, text1, text2):
    return html.Div([
        html.Div([
            dbc.CardImg(
                src=gif_src,
                bottom=True,
                style={"width": "300px"}  # Adjust the dimensions as needed
            ),
        ], style={'float': 'left', 'margin-right': '10px'}),
        
        html.Div([
            html.P(text1),
            html.P(text2),
        ], style={'overflow': 'hidden'})
    ], style={'overflow': 'hidden'})

### CALL YOUR FUNCTIONS 
# Load station data from JSON file
file_path = "nested_dict_extended.json"
data_dict = load_station_data_from_json(file_path)

if data_dict:
    print("Data loaded successfully.")
else:
    print("Error loading data.")


# Find and store maximum values for all stations
max_values = find_and_store_max_values(data_dict)

# Create peak table DataFrame
df, peak_table_all = process_peak_table_all(max_values, sites_of_interest_merge)

# Call gaugeboard_comparison function
top_ten_records, filtered_df = gaugeboard_comparison(gaugeboard_data, df)

# Identify the common station that has historic values, threholds and peak data
complete_stations = sorted(set(filtered_df['Station'].unique()) & set(threshold_dict.keys()) & set(data_dict.keys()))
percent_complete = len(complete_stations) / len(data_dict) * 100 if len(data_dict) > 0 else 0

initial_map_html = create_map(data_dict)


# Define the content of the modal
modal_content = dbc.Modal([
    dbc.ModalHeader("A note on data completeness"),
    dbc.ModalBody([
        html.H4("Not all stations have historic values, typical ranges, and peak values", style={"textAlign": "left", "color": "green", "fontWeight": "bold"}),
        html.P("Stations with complete datasets:", style={"textAlign": "left", "font-size": "16px", "color": "green"}),
        html.P(', '.join(complete_stations), style={"textAlign": "left", "font-size": "14px", "color": "green"}),
        html.P(f"That is {len(complete_stations)} stations out of {len(data_dict)} in the whole dataset ({percent_complete:.0f}%)", style={"textAlign": "left", "font-size": "12px", "color": "green", "fontStyle": "italic"}),
        #dbc.CardImg(src="https://media2.giphy.com/media/1Zp8tUAMkOZDMkqcHb/giphy.gif?cid=6c09b952rjrtfs3brpsa0z89g2oeqrzgg7d3sdoj8fon3aqd&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g", bottom=True, style={"width": "250px"}), 
    ]),
    dbc.ModalFooter(
        dbc.Button("Close", id="close_modal", className="ml-auto")
    ),
], id="modal")