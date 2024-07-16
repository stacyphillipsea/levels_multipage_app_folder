#navbar.py:

import dash_bootstrap_components as dbc
from dash import html


def create_navbar():

    # Create the logo element
    logo = html.A(html.Img(src="https://visualpharm.com/assets/818/Cheese-595b40b65ba036ed117d2a6c.svg",
                           height="50px"), href="/")
    
    # Create the brand text element
    brand_text = html.Span("FETA Homepage", style={'margin-left': '10px'})

    # Combine the image and brand text in a div
    brand_content = html.Div([logo, brand_text], style={'display': 'flex', 'align-items': 'center'})
    
    # Create the Navbar using Dash Bootstrap Components
    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Navigation", # Label given to the dropdown menu
                children=[
                    # In this part of the code we create the items that will appear in the dropdown menu on the right
                    # side of the Navbar.  The first parameter is the text that appears and the second parameter 
                    # is the URL extension.
                    dbc.DropdownMenuItem("Home", href='/'), # Hyperlink item that appears in the dropdown menu
                    dbc.DropdownMenuItem(divider=True), # Divider item that appears in the dropdown menu 
                    dbc.DropdownMenuItem("Page 1", href='/page-1'), # Hyperlink item that appears in the dropdown menu
                    dbc.DropdownMenuItem("Page 2", href='/page-2'), # Hyperlink item that appears in the dropdown menu
                    dbc.DropdownMenuItem("Page 3", href='/page-3'), # Hyperlink item that appears in the dropdown menu
                    
                ],
            ),
        ],
        brand=brand_content,  # Set the brand_content on the left side of the Navbar
        brand_href="/",  # Set the URL where the user will be sent when they click the brand we just created "Home"
        sticky="top",  # Stick it to the top... like Spider Man crawling on the ceiling?
        color="primary",  # Change this to change color of the navbar e.g. "primary", "secondary" etc.
        dark=True,  # Change this to change color of text within the navbar (False for light text)
    )

    return navbar
