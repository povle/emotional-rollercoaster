from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from bin.components import *
from bin.algorithms import *
from bin.helpers import ids
from config.config import *

import plotly.express as px

app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Load data
df = prepare_data(PATH_TO_CSV_FILE)
# Process data
df = moving_average(df, GLOBAL_WINDOW_SIZE)
unique_peers = df.index.get_level_values('peer_id').unique()
# Actual {peer_id: name_of_chat}
peers_decyphered = {peer: ids[peer] for peer in unique_peers}

app.layout = html.Div([
    navbar,
    html.Div(generate_dropdown(peers_decyphered, id='dropdown')),
    # Initialize graph
    html.Div(dcc.Graph(id='graph')),
])

# Callback to update data with date picker and return graph to layout.
@app.callback(
    Output('graph', 'figure'),
    Input('dropdown', 'value'))
def update_graph(value):
    # Filter dataframe by peer_id
    df_filtered = df.loc[value]
    # Plot the data
    fig = px.line(x=df_filtered.index, y=df_filtered.sentiment)
    # Add axhline by sum divide by number of rows
    fig.add_shape(
        type="line",
        x0=df_filtered.index[0],
        y0=df_filtered.sentiment.sum() / len(df_filtered.sentiment),
        x1=df_filtered.index[-1],
        y1=df_filtered.sentiment.sum() / len(df_filtered.sentiment),
        line=dict(
            color="red",
            width=2,
            dash="dash"
        )
    )
    return fig
    

if __name__ == "__main__":
    app.run_server(debug=True)