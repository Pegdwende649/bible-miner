from functools import reduce
import copy 
import plotly.express as px
from plotly.subplots import make_subplots
import pickle
import numpy as np
from io import BytesIO
from collections import Counter
import plotly.graph_objs as go
import glob
import re 
from dash.dependencies import Input, Output, State


import pandas as pd
import requests, base64
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from threading import Timer
import webbrowser
from bs4 import BeautifulSoup
import dash_dangerously_set_inner_html




port = 8888 # or simply open on the default `8050` port
#versions_paths =  glob.glob("./search_engine/data/bibles/*")
FFR_LOGO = "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f1/Logo_FFR_2019.svg/1200px-Logo_FFR_2019.svg.png"
WORLD_CUP_IMAGE = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/08/b549879e-fdc4-4edf-8c6f-61eee59f8a41/920x517_055_agif290857.jpg"
versions_keys = pd.read_csv("./search_engine/data/keys/bible_version_key.csv")


versions_keys_dict = {versions_keys["table"][i]:
                   {"abbreviation":versions_keys["abbreviation"][i],"name":versions_keys["version"][i],"info_url":versions_keys["info_url"][i]}
                   for i in range(len(versions_keys))}


def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='English bibles', value='tab-1'),
        dcc.Tab(label='French bibles', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])




### COMPONENTS BUILDING ###

# NAVBAR component 

nav_item = dbc.NavItem(dbc.NavLink('Github',href = "https://github.com/Pegdwende649/"))
dropdown = dbc.DropdownMenu(children = [dbc.DropdownMenuItem('The author',href='https://github.com/Pegdwende649/'),
                                        dbc.DropdownMenuItem(divider = True),
                                        dbc.DropdownMenuItem('ENSAI',href='https://ensai.fr')],
                           nav =True,
                           in_navbar = True,
                           label = 'A propos ')


navbar = dbc.Navbar(
    dbc.Container(
            [
                html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=FFR_LOGO, height="30px")),
                                dbc.Col(dbc.NavbarBrand("BIBLE MINER", className="ml-2")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="https://github.com/Pegdwende649/bible-miner",
                     ),
               dbc.NavbarToggler(id="navbar-toggler"),
               dbc.Collapse(dbc.Nav([nav_item,dropdown],className = 'ml-auto',navbar=True), id="navbar-collapse", navbar=True),
            ],
    ),
    color="dark",
    dark=True,
    className = 'mb5')

# CARDS components

cards = []


DropDownModal = html.Div([html.P("CHOISISSEZ UNE STATISTIQUE"),
            dcc.Dropdown(
                id='dropdown_stats_graphs',
                value = "game_actions_",

                options=[{'value': "game_actions_" ,'label': "Actions du jeu"},
                         {'value' : "ruck_" ,'label':'Vitesse du Ruck'},
                         {'value' : "kick_" ,'label':'Jeu au pied'},
                        ],
                placeholder="Choisissez une statistique",
            ),
        ]) 


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}


for version_key in versions_keys_dict.keys():
    version_name = versions_keys_dict[version_key]["abbreviation"]
    

    r = requests.get(versions_keys_dict[version_key]["info_url"], headers=headers)#, proxies=proxies)
    content = r.content
    soup = BeautifulSoup(content)
    
    for d in soup.findAll('div',attrs={'class':'mw-parser-output'}):
        info_text = d.find('p')
    
    logo_filename = "./search_engine/images/logo_"+version_name+".png" # replace with your own image
    encoded_image = base64.b64encode(open(logo_filename, 'rb').read())
    card = dbc.Card(
        [
            dbc.CardBody(dbc.CardImg(src='data:image/png;base64,{}'.format(encoded_image.decode()),top = True)),
            dbc.CardBody(
                [
                    html.H4(versions_keys_dict[version_key]["name"], className="card-title"),
                    html.P(
                        "",
                        className="card-text"+version_name,
                    ),
                    dbc.Button("More", color="primary",id = "open-"+version_name),
                    dbc.Modal(
                                          [
                                            dbc.ModalHeader(versions_keys_dict[version_key]["name"]),
                                            dbc.ModalBody([
                                                #html.Div(version_name, className="card-title")
                                                html.Div([dash_dangerously_set_inner_html.DangerouslySetInnerHTML(""" """+str(info_text)+"\n\n <b>Wikipedia</b>")])]),

                                                dbc.ModalFooter(
                                                dbc.Button("Close", id="close-"+version_name, className="ml-auto")
                                            )
                                          ],id = "modal-"+version_name,size = "xl"
                            ),
                    

                ],
                id = "card-body-"+version_name

            ),

        ],
        style={"width": "8rem"},
    )
    cards.append(card)
cards = dbc.CardDeck(cards)

### COMPONENTS INSERTION ###

layout_tab1 = html.Div(
    [navbar,cards])


layout_tab2 = html.Div(
    [navbar])



#### Callbacks


# Tabs callback
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    
    if tab == 'tab-1':        
        return  layout_tab1
                                           
     
    elif tab == 'tab-2':        
        return layout_tab2
 

# modals callbacks

modal_code_to_exec = ""
for version_key in versions_keys_dict.keys():
    version_name = versions_keys_dict[version_key]["abbreviation"]
    modal_code_to_exec += "@app.callback(\n Output(\"modal-"+version_name+"\", \"is_open\"),\n [Input(\"open-"+version_name+"\", \"n_clicks\"), Input(\"close-"+version_name+"\", \"n_clicks\")],\n [State(\"modal-"+version_name+"\", \"is_open\")],\n )\ndef toggle_modal_"+version_name+" (n1, n2, is_open):\n \t if n1 or n2:\n \t \t return not is_open \n \t return is_open\n\n" 

exec(modal_code_to_exec)

if __name__ == "__main__":
    Timer(1, open_browser).start();
    app.run_server(port = port)#,debug=True,use_reloader=False)



"""
def enconde_image(image_url):
    buffered = BytesIO(requests.get(image_url).content)
    image_base64 = base64.b64encode(buffered.getvalue())
    return b'data:image/png;base64,' + image_base64

Img = html.Div(html.Img(src=WORLD_CUP_IMAGE, style={'width': '100%', 'height':'200px'}))


DropdownApp = html.Div([html.P("CHOISISSEZ UNE EQUIPE"),
    dcc.Dropdown(
        id='team_id',
        value = 1133,
        options=[{'value': x, 'label': renameteams[str(x)]} for x in teams],
        placeholder="Select a team",
    ),
        html.Div(id='output-container')
])


GraphGlobal = html.Div(className='graph_g',  # Define the row element
                               
                       
                       
                       children = [html.Div(className = 'graph_global_classname',children = [dcc.Graph(id = "possesion_time"),
                                                                                                         dcc.Graph(id="graph_global")],
                                                                                                     )])

DropdownAppPlayers = html.Div([html.P("CHOISISSEZ UNE CLASSE"),
    dcc.Dropdown(
        id='class_id',
        value = 1,
        options=[{'value': x, 'label': "Classe "+str(x) } for x in dict_Joueur.keys()],
        placeholder="Select a team",
    ),
    html.Div(id='output-container-players')
])
    
"""
"""app.layout = html.Div(
    [navbar,DropdownApp,GraphGlobal]
)
"""
# CALLBACKS #


"""
layout_tab1 = html.Div(
    [navbar,DropdownApp,GraphGlobal])


layout_tab2 = html.Div(
    [navbar,DropdownAppPlayers])


  
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        
        return  layout_tab1
                                           
    # Define the left element
     
    elif tab == 'tab-2':
        
        return layout_tab2




#dropdown App
@app.callback(
    Output('output-container', 'children'),
    [Input('team_id', 'value')])
def update_dropdown(team_id):
    team_id_display = renameteams[str(team_id)]
    cards = []
    for match_id in enumerate(sorted(teams_actions_ct_sorted_dict[team_id].keys())):
        match_num = match_id[0]
        opposed_team_id = set(matches_list[match_id[1]])-set([team_id])
        opposed_team_display = renameteams[str(list(opposed_team_id)[0])]

        if scores[match_id[1]][team_id]>scores[match_id[1]][list(opposed_team_id)[0]]:
            button_color =  "success"
        elif scores[match_id[1]][team_id]==scores[match_id[1]][list(opposed_team_id)[0]]:
            button_color = "warning"
        else:
            button_color =  "danger"
       
        Graphs = html.Div(className='pie',  # Define the row element
                                   children = [html.Div(className = 'graphs',children = [dcc.Graph(id="chart_pie",figure = team_actions_pie1(team_id,match_id[1])),
                                                                                         dcc.Graph(id="chart_bars",figure = plot_kicks(team_id,match_id[1])),
                                                                                         dcc.Graph(id="chart_rucks",figure = plotVitesseRuck(match_id[1])[0]),
        
                                                                                         dcc.Graph(id="chart_rucks",figure = plotVitesseRuck(match_id[1])[1])])])
        GraphsDivs = html.Div(className = "eg",children = [dcc.Graph(id="effective_graph_fig")])
        DropDownModal = html.Div([html.P("CHOISISSEZ UNE STATISTIQUE"),
            dcc.Dropdown(
                id='dropdown_stats_graphs',
                value = "game_actions_" + str(team_id)+"_"+str(match_id[1]),

                options=[{'value': "game_actions_" + str(team_id)+"_"+str(match_id[1]), 'label': "Actions du jeu"},
                         {'value' : "ruck_" + str(team_id)+"_"+str(match_id[1]),'label':'Vitesse du Ruck'},
                         {'value' : "kick_" + str(team_id)+"_"+str(match_id[1]),'label':'Jeu au pied'},
                        ],
                placeholder="Choisissez une statistique",
            ),
        ])
        
        card =   dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("MATCH " + str(1+match_num), className="card-title" + str(match_num)),
                                html.P(
                                    "SCORE: " + str(scores[match_id[1]][team_id])+" - "+str(scores[match_id[1]][list(opposed_team_id)[0]])
                                ),
                                html.P("ADVERSAIRE: "+opposed_team_display, className="card-text"+str(match_num)),
                                dbc.Button(
                                    "GRAPHIQUES", id="open"+str(match_num), color=button_color,className="mt-auto"+ str(match_num)
                                ),
                                dbc.Modal(
                                          [
                                            dbc.ModalHeader("Statistiques du match "+team_id_display+" VS "+opposed_team_display),
                                            dbc.ModalBody([DropDownModal,Graphs]),
                                            dbc.ModalFooter(
                                            dbc.Button("Close", id="close"+str(match_num), className="ml-auto"+str(match_num)),
                            ),
                        ],id="modal"+str(match_num),size = 'xl'
),]
                        )
                    )
        cards.append(card)
    cards = dbc.CardDeck(cards)
    
    return cards





@app.callback(
    Output('output-container-players', 'children'),
    [Input('class_id', 'value')])
def update_dropdown_players(class_id):
    print(class_id)
    cards = []

    #for class_ in dict_Joueur.keys():
    for player in dict_Joueur[class_id][:10]:
        card =   dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Button(
                                    "Joueur: " + str(player), className="card-title")
                                #<id="open"+str(match_num), color=button_color,className="mt-auto"+ str(match_num)
                                                                #html.H5("Joueur :" + str(player), className="card-title"),
                                ]))
        cards.append(card)
    cards = dbc.CardDeck(cards)
        
    return cards

   


#dropdown App
@app.callback(
    Output('graph_global', 'figure'),
    [Input('team_id', 'value')])
def plotglobalPossesion(team_id):

    fig = plotAllPossesion(team_id)
                                                                                                         
    return fig


@app.callback(
    Output('effective_graph_fig', 'figure'),
    [Input('dropdown_stats_graphs', 'value')])

def plot_effective_graphs(graph_id):
    #print(graph_id) 
    if "game_actions" in graph_id:
        
        fig = team_actions_pie1(int(graph_id[-16:][:4]),int(graph_id[-16:][5:]))  
    elif "ruck" in graph_id:
        print("ruck")
        fig = plotVitesseRuck(int(graph_id[-16:][:4]),int(graph_id[-16:][5:]))
    elif "kick" in graph:
        fig = plot_kicks(int(graph_id[-16:][:4]),int(graph_id[-16:][5:]))
        print("kick")
        
    return fig

    

@app.callback(
    Output('possesion_time', 'figure'),
    [Input('team_id', 'value')])
def plot_possession(team_id):
    fig = plotPossesion(team_id)  
    return fig

    



@app.callback(
    Output("modal0", "is_open"),
    [Input("open0", "n_clicks"), Input("close0", "n_clicks")],
    [State("modal0", "is_open")],
)
def toggle_modal0(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal1", "is_open"),
    [Input("open1", "n_clicks"), Input("close1", "n_clicks")],
    [State("modal1", "is_open")],
)
def toggle_modal1(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



@app.callback(
    Output("modal2", "is_open"),
    [Input("open2", "n_clicks"), Input("close2", "n_clicks")],
    [State("modal2", "is_open")],
)
def toggle_modal2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal3", "is_open"),
    [Input("open3", "n_clicks"), Input("close3", "n_clicks")],
    [State("modal3", "is_open")],
)
def toggle_modal3(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal4", "is_open"),
    [Input("open4", "n_clicks"), Input("close4", "n_clicks")],
    [State("modal4", "is_open")],
)
def toggle_modal4(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal5", "is_open"),
    [Input("open5", "n_clicks"), Input("close5", "n_clicks")],
    [State("modal5", "is_open")],
)
def toggle_modal5(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal6", "is_open"),
    [Input("open6", "n_clicks"), Input("close6", "n_clicks")],
    [State("modal6", "is_open")],
)
def toggle_modal6(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("modal7", "is_open"),
    [Input("open7", "n_clicks"), Input("close7", "n_clicks")],
    [State("modal7", "is_open")],
)
def toggle_modal7(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



#add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
"""




html_doc = """<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc, 'html.parser')

print(soup.prettify())
# <html>
#  <head>
#   <title>
#    The Dormouse's story
#   </title>
#  </head>
#  <body>
#   <p class="title">
#    <b>
#     The Dormouse's story
#    </b>
#   </p>
#   <p class="story">
#    Once upon a time there were three little sisters; and their names were
#    <a class="sister" href="http://example.com/elsie" id="link1">
#     Elsie
#    </a>
#    ,
#    <a class="sister" href="http://example.com/lacie" id="link2">
#     Lacie
#    </a>
#    and
#    <a class="sister" href="http://example.com/tillie" id="link3">
#     Tillie
#    </a>
#    ; and they lived at the bottom of a well.
#   </p>
#   <p class="story">
#    ...
#   </p>
#  </body>
# </html>

import dash
import dash_html_components as html
import base64

app = dash.Dash()

image_filename = 'search_engine/images/logo_kjv.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
])

if __name__ == '__main__':
    app.run_server()