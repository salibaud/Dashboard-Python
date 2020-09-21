# -*- coding: utf-8 -*-
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
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


def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value"),
            html.P(text, className="twelve columns indicator_text"),
        ],
        className="four columns indicator pretty_container",
    )
    


#grafico barras horizontal
def cases_by_account(cases):
    #cases = cases.dropna(subset=["id"])
    #cases = pd.merge(cases, accounts, left_on="AccountId", right_on="Id")
    cases = cases.groupby(["Marca_cotizacion"]).count()
    cases = cases.sort_values("id")
    data = [
        go.Bar(
            y=cases.index.get_level_values("Marca_cotizacion"),
            x=cases["id"],
            orientation="h",
            marker=dict(color="#0073e4"),
        )
    ]  # x could be any column value since its a count

    layout = go.Layout(
        autosize=True,
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}



# Grafico de tortas
def lead_source(status, df):
#    if status == "open":
#        df = df[
#            (df["Status"] == "Open - Not Contacted")
#            | (df["Status"] == "Working - Contacted")
#        ]
#
##    elif status == "converted":
#        df = df[df["Status"] == "Closed - Converted"]
#
#    elif status == "lost":
#        df = df[df["Status"] == "Closed - Not Converted"]

    nb_leads = len(df.index)
    types = df["tipo"].unique().tolist()
    values = []

    # compute % for each leadsource type
    for case_type in types:
        nb_type = df[df["tipo"] == case_type].shape[0]
        values.append(nb_type / nb_leads * 100)

    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(autosize=True, margin=dict(l=15, r=10, t=0, b=65))
    return dict(data=[trace], layout=layout)


def converted_leads_count(period, df):
    #df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
    df['fecha']=df['fecha'].apply(lambda x: pd.to_datetime(x))
    df["fecha"] = pd.to_datetime(df["fecha"],utc=True, format="%Y-%m-%d")
    df['fecha'] = df['fecha'].dt.date
    #df = df[df["Status"] == "Closed - Converted"]

    df = (
        df.groupby([pd.Grouper(key="fecha")])
        .count()
        .reset_index()
        .sort_values("fecha")
    )

    trace = go.Scatter(
        x=df["fecha"],
        y=df["id"],
        name="Clientes creados",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        autosize=True,
        xaxis=dict(showgrid=False),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


layout = [

    html.Div(

        
        id="lead_grid",
        children=[    
     #   dcc.Location(id='url_login_success', refresh=True),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="converted_leads_dropdown",
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
                    id="lead_source_dropdown",
                    options=[
                        {"label": "Todos", "value": "all"},
                        {"label": "Clientes", "value": "Clientes"},
                        {"label": "Cotizantes", "value": "Cotizantes"},
                        {"label": "Leads", "value": "Leads"},
                    ],
                    value="all",
                    clearable=False,
                ),
            ),

           # html.Span(
           #     "Add new",
           #     id="new_lead",
           #     n_clicks=0,
           #     className="button pretty_container",
           # ),
            html.Div(
                className="row indicators",
                children=[
                    indicator("#00cc96", "Clientes", "left_leads_indicator"),
                    indicator("#119DFF", "Cotizaciones", "middle_leads_indicator"),
                    indicator("#EF553B", "Leads", "right_leads_indicator"),
                ],
            ),
            
            html.Div(
                id="leads_per_state",
                className="chart_div pretty_container",
                children=[
                    html.P("Leads count per state"),
                    dcc.Graph(
                        id="map",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="leads_source_container",
                className="chart_div pretty_container",
                children=[
                    html.P("Leads by source"),
                    dcc.Graph(
                        id="lead_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="converted_leads_container",
                className="chart_div pretty_container",
                children=[
                    html.P("Converted Leads count"),
                    dcc.Graph(
                        id="converted_leads",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(id="leads_table", className="row pretty_container table"),
            dcc.Store(id="leads_df", data=pd.read_csv("maestro.csv").to_json(orient="split")),
            dcc.Store( id="detalle_df", data=pd.read_csv("maestro.csv").to_json(orient="split")),
        ],
    ),
 
    #modal(),
]


# updates left indicator based on df updates
@app.callback(Output("left_leads_indicator", "children"), [Input("leads_df", "data")])
def left_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    converted_leads = len(df[df["tipo"] == "Cliente"].index)
    return dcc.Markdown("**{}**".format(converted_leads))


# updates middle indicator based on df updates
@app.callback(Output("middle_leads_indicator", "children"), [Input("leads_df", "data")])
def middle_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    open_leads = len(
        df[
            (df["tipo"] == "Cotizante") 
        ].index
    )
    return dcc.Markdown("**{}**".format(open_leads))


# updates right indicator based on df updates
@app.callback(Output("right_leads_indicator", "children"), [Input("leads_df", "data")])
def right_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    converted_leads = len(df[df["tipo"] == "Cliente"].index)
    #lost_leads = len(df[df["Status"] == "Closed - Not Converted"].index)
    #conversion_rates = converted_leads / (converted_leads + lost_leads) * 100
    #conversion_rates = "%.2f" % conversion_rates + "%"
    conversion_rates = 0
    return dcc.Markdown("**{}**".format(conversion_rates))


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("lead_source", "figure"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "data")],
)
def lead_source_callback(status, df):
    df = pd.read_json(df, orient="split")
    return lead_source(status, df)


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("map", "figure"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "data")],
)
def map_callback(status, df):
    df = pd.read_json(df, orient="split")
    return cases_by_account(df)


# update table based on dropdown's value and df updates
@app.callback(
    Output("leads_table", "children"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "data")],
)
def leads_table_callback(status, df):
    df = pd.read_json(df, orient="split")
    if status == "Clientes":
        df = df[
            (df["tipo"] == "Cliente")
        ]
    elif status == "Cotizantes":
        df = df[df["tipo"] == "Cotizante"]
    elif status == "Leads":
        df = df[df["tipo"] == "Leads"]
    df = df[["fecha", "Rut", "Nombre_completo", "tipo_cliente", "Celular","tipo"]]
    return df_to_table(df)


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("converted_leads", "figure"),
    [Input("converted_leads_dropdown", "value"), Input("leads_df", "data")],
)
def converted_leads_callback(period, df):
    df = pd.read_json(df, orient="split")
    return converted_leads_count(period, df)


# hide/show modal
@app.callback(Output("leads_modal", "style"), [Input("new_lead", "n_clicks")])
def display_leads_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# reset to 0 add button n_clicks property
@app.callback(
    Output("new_lead", "n_clicks"),
    [Input("leads_modal_close", "n_clicks"), Input("submit_new_lead", "n_clicks")],
)
def close_modal_callback(n, n2):
    return 0

server = app.server
@server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(server.root_path, 'static'),
                                     'favicon.ico')