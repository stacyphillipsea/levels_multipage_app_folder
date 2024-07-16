#page_2.py:
from dash import html
from navbar import create_navbar
from common import gif_with_text, shared_data
from components import hello_component
from page_1 import global_data_dict

nav = create_navbar()

header = html.H3('Welcome to page 2!')

def create_page_2(shared_data):
    # Use shared data in the layout or callbacks as needed
    # For example:
    layout = html.Div([
        nav,
        header,
        html.H1('Page 2'),
        html.Hr(), # line break
        html.Div(f'This is the data you loaded from Page 1: {global_data_dict}'),
        html.Hr(), # line break
        gif_with_text(
            gif_src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGx6cjZuaGZzcmx4cW9sNmN2MDJyeHV6emhudmcxcDR0amw1amJ5cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CuMiNoTRz2bYc/giphy.gif",
            text1="Ooooo this is also working!",
            text2="Yaaaaaaay"
        ),
        html.Hr(), # line break,
        hello_component()
    ])
    return layout
