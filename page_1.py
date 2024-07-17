import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from navbar import create_navbar
from dash.dependencies import Input, Output
from common import (
    data_dict,
    dash_table,
    filtered_df,
    peak_table_all,
    max_values,
    DATE_FILTERS,
    station_top_ten,
    initial_map_html,
    plot_historic_levels,
    threshold_dict,
    create_map,
    complete_stations,
    percent_complete
)

from app import app  # Assuming your Dash app object is named app

nav = create_navbar(app)

header = html.H3('Welcome to page 1!')

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


# Define layout for page 1
def create_page_1(shared_data):
    layout = html.Div([
        nav,
        header,
            # Data info modal popup
        html.Div([
            html.Div(id="data-modal"),
            html.Button("A note on data completeness", id="open_modal"),
            # Define the modal
            modal_content,
        ]),
        # Dropdowns and map
        dbc.Row([
            dbc.Col([
                html.P("Choose a site for peak analysis:", id="station-choice", 
                        style={'font-size': '16px', "fontStyle": 'bold'}), 
                html.P("First, pick the river name, and then the stations available for that river will be shown.", 
                        style={'font-size': '14px'}),
                html.P("You can start typing into the bar to search, or pick from the dropdown.", 
                        style={'font-size': '14px'}),
                html.P("The map to the right can help you identify what river a site is on; each river is coloured differently.", 
                        style={'font-size': '14px'}),
                dcc.Dropdown(
                    id="river-dropdown",
                    clearable=False,
                    value="River Severn",  # Default value for the river dropdown
                    options=[
                        {'label': river_name, 'value': river_name} 
                        for river_name in sorted(set([v['river_name'] for v in data_dict.values() if v.get('river_name') is not None]))
                    ],
                    style={'font-size': '16px'}
                ),
                dcc.Dropdown(
                    id="station-dropdown",
                    clearable=False,
                    value="Welsh Bridge",  # Default value for the station dropdown
                    options=[],  # Will be dynamically populated based on the selected river name
                    style={'font-size': '16px'}
                ),
            ], width=8),
            dbc.Col(
                html.Iframe(id='map-container', srcDoc=initial_map_html, width='100%', height='200'),
                width=4
            ),
        ]),
        html.Hr(),  # line break
        # Peak chart and peak table
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H2("River levels for this station over Winter 23-24", id="peak-info", 
                            style={"textAlign": "center", 'font-size': '14px'}),
                    html.Div(id="output-graph", className="card"),
                ]),
                width=8
            ),  
            dbc.Col(
                html.Div([
                    html.H2("Peaks identified for this station over Winter 23-24", 
                            style={"textAlign": "center", 'font-size': '14px'}),
                    html.Div(id="peak-table", className="card"),
                    html.Br(),
                    html.H4(["To see storm parameters used, click ",
                              html.A("here", href="#storm-info"), "."], 
                             style={"textAlign": "center", "font-size": "14px"})
                ]),
                width=4
            ),  
        ]),
        html.Hr(),  # line break
        # Peaks versus historic table and chart
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H2("Top 10 historic levels for this station", id="historic-info", 
                            style={"textAlign": "center", 'font-size': '14px'}),
                    dash_table.DataTable(
                        id='station-top-ten-table',
                        columns=[{"name": i, "id": i} for i in filtered_df.columns],
                        data=[],
                        style_table={'minWidth': '90%', 'overflowY': 'auto', 
                                     'border': '1px solid black', 'font-size': '12px'},  # Adjust font size
                        style_cell={'textAlign': 'left', 'padding': '5px', 
                                    'border': '1px solid black'},  # Add padding
                        page_action='none'
                    ),
                ]),
                width=7
            ),
            dbc.Col(
                html.Div([
                    html.H2("Winter 23-24 peaks versus historic levels", 
                            style={"textAlign": "center", 'font-size': '14px'}),
                    html.H2("Only top-3 historic records are shown here to help comparison", 
                            style={"textAlign": "center", 'font-size': '10px'}),
                    html.Div(id="historic-graph", className="card"),
                ]),
            )
        ]),
    ])
    return layout

### DEFINE CALLBACKS
@app.callback(
    Output("download-component", "data"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(peak_table_all.to_csv, "Winter2324_PeakLevels.csv")

def update_station_options(selected_river):
    if selected_river:
        stations = [key for key, value in data_dict.items() if value['river_name'] == selected_river]
        options = [{'label': station, 'value': station} for station in stations]
        return options
    else:
        return []

# Callback associated with the dropdowns
@app.callback(
    [Output('output-graph', 'children'),
     Output('peak-table', 'children'),
     Output('historic-graph', 'children'),
     Output('station-top-ten-table', 'data'),
     Output('station-dropdown', 'options')],
    [Input('river-dropdown', 'value'),
     Input('station-dropdown', 'value')]
)
### UPDATE FUNCTIONS BASED ON THE CALLBACK
def update_graph_peak_table_top_ten(selected_river, selected_station):
    # Update the options of the station dropdown based on the selected river
    station_options = update_station_options(selected_river)

    if selected_station:
        station_data = data_dict[selected_station]
        df = station_data.get('date_values')
        river_name = station_data.get('river_name', 'Unknown River')
        if df is not None:
            figure = {
                'data': [{'x': df['dateTime'], 
                           'y': df['value'], 
                           'type': 'line', 
                           'name': 'River Level'}],
                'layout': {
                    'title': f'River Levels for {selected_station} ({river_name})',
                    'xaxis': {'title': 'Date Time'},
                    'yaxis': {
                        'title': {
                            'text': 'Level<br><span style="font-size: 80%;">(metres above gaugeboard datum)</span>',
                            'standoff': 0
                        }
                    }
                }
            }
            if selected_station in max_values:
                # Create table rows for peak values
                table_rows = []
                for filter_name, max_value_info in max_values[selected_station].items():
                    max_datetime = max_value_info['dateTime']
                    max_value = max_value_info['value']
                    figure['data'].append({
                        'x': [max_datetime], 
                        'y': [max_value], 
                        'mode': 'markers',
                        'marker': {'color': DATE_FILTERS[filter_name][2], 'size': 10},
                        'name': f'Storm {filter_name} peak'
                    })
                    max_datetime = max_value_info['dateTime'].strftime('%d-%b-%Y %H:%M')  # Format datetime here
                    color = DATE_FILTERS[filter_name][2]  # get color info

                    # Create a colored marker cell
                    colored_marker_cell = html.Td(style={'background-color': color, 'width': '10px'}, children=[])

                    table_rows.append(html.Tr([
                        colored_marker_cell,  # Colored marker cell
                        html.Td(filter_name, style={'font-size': '16px'}),
                        html.Td(str(max_datetime), style={'font-size': '16px'}),
                        html.Td(str(max_value), style={'font-size': '16px'})
                    ]))

                # Create the table
                peak_table = html.Table([
                    html.Thead(html.Tr([
                        html.Th('', style={'font-size': '16px', 'width': '18px'}),  # Empty header for marker cell
                        html.Th('Storm Name', style={'font-size': '16px'}),
                        html.Th('Date Time', style={'font-size': '16px'}),
                        html.Th('Peak Value', style={'font-size': '16px'})
                    ])),
                    html.Tbody(table_rows)
                ])

                # Get top 10 table data
                top_10_df = station_top_ten(selected_station)

                # Make historic plot
                fig = plot_historic_levels(filtered_df, selected_station, threshold_dict)
                # Include the generated plot in the layout
                historic_graph = dcc.Graph(figure=fig)

                # Return graph, peak table, and top 10 table data
                return dcc.Graph(id='river-level-graph', figure=figure), peak_table, historic_graph, top_10_df.to_dict('records'), station_options

    return "No data available for selected station.", "", [], [], station_options

# Callback to update map based on selected station
@app.callback(
    Output('map-container', 'srcDoc'),
    [Input('station-dropdown', 'value')]
)
def update_map(selected_station):
    return create_map(data_dict, selected_station)

# Define callback to toggle the modal
@app.callback(
    dash.dependencies.Output("modal", "is_open"),
    [dash.dependencies.Input("open_modal", "n_clicks"), dash.dependencies.Input("close_modal", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
