# common.py:

# import commonly used libraries
import requests
import json
import pandas as pd
import dash
from dash import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import datetime

# Example of a global variable
shared_data = "Fabulous data will be available across all pages!"

global_data_dict = {}

### GET YOUR DATA BITS
# Define constants
BASE_URL = "http://environment.data.gov.uk/hydrology/id"
BASE_STATIONS_URL = "http://environment.data.gov.uk/hydrology/id/stations"
WISKI_IDS = ['2175', '2077', '2134', '2180', '2001', '2642', '2085', '2616', '2032', '2087', '2606', '2057', '2071',
             '2618', '2165', '2102', '2153', '2132', '2008', '2086', '2002', '2128', '055829', '055811', '055807',
             '055817', '055843', '4143', '4078', '4018', '4703', '4052', '4040', '4083', '4006', '4012', '4019',
             '4069', '4039', '4066', '4081', '4878', '4003', '2090', '2019', '2091', '2093', '2050', '2049', '2048',
             '452039', '2092', '2621', '2104']
#WISKI_IDS = ['2175', '2077', '2134']
MIN_DATE = "2023-10-01"
MAX_DATE = "2024-02-29"
DATE_FILTERS = {
    'Babet': ('2023-10-18', '2023-10-31', 'red'),
    'Ciaran': ('2023-11-01', '2023-11-08', 'blue'),
    'Elin & Fergus': ('2023-11-09', '2023-12-17', 'black'),
    'Gerrit': ('2023-12-26', '2024-01-02', 'pink'),
    'Henk': ('2024-01-02', '2024-01-11', 'green'),
    'Isha & Jocelyn': ('2024-01-21', '2024-01-23', 'orange'),
    'Early February': ('2024-02-09', '2024-02-12', 'cornflowerblue'),
    'Late February': ('2024-02-23', '2024-02-24', 'gray')
}

sites_of_interest_merge = pd.read_csv('sites_of_interest_merge.csv')

### MAKE YOUR FUNCTIONS
def fetch_station_data(wiski_id, start_date, end_date):
    try:
        url_endpoint = f"{BASE_STATIONS_URL}?wiskiID={wiski_id}"
        response = requests.get(url_endpoint)
        response.raise_for_status()
        data = json.loads(response.content)
        if 'items' in data and data['items']:
            label_field = data['items'][0].get('label')
            name = str(label_field[1] if isinstance(label_field, list) else label_field)
            river_name = data['items'][0].get('riverName')
            latitude = data['items'][0].get('lat')
            longitude = data['items'][0].get('long')
            measure_url = f"{BASE_URL}/measures?station.wiskiID={wiski_id}&observedProperty=waterLevel&periodName=15min"
            response = requests.get(measure_url)
            response.raise_for_status()
            measure = json.loads(response.content)
            if 'items' in measure and measure['items']:
                measure_id = measure['items'][0]['@id']
                readings_url = f"{measure_id}/readings?mineq-date={start_date}&maxeq-date={end_date}"
                response = requests.get(readings_url)
                response.raise_for_status()
                readings = json.loads(response.content)
                readings_items = readings.get('items', [])
                if readings_items:
                    df = pd.DataFrame.from_dict(readings_items)
                    df['dateTime'] = pd.to_datetime(df['dateTime'])
                    return {
                        'name': name,
                        'date_values': df[['dateTime', 'value']],
                        'river_name': river_name,
                        'lat': latitude,
                        'long': longitude
                    }
                else:
                    print(f"No readings found for {name} ({wiski_id})")
            else:
                print(f"No measure items found for WISKI ID {wiski_id}")
        else:
            print(f"No station items found for WISKI ID {wiski_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for WISKI ID {wiski_id}: {e}")
    return None

# Fetch data for all stations
def fetch_all_station_data(start_date, end_date):
    data_dict = {}
    for wiski_id in WISKI_IDS:
        station_data = fetch_station_data(wiski_id, start_date, end_date)
        if station_data:
            data_dict[station_data['name']] = station_data
    return data_dict

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
        flat_df[f'{storm}_DateTime'] = pivot_df[f'DateTime_{storm}']
        flat_df[f'{storm}_Value'] = pivot_df[f'Value_{storm}']

    # Reset index if necessary
    flat_df.reset_index(inplace=True)

    # Merge with 'sites_of_interest_merge' DataFrame
    peak_table_all = pd.merge(flat_df, sites_of_interest_merge[['Region', 'River','Gauge','Order']], left_on='Station', right_on='Gauge')
    columns_to_move = ['Order','Region', 'River']
    new_order = columns_to_move + [col for col in peak_table_all.columns if col not in columns_to_move]
    peak_table_all = peak_table_all[new_order]
    peak_table_all.drop(columns=['Gauge'], inplace=True)

    peak_table_all = peak_table_all.sort_values(by=['Order'], ascending=[True])
    peak_table_all.set_index('Order', inplace=True)

    peak_table_all = peak_table_all.drop_duplicates(subset=['Station'])
    
    return peak_table_all

### CALL YOUR FUNCTIONS
# Fetch data for all stations
# data_dict = fetch_all_station_data()
# shared_data = data_dict

# # Find and store maximum values for all stations
# max_values = find_and_store_max_values(data_dict)

# # Create peak table DataFrame
# peak_table_all = process_peak_table_all(max_values, sites_of_interest_merge)




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

