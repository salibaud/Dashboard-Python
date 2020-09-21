# -*- coding: utf-8 -*-
from datetime import date
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import urllib.parse
from flask_login import logout_user, current_user




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
    cols = ["fecha", "Rut", "Nombre_completo", "tipo_cliente", "Celular","tipo"]
    df = df[cols].iloc[:50]
    # only display 21 characters
    df["Nombre_completo"] = df["Nombre_completo"].apply(lambda x: x[:30])
    return df_to_table(df)


layout = [
    html.Div(
        id="lead_grid",
        children=[
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="converted_opportunities_dropdown",
                    options=[
                        {"label": "By day", "value": "D"},
                        {"label": "By week", "value": "W-MON"},
                        {"label": "By month", "value": "M"},
                    ],
                    value="E",
                    clearable=False,
                ),
            ),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="converted_opportunities_dropdown",
                    options=[
                        {"label": "By day", "value": "D"},
                        {"label": "By week", "value": "W-MON"},
                        {"label": "By month", "value": "M"},
                    ],
                    value="D",
                    clearable=False,
                ),
            ),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="heatmap_dropdown",
                    options=[
                        {"label": "All stages", "value": "all_s"},
                        {"label": "Cold stages", "value": "cold"},
                        {"label": "Warm stages", "value": "warm"},
                        {"label": "Hot stages", "value": "hot"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
            ),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="source_dropdown",
                    options=[
                        {"label": "All sources", "value": "all_s"},
                        {"label": "Web", "value": "Web"},
                        {"label": "Word of Mouth", "value": "Word of mouth"},
                        {"label": "Phone Inquiry", "value": "Phone Inquiry"},
                        {"label": "Partner Referral", "value": "Partner Referral"},
                        {"label": "Purchased List", "value": "Purchased List"},
                        {"label": "Other", "value": "Other"},
                    ],
                    value="all_c",
                    clearable=False,
                ),
            ),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="source_dropdown1",
                    options=[
                        {"label": "All sources", "value": "All"},
                        {"label": "Web", "value": "Web"},
                        {"label": "Word of Mouth", "value": "Word of mouth"},
                        {"label": "Phone Inquiry", "value": "Phone Inquiry"},
                        {"label": "Partner Referral", "value": "Partner Referral"},
                        {"label": "Purchased List", "value": "Purchased List"},
                        {"label": "Other", "value": "Other"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
            ),
            html.A('Descargar',id='descargar',download="rawdata.csv",href="",target="_blank",className="button"),
            
            
           
           
            html.Div(
                id="detalles",
                className="row pretty_container table",
                children=[
                    html.Div([html.P("Explorar maestro")], className="subtitle"),
                    html.Div(id="top_open_opportunities", className="table"),
                ],
            ),
            dcc.Store(id="leads_df", data=pd.read_csv("maestro.csv").to_json(orient="split")),
            dcc.Store( id="detalle_df", data=pd.read_csv("maestro.csv").to_json(orient="split")),
            
                    ],
    ),
    
]



def filter_data(value):
        return pd.read_json(pd.read_csv("maestro.csv").to_json(orient="split"), orient="split")


# updates top open opportunities based on df updates
@app.callback(
    Output("top_open_opportunities", "children"), [Input("detalle_df", "data")]
)
def top_open_opportunities_callback(df):
    df = pd.read_json(df, orient="split")
    return top_open_opportunities(df)
    

@app.callback(
    Output('descargar', 'href'),
    [Input('source_dropdown1', 'value')])
def update_download_link(filter_value):
    dff = filter_data(filter_value)
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string