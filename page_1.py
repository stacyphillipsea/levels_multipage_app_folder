# page1.py:
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from navbar import create_navbar
from dash.dependencies import Input, Output, State
from common import fetch_all_station_data, global_data_dict, MIN_DATE, MAX_DATE
from app import app  # Assuming your Dash app object is named app
import time

nav = create_navbar()

header = html.H3('Welcome to page 1!')

# Define layout for page 1
def create_page_1(shared_data):
    # Use shared data in the layout or callbacks as needed
    # For example:
    layout = html.Div([
        nav,
        header,
        html.H1("Pick the dates you would like data for!"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=MIN_DATE,
            end_date=MAX_DATE,
            display_format='YYYY-MM-DD',
            className="mb-3 mt-3"
        ),
        dbc.Button("Fetch Data", id='fetch-data-button', color="primary", className="mr-2"),
        dbc.Spinner(html.Div(id='output-spinner')),
        html.Div(id='output-data')
    ])
    return layout

# Modify fetch_data_content to accept data_dict as an argument
def fetch_data_content(start_date, end_date, data_dict):

    # Simulate data fetching delay
    time.sleep(3)

    # Call fetch_all_station_data function from common.py to fetch data
    data_dict = fetch_all_station_data(start_date, end_date)

    print("Global data dict updated successfully:", data_dict)  # Print the updated global data dict for debugging

    # Format the fetched data for display
    formatted_data = html.Pre(str(data_dict))

    # Return the fetched data
    return html.Div([
        html.H3('Data fetched successfully!'),
        formatted_data
    ])

# Update the callback to pass data_dict to fetch_data_content
@app.callback(
    Output('output-data', 'children'),
    [Input('fetch-data-button', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')]
)

def fetch_data(n_clicks, start_date, end_date):
    if n_clicks is not None and n_clicks > 0:
        print("Fetch button clicked!")
        
        # Show the spinner while data is being fetched
        return dbc.Spinner(
            html.Div(fetch_data_content(start_date, end_date, global_data_dict)),
            color="primary",
            size="lg",
            fullscreen=True,
        )
    else:
        print("Fetch button not clicked!")
        return html.Div()
