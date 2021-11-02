### Components for the Dashboard ###

import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc

def generate_date_picker(df, id='date_picker'):
    date_picker = html.Div([
    dcc.DatePickerRange(id=id,
                        min_date_allowed=df.index[0],
                        max_date_allowed=df.index[-1],
                        start_date=df.index[0],
                        end_date=df.index[-1]),
])
    return date_picker

def generate_dropdown(dictionary, id='dropdown'):
    dropdown = html.Div([
    dcc.Dropdown(id=id,
                 options=[{'label': dictionary[key], 'value': key} for key, value in dictionary.items()],
                 value=list(dictionary.items())[0][0])
])
    return dropdown

badge = dbc.Button(
    [
        "Notifications",
        dbc.Badge("4", color="light", text_color="primary", className="ms-1"),
    ],
    color="primary",
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="🎢 Emotional Rollercoaster",
    brand_href="#",
    color="primary",
)

button = html.Div(
    [
        dbc.Button(
            "Click me", id="example-button", className="me-2", n_clicks=0
        ),
        html.Span(id="example-output", style={"verticalAlign": "middle"}),
    ]
)

dropdown = html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='NYC'
    ),
    html.Div(id='dd-output-container')
])

