#page_3.py:
from dash import html
from navbar import create_navbar
from common import gif_with_text

nav = create_navbar()

header = html.H3('Welcome to page 3!')


def create_page_3(shared_data):
    # Use shared data in the layout or callbacks as needed
    # For example:
    layout = html.Div([
        nav,
        header,
        html.H1('Page 3'),
        html.Hr(), # line break
        html.Div(f'Shared data: {shared_data}'),
        html.Hr(), # line break
        gif_with_text(
            gif_src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXhld2FuMjh0NWVrc2cxZzB4dXpkcW9jbGt0OGxyeXFmajlhODVyZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/k5lj4s1qxaSyI/giphy.gif",
            text1="Wow, even on page 3 the code still works!",
            text2="Was not expecting that..."
        )
    ])
    return layout
