#app.py:
import dash
import dash_bootstrap_components as dbc
import os  
from navbar import create_navbar

asst_path = os.path.join(os.getcwd(), "assets_folder")

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True, 
                external_stylesheets=[dbc.themes.MINTY],
                assets_folder=asst_path)

nav = create_navbar(app)
