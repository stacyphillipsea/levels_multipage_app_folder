from dash import html
import dash_bootstrap_components as dbc
from navbar import create_navbar
from common import gif_with_text, data_dict
from app import app  # Import the app instance

nav = create_navbar(app)

def create_page_home():
    layout = html.Div([
        nav,
        
        # Main title
        html.H1("Welcome to the Flood Event Telemetry Analyser (FETA)!",
                style={"textAlign": "center"}, id="top"),
        
        # Subtitle
        html.H5([
            "This app allows you to explore river level data for the Winter flood events 2023-2024",
            html.Br(),
            "for sites across the West Midlands"
        ], style={"textAlign": "center"}),
        
        # Author info
        html.H4([
            "App created by ",
            html.A("Stacy Phillips", href="mailto:stacy.phillips1@environment-agency.gov.uk?subject=I%20love%20your%20FETA%20app!")
        ], style={"textAlign": "center", "color": "#034B89"}),

        html.Hr(),  # line break
        
        # How to use information & photo
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H5("How to use the FETA", style={"text-decoration": "underline"}),
                    html.P("Data is automatically downloaded using the Environment Agency API for a number of different specified gauging stations."),
                    html.P([
                        "Choose your station of interest ",
                        html.A("(here)", href="#station-choice"),
                        " and then look at the peak levels for that station across different storm events ",
                        html.A("(here)", href="#peak-info"),
                        "."
                    ]),
                    html.P([
                        "You can then compare these peak levels to historic records ",
                        html.A("(here)", href="#historic-info"),
                        " (where available: ",
                        html.A("see note here", href="#data-modal"), 
                        ") to give context for each storm event."
                    ]),
                    html.P("All of the charts, maps and tables are interactive in some way, allowing you to filter, sort and investigate the data as you please."),
                    html.P([
                        "Further information about data sources can be found at the ",
                        html.A("bottom of the page", href="#data-info"),
                        "."
                    ]),
                    html.Div(style={"height": "14px"}),
                ], width=9),
                
                dbc.Col([
                    html.A(
                        [
                            html.Img(
                                src="https://www.shropshirestar.com/resizer/R-JBYJySB7d1sV88kojEsofoO0w=/1200x675/cloudfront-us-east-1.images.arcpublishing.com/mna/6RGV7KRRMRDC7JMDGNQFHD7X7U.jpg", 
                                style={"width": "100%"}
                            ), 
                            html.P(
                                "Flooding in Shrewsbury following Storm Gerrit", 
                                style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "font-size": "12px", "margin-bottom": "5px"}
                            ),
                            html.P(
                                "Photo from Shropshire Star", 
                                style={"textAlign": "center", "fontStyle": "italic", "color": "gray", "font-size": "10px"}
                            )
                        ],
                        href="https://www.shropshirestar.com/resizer/R-JBYJySB7d1sV88kojEsofoO0w=/1200x675/cloudfront-us-east-1.images.arcpublishing.com/mna/6RGV7KRRMRDC7JMDGNQFHD7X7U.jpg",
                        target="_blank"
                    ),
                ]),
            ]),
            
            # Warning message
            dbc.Row([
                dbc.Col(
                    html.H6("!!! This site is a work in progress: Still tons of work to do !!!", 
                            style={"textAlign": "center", "color": "red", "fontStyle": "italic", "fontWeight": "bold"}),
                )
            ]),
        ]),

        html.Hr(),  # line break
        
        # GIF with text
        gif_with_text(
            gif_src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjRxa3EyZXZobXN1ZnphaXM4a290c3Fndjg4eGUzb2pvM2tpMnFhNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/32aROMpuC7xqKdWbKO/giphy.gif",
            text1="Yay my code is doing what I want it to.",
            text2="This makes me a happy Stacy."
        ),

    ])
    return layout
