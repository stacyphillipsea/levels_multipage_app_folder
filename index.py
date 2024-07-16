#index.py:
from dash import html, dcc
from dash.dependencies import Input, Output
from home import create_page_home
from page_1 import create_page_1
from page_2 import create_page_2
from page_3 import create_page_3
from app import app

server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Update the callback to pass the fetched data to create_page_1
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/page-1':
        # Pass global_data_dict to create_page_1
        return create_page_1(shared_data)
    elif pathname == '/page-2':
        return create_page_2(shared_data)
    elif pathname == '/page-3':
        return create_page_3(shared_data)
    else:
        return create_page_home()


if __name__ == '__main__':
    app.run_server(debug=False)
