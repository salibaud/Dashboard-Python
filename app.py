# index page
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sqlalchemy.sql import select
from flask_caching import Cache
from server import app, server
from flask_login import logout_user, current_user
from views import login, login_fd, logout,leads,detalles,admin
from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from config import engine
import json
from datetime import date
import pandas as pd

db = SQLAlchemy()

cache = Cache(app.server, config={"CACHE_TYPE": "simple"})

cache.clear()
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    compania = db.Column(db.String(20))
    tipo_usuario = db.Column(db.String(20))
    nivel = db.Column(db.String(20))





# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])]
        + [
            html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ]
    )



# returns most significant part of a number
def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


# returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            html.P(id=id_value, className="indicator_value"),
            html.P(text, className="twelve columns indicator_text"),
        ],
        className="four columns indicator pretty_container",
    )
    
header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.Img(src='assets/dash-logo-stripe.svg',className='logo'),
            #html.Img(src=app.get_asset_url("logo_jpn.png")),
            html.Div(className='links', children=[
                #html.Div(id='panel1', className='link1'),
                #html.Div(id='panel2', className='link1'),
                html.Div(id='separador', className='link'),
                html.Div(id='administrador', className='link'),
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link'),
                
            ]),
            html.Div(className='links1', children=[
                html.Div(id='panel1', className='link1'),
                html.Div(id='panel2', className='link1'),
                html.Div(id='registro_visitas', className='link'),
               # html.Div(id='logout', className='link')
            ]),
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Link(
            href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
            rel="stylesheet",
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"
        ),
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return login.layout
    elif pathname == '/login':
        return login.layout
    elif pathname == '/leads':
        if current_user.is_authenticated():
        		return leads.layout
    elif pathname == '/admin':
        if current_user.is_authenticated():
        	if current_user.username=='admin':
        		return admin.layout
    elif pathname == '/detalles':
        if current_user.is_authenticated():
            return detalles.layout
        else:
            return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated():
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404'


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated():
        return html.Div('Usuario: ' + current_user.username)
        # 'User authenticated' return username in get_id()
    else:
        return ''

@app.callback(
    Output('administrador', 'children'),
    [Input('page-content', 'children')])
def administrador(input1):
	nivel='(cliente)'
	if current_user.is_authenticated():
		User_tbl = Table('user', User.metadata)
		select_st = select([User_tbl.c.username, User_tbl.c.email,User_tbl.c.nivel])
		conn = engine.connect()
		rs = conn.execute(select_st)
		try:
			for i in rs:
				if i[0] == current_user.username:
					if i[2]=="admin":
						nivel="admin"
						return html.A('Administración', href='/admin')
		except:
			return ''
	else:
		return ''
        






@app.callback(
    Output('separador', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated():
        return html.Div('|         ')
        # 'User authenticated' return username in get_id()
    else:
        return ''



@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated():
        return html.A('Salir', href='/logout')
    else:
        return ''



@app.callback(
    Output('panel1', 'children'),
    [Input('page-content', 'children')])
def user_panels(input1):
    if current_user.is_authenticated():
        return html.A('Leads', href='/leads')
    else:
        return ''


@app.callback(
    Output('panel2', 'children'),
    [Input('page-content', 'children')])
def user_panels(input1):
    if current_user.is_authenticated():
        return html.A('Detalle', href='/detalles')
    else:
        return ''
        
        
@app.callback(
    Output('registro_visitas', 'children'),
    [Input('url', 'pathname')])
def registro_visitas(input1):
	registro = pd.read_csv("visitas.csv",sep=';')
	useri="visita"
	if current_user.is_authenticated():
		useri=current_user.username
	pagina=input1
	visita='1'
	fecha=date.today()
	datos =[useri,pagina,visita,fecha]
	datos1=(pd.DataFrame(datos).T).rename(columns={0:"usuario",1:"pagina",2:"visita",3:"fecha"}).reset_index(drop=True)
	registro=registro.append(datos1)
	registro.drop_duplicates(keep = False, inplace = True) 
	registro.to_csv("visitas.csv",sep=';', index=False)
	numero_visitas=registro.count()
	return ''






if __name__ == '__main__':
    app.run_server(debug=True)
