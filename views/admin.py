# -*- coding: utf-8 -*-
from datetime import date
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import urllib.parse

from server import app


# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])]
        + [
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ]
    )




# returns top 5 open opportunities
def top_open_opportunities(df):
    #df = df.sort_values("Amount", ascending=True)
    #cols = ["fecha", "Rut", "Nombre_completo", "tipo_cliente", "Celular","tipo"]
    df = df.iloc[:]
    # only display 21 characters
    return df_to_table(df)



layout = [
    html.Div(
        id="lead_grid",
        children=[
        	html.Div(
        		id="detalles",
                className="row pretty_container table",
                children=[
                    html.Div([html.P("Registro visitas")], className="subtitle"),
                    html.Div(id="visitas_tabla", className="table"),
                ],
            ),
            dcc.Store(id="visitas_df", data=pd.read_csv("visitas.csv",sep=';').to_json(orient="split")),
            
                    ],
    ),
    
]

# updates top open opportunities based on df updates
@app.callback(
    Output("visitas_tabla", "children"), [Input("visitas_df", "data")]
)
def top_open_opportunities_callback(df):
    df = pd.read_json(df, orient="split")
    return top_open_opportunities(df)
    
