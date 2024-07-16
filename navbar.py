#navbar.py:

from dash import html
import dash_bootstrap_components as dbc

def create_navbar(app):
    # Define paths to the logos within the assets/logos directory
    logo_src = "https://visualpharm.com/assets/818/Cheese-595b40b65ba036ed117d2a6c.svg"
    ea_logo_clip_src = app.get_asset_url('EA_logo_clip.png')
    dash_logo_src = app.get_asset_url('DASH_logo.png')
    apprenticeship_logo="https://nowskills.co.uk/wp-content/uploads/2018/11/Apprenticeships-Logo-PNG.png"
    cs_logo = app.get_asset_url('CS_Logo.png')

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=logo_src, height="50px")),
                            dbc.Col(dbc.NavbarBrand("FETA Homepage", className="ms-2", style={"color": "#008531", "font-weight": "bold"})),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("App powered by", className="ms-2", style={"color": "#008531"}), width="auto"),
                        dbc.Col(html.A(html.Img(src=apprenticeship_logo, height="50px")), width="auto"),
                        dbc.Col(html.A(html.Img(src=cs_logo, height="50px")), width="auto"),
                        dbc.Col(html.A(html.Img(src=ea_logo_clip_src, height="60px")), width="auto", style={"padding-right": "10px"}),
                        dbc.Col(html.A(html.Img(src=dash_logo_src, height="50px")), width="auto"),
                    ],
                    className="g-0 flex-nowrap mt-3 mt-md-0",
                    align="center",
                    justify="center",
                ),
                dbc.DropdownMenu(
                    nav=True,
                    in_navbar=True,
                    label="Navigation",
                    children=[
                        dbc.DropdownMenuItem("Home", href='/'),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Page 1", href='/page-1'),
                        dbc.DropdownMenuItem("Page 2", href='/page-2'),
                        dbc.DropdownMenuItem("Page 3", href='/page-3'),
                    ],
                    className= "ms-auto",
                ),
            ],
            className= "justify-content-between",
        ),
        color="#d9f5ce",
        dark=True,
    )

    return navbar
