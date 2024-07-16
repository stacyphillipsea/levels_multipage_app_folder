#home.py:

from dash import html
from navbar import create_navbar
from common import gif_with_text, global_data_dict

nav = create_navbar()

header = html.H1('Welcome to the Flood Event Telemetry Analyser (FETA)')


def create_page_home():
    # Use shared data in the layout or callbacks as needed
    # For example:
    layout = html.Div([
        nav,
        header,
        # html.H1('Home Page'),
        # html.Hr(), # line break
        gif_with_text(
            gif_src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjRxa3EyZXZobXN1ZnphaXM4a290c3Fndjg4eGUzb2pvM2tpMnFhNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/32aROMpuC7xqKdWbKO/giphy.gif",
            text1="Yay my code is doing what I want it to.",
            text2="This makes me a happy Stacy."
        )
    ])
    return layout
