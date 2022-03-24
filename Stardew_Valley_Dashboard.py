#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Import libraries
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

#Function to create figure
def create_fig(metric, metric_format, title_1, title_2, image, image_size):
    #Add indicator
    fig = go.Figure(go.Indicator(
        mode = 'number',
        value = metric,
        number = {'valueformat': metric_format, 'font.size': 50},
        domain = {'x': [0, 1], 'y': [0, 0.65]}))

    #Add title
    fig.update_layout(title = {'text': '{}<br>{}'.format(title_1, title_2), 'x': 0.5, 'xanchor': 'center', 'y': 0.1, 'yanchor': 'top', 'font.size': 12},
                      paper_bgcolor='rgba(0,0,0,0)',
                      font_color='white',
                      autosize=False,
                      width=180,
                      height=180,
                      margin=dict(l=2, r=2, b=2, t=2))
    
    #Add image. Use image_base64 if image is stored locally
    image_base64 = base64.b64encode(open(image, 'rb').read()).decode('ascii')
        
    fig.add_layout_image(
            dict(source='data:image/png;base64,{}'.format(image_base64),
            xref='paper', yref='paper',
            x=0.5, y=0.48,
            sizex=image_size, sizey=image_size,
            xanchor='center', yanchor='bottom'))

    return fig

#Function to import save file, extract all metrics and create figures
def refresh_data():
    #Import save file. Replace <path> with path to save file
    with open('<path>', 'r') as f:
        soup = BeautifulSoup(f, 'lxml')

    #Get all relevant item blocks
    items = [x for x in soup.find_all('item') if x.find('name') != None]
    groups = [[x for x in y if x.find('name') != None] for y in soup.find_all('items')]
    buildings = [x.find_all('displayname') for x in soup.find_all('building') if 'Deluxe' in x.find('buildingtype').text]
    trees = [x for x in soup.find_all('item') if x.find('fruitsontree') != None]
    crops = [x for x in soup.find_all('item') if x.find('crop') != None]

    #Get metrics from save file
    #Diamond replication progress
    minutesuntilready_diamond = int(max([x.find_all('minutesuntilready')[1].text for x in items if x.find('name').text == 'Crystalarium']))
    totalminutes_diamond = 5*24*60
    progress_diamond = (totalminutes_diamond - minutesuntilready_diamond) / totalminutes_diamond

    #Diamonds on hand
    on_hand_diamond = np.array([int(x.find('stack').text) for x in groups[0] if x.find('name').text == 'Diamond']).sum()

    #Years Penny will still love me
    years_diamond = on_hand_diamond / (28 * 4)

    #Triple shot espressos
    on_hand_coffees = np.array([int(x.find('stack').text) for x in groups[35] if x.find('name').text == 'Coffee']).sum()
    on_hand_espressos = np.array([int(x.find('stack').text) for x in groups[0] if x.find('name').text == 'Triple Shot Espresso']).sum()
    total_espressos = (on_hand_coffees / 3) + on_hand_espressos

    #Hay level in silos
    hay_silos = int(soup.find('piecesofhay').text)
    capacity_silos = 960
    hay_level_silos = hay_silos / capacity_silos

    #Hay level in barns and coops
    hay_feeders = np.array([len([x.text for x in y if x.text == 'Hay']) for y in buildings]).sum()
    capacity_feeders = 108
    hay_level_feeders = hay_feeders / capacity_feeders

    #Hay on hand
    on_hand_hay = np.array([int(x.find('stack').text) for x in groups[0] if x.find('name').text == 'Hay']).sum() + np.array([int(x.find('stack').text) for x in groups[1] if x.find('name').text == 'Hay']).sum()

    #Animal products ready
    animal_products_ready = np.array([np.array([int(x.find('stack').text) for x in y]).sum() for y in groups[2:7]]).sum() + np.array([np.array([int(x.find('stack').text) for x in y]).sum() for y in groups[29:32]]).sum()

    #Tree fruits ready in greenhouse
    treefruits_greenhouse = np.array([int(x.find('fruitsontree').text) for x in trees if x.find('greenhousetree').text == 'true']).sum()

    #Tree fruits ready on farm
    treefruits_farm = np.array([int(x.find('fruitsontree').text) for x in trees if x.find('greenhousetree').text == 'false']).sum()

    #Crops ready in greenhouse
    planted_greenhouse = np.array([int(x.find('minharvest').text) for x in crops if x.find('isgreenhousedirt').text == 'true']).sum()
    phasedays_greenhouse = np.array([int(x.text) for x in [y.find('phasedays').contents[:-1] for y in crops if y.find('isgreenhousedirt').text == 'true'][0]])
    totaldays_greenhouse = phasedays_greenhouse.sum()
    currentphase_greenhouse = [int(x.find('currentphase').text) for x in crops if x.find('isgreenhousedirt').text == 'true'][0]
    dayofcurrentphase_greenhouse = [int(x.find('dayofcurrentphase').text) for x in crops if x.find('isgreenhousedirt').text == 'true'][0]
    daysuntilready_greenhouse = phasedays_greenhouse.sum() - (phasedays_greenhouse[:currentphase_greenhouse].sum() + dayofcurrentphase_greenhouse)

    #Crops ready on farm
    planted_farm = np.array([int(x.find('minharvest').text) for x in crops if int(x.find('x').text) >= 45 and int(x.find('x').text) < 65 and int(x.find('y').text) >= 27 and int(x.find('y').text) < 41]).sum()
    phasedays_farm = np.array([int(x.text) for x in [y.find('phasedays').contents[:-1] for y in crops if int(y.find('x').text) >= 45 and int(y.find('x').text) < 65 and int(y.find('y').text) >= 27 and int(y.find('y').text) < 41][0]])
    totaldays_farm = phasedays_farm.sum()
    currentphase_farm = [int(x.find('currentphase').text) for x in crops if int(x.find('x').text) >= 45 and int(x.find('x').text) < 65 and int(x.find('y').text) >= 27 and int(x.find('y').text) < 41][0]
    dayofcurrentphase_farm = [int(x.find('dayofcurrentphase').text) for x in crops if int(x.find('x').text) >= 45 and int(x.find('x').text) < 65 and int(x.find('y').text) >= 27 and int(x.find('y').text) < 41][0]
    daysuntilready_farm = phasedays_farm.sum() - (phasedays_farm[:currentphase_farm].sum() + dayofcurrentphase_farm)

    #Progress for honey production in bee houses
    minutesuntilready_honey = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Bee House']))
    totalminutes_honey = 6100
    progress_honey = (totalminutes_honey - minutesuntilready_honey) / totalminutes_honey

    #Progress for maple syrup tapper
    minutesuntilready_maple = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Tapper' and x.find_all('name')[2].text == 'Maple Syrup']))
    totalminutes_maple = 9*24*60
    progress_maple = (totalminutes_maple - minutesuntilready_maple) / totalminutes_maple

    #Progress for oak resin tapper
    minutesuntilready_oak = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Tapper' and x.find_all('name')[2].text == 'Oak Resin']))
    totalminutes_oak = 7*24*60
    progress_oak = (totalminutes_oak - minutesuntilready_oak) / totalminutes_oak

    #Progress for pine tar tapper
    minutesuntilready_pine = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Tapper' and x.find_all('name')[2].text == 'Pine Tar']))
    totalminutes_pine = 5*24*60
    progress_pine = (totalminutes_pine - minutesuntilready_pine) / totalminutes_pine

    #Progress for preserves jars
    minutesuntilready_preserves = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Preserves Jar']))
    totalminutes_preserves = 6000
    progress_preserves = (totalminutes_preserves - minutesuntilready_preserves) / totalminutes_preserves

    #Progress for kegs
    minutesuntilready_keg = int(max([x.find_all('minutesuntilready')[-1].text for x in items if x.find('name').text == 'Keg']))
    totalminutes_keg = 10000
    progress_keg = (totalminutes_keg - minutesuntilready_keg) / totalminutes_keg

    #Progress for cellar
    quality_names = ['base', 'silver star', 'gold star', 'iridium star', 'iridium star']
    quality_number = [0, 0.25, 0.5, 0.75, 1]
    quality_code_cask = [int(x.find_all('quality')[-1].text) for x in items if x.find('name').text == 'Cask' and len(x.find_all('name')) == 4][0]
    quality_cask = quality_names[quality_code_cask]

    #Crops to turn into artisan goods
    ready_artisan = np.array([int(x.find('stack').text) for x in groups[25]]).sum()

    #Luck
    luck = round(float(soup.find('dailyluck').text), 2)

    #Get today's date
    today = int(soup.find('dayofmonthforsavegame').text)
    if today == 28:
        tomorrow = 1
    else:
        tomorrow = today + 1
    seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    season = int(soup.find('seasonforsavegame').text)

    #Clean weather types
    weather_types = {0: 'Tomorrow is sunny', 
                     1: 'Tomorrow is rainy', 
                     3: 'Lightning tomorrow', 
                     4: 'Festival tomorrow',
                     5: 'Tomorrow is snowy',
                     6: 'Tomorrow is windy', 
                     7: 'Tomorrow is windy'}

    weather_images = {0: 'StatusSun.png', 
                     1: 'StatusRain.png', 
                     3: 'StatusStorm.png', 
                     4: 'StatusFestival.png',
                     5: 'StatusSnow.png',
                     6: 'StatusWindSpring.png',
                     7: 'StatusWindFall.png'}

    #Weather for tomorrow on farm
    weather_farm = [int(x.find('weatherfortomorrow').text) for x in soup.find_all('item') if x.find('locationcontext') != None][0]
    if (weather_farm == 2) & (season == 0):
        weather_farm = 6
    elif (weather_farm == 2) & (season == 2):
        weather_farm = 7
    else:
        pass

    #Weather for tomorrow on island
    weather_island = [int(x.find('weatherfortomorrow').text) for x in soup.find_all('item') if x.find('locationcontext') != None][1]
    if (weather_island == 2) & (season == 0):
        weather_island = 6
    elif (weather_island == 2) & (season == 2):
        weather_island = 7
    else:
        pass

    #Staircases on hand
    on_hand_staircase = np.array([int(x.find('stack').text) for x in groups[10] if x.find('name').text == 'Staircase']).sum() + np.array([int(x.find('stack').text) for x in groups[24] if x.find('name').text == 'Jade']).sum()
    
    #Plot metrics
    #Diamond replication progress
    if minutesuntilready_diamond == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_diamond / 1440)

    fig_1_1 = create_fig(progress_diamond, '.0%', 'Diamond replication progress', title_2, 'Crystalarium.png', 0.5)

    #Diamonds on hand
    fig_1_2 = create_fig(on_hand_diamond, '.0f', 'Diamonds on hand', '', 'Diamond.png', 0.3)

    #Years Penny will still love me
    fig_1_3 = create_fig(years_diamond, '.0f', 'Number of years Penny', 'will still love me', 'Penny.png', 0.45)

    #Triple shot espressos
    fig_1_4 = create_fig(total_espressos, '.2s', 'Triple shot espressos that', 'can be brewed', 'Triple_Shot_Espresso.png', 0.3)

    #Hay level in silos
    if hay_silos == 0:
        title_2 = '(Empty and needs top up!)'
    else:
        title_2 = '(Top up by {:,.0f})'.format(capacity_silos - hay_silos)

    fig_2_1 = create_fig(hay_level_silos, '.0%', 'Hay level in silos', title_2, '100px-Silo.png', 0.5)

    #Hay level in barns and coops
    if hay_feeders == 0:
        title_2 = '(Empty and needs top up!)'
    else:
        title_2 = ''

    fig_2_2 = create_fig(hay_level_feeders, '.0%', 'Hay level in hoppers', title_2, 'Hay_Hopper_Full.png', 0.4)

    #Hay on hand
    fig_2_3 = create_fig(on_hand_hay, '.2s', 'Hay on hand', '(Buy more in {:.0f} days)'.format(on_hand_hay / 108), 'Hay.png', 0.3)

    #Animal products ready
    fig_2_4 = create_fig(animal_products_ready, '.0f', 'Animal products ready', 'in barns & coops', 'Wool.png', 0.3)

    #Tree fruits ready in greenhouse
    fig_3_1 = create_fig(treefruits_farm, '.0f', 'Tree fruits ready for harvest', 'Outdoors', 'Cherry_Stage_5_Fruit.png', 0.5)

    #Tree fruits ready on farm
    fig_3_2 = create_fig(treefruits_greenhouse, '.0f', 'Tree fruits ready for harvest', 'Greenhouse', '170px-Greenhouse.png', 0.5)

    #Crops ready in greenhouse
    if daysuntilready_greenhouse <= 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({} days to go)'.format(daysuntilready_greenhouse)

    fig_3_3 = create_fig(planted_greenhouse, '.0f', 'Crops planted in greenhouse', title_2, '170px-Greenhouse.png', 0.5)     

    #Crops ready on farm
    if daysuntilready_farm <= 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({} days to go)'.format(daysuntilready_farm)

    fig_3_4 = create_fig(planted_farm, '.0f', 'Crops planted outdoors', title_2, 'Ancient_Fruit_Stage_6.png', 0.4)

    #Progress for honey production in bee houses
    if minutesuntilready_honey == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_honey / 1440)

    fig_3_5 = create_fig(progress_honey, '.0%', 'Honey production progress', title_2, 'Honey.png', 0.3)

    #Progress for maple syrup tapper
    if minutesuntilready_maple == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_maple / 1440)

    fig_3_6 = create_fig(progress_maple, '.0%', 'Maple production progress', title_2, 'Maple_Syrup.png', 0.3)

    #Progress for oak resin tapper
    if minutesuntilready_oak == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_oak / 1440)

    fig_3_7 = create_fig(progress_oak, '.0%', 'Oak resin production progress', title_2, 'Oak_Resin.png', 0.3)

    #Progress for pine tar tapper
    if minutesuntilready_pine == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_pine / 1440)

    fig_3_8 = create_fig(progress_pine, '.0%', 'Pine tar production progress', title_2, 'Pine_Tar.png', 0.3)

    #Progress for preserves jars
    if minutesuntilready_preserves == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_preserves / 1440)

    fig_4_1 = create_fig(progress_preserves, '.0%', 'Preserves production progress', title_2, 'Jelly.png', 0.3)

    #Progress for kegs
    if minutesuntilready_keg == 0:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '({:.1f} days to go)'.format(minutesuntilready_keg / 1440)

    fig_4_2 = create_fig(progress_keg, '.0%', 'Wine production progress', title_2, 'Wine.png', 0.3)

    #Progress for cellar
    if quality_number[quality_code_cask] == 1:
        title_2 = '(Ready to harvest!)'
    else:
        title_2 = '(Currently {} quality)'.format(quality_cask)

    fig_4_3 = create_fig(quality_number[quality_code_cask], '.0%', 'Wine aging progress', title_2, 'Cask.png', 0.45)

    #Crops to turn into artisan goods
    fig_4_4 = create_fig(ready_artisan, '.0f', 'Crops ready for artisan goods', '(Enough for {:.1f} batches)'.format(ready_artisan / 345), 'Ancient_Fruit.png', 0.3)

    #Tomorrow's weather on farm
    fig_5_1 = create_fig(tomorrow, '.0f', seasons[season], '{} on farm'.format(weather_types[weather_farm]), weather_images[weather_farm], 0.5)

    #Tomorrow's weather on island
    fig_5_2 = create_fig(tomorrow, '.0f', seasons[season], '{} on island'.format(weather_types[weather_island]), weather_images[weather_island], 0.5)

    #Luck
    if luck == 0:
        title_2 = 'The spirits feel neutral today'
    elif luck > 0:
        title_2 = 'Luck is on your side today!'
    elif luck < 0:
        title_2 = 'Luck is not on your side today'

    fig_5_3 = create_fig(luck, '+', 'Luck today', title_2, 'Fortune_Teller.png', 0.5)

    #Staircases on hand
    fig_5_4 = create_fig(on_hand_staircase, '.2s', 'Jade and staircases that', 'can be crafted', 'Staircase.png', 0.3)
    
    return fig_1_1, fig_1_2, fig_1_3, fig_1_4, fig_2_1, fig_2_2, fig_2_3, fig_2_4, fig_3_1, fig_3_2, fig_3_3, fig_3_4, fig_3_5, fig_3_6, fig_3_7, fig_3_8, fig_4_1, fig_4_2, fig_4_3, fig_4_4, fig_5_1, fig_5_2, fig_5_3, fig_5_4

#Run data for first time
fig_1_1, fig_1_2, fig_1_3, fig_1_4, fig_2_1, fig_2_2, fig_2_3, fig_2_4, fig_3_1, fig_3_2, fig_3_3, fig_3_4, fig_3_5, fig_3_6, fig_3_7, fig_3_8, fig_4_1, fig_4_2, fig_4_3, fig_4_4, fig_5_1, fig_5_2, fig_5_3, fig_5_4 = refresh_data()

#Run dashboard
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4('The most important things')),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_1_1', figure=fig_1_1)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_1_2', figure=fig_1_2)]), width='auto')]),
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_1_3', figure=fig_1_3)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_1_4', figure=fig_1_4)]), width='auto')])])],
                color='rgba(191, 48, 86, 0.7)', inverse=True
            ), width='auto', style={'padding': 10, 'margin-left': '10%'}),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4('What shall we harvest today?')),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_1', figure=fig_3_1)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_2', figure=fig_3_2)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_4', figure=fig_3_4)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_3', figure=fig_3_3)]), width='auto')]),
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_5', figure=fig_3_5)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_6', figure=fig_3_6)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_7', figure=fig_3_7)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_3_8', figure=fig_3_8)]), width='auto')])])],
                color='rgba(173, 217, 13, 0.7)', inverse=True
            ), width='auto', style={'padding': 10}),
        dbc.Col(dbc.Card([
            dbc.CardImg(src="/assets/Avatar.png", top=True),
            dbc.CardFooter(dbc.Button('Refresh', id='refresh_button', color='success', className='me-1'))],
                color='success'), width='auto', style={'padding': 10})
            ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4('Keep the animals happy')),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_2_1', figure=fig_2_1)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_2_2', figure=fig_2_2)]), width='auto')]),
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_2_3', figure=fig_2_3)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_2_4', figure=fig_2_4)]), width='auto')])])],
                color='rgba(33, 175, 191, 0.7)', inverse=True
            ), width='auto', style={'padding': 10, 'margin-left': '10%'}),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4('Artisan goods progress')),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_4_1', figure=fig_4_1)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_4_2', figure=fig_4_2)]), width='auto')]),
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_4_3', figure=fig_4_3)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_4_4', figure=fig_4_4)]), width='auto')])])],
                color='rgba(242, 165, 22, 0.7)', inverse=True
            ), width='auto', style={'padding': 10}),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Let's go adventuring!")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_5_3', figure=fig_5_3)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_5_4', figure=fig_5_4)]), width='auto')]),
                    dbc.Row([
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_5_1', figure=fig_5_1)]), width='auto'),
                        dbc.Col(html.Div(children=[dcc.Graph(id='fig_5_2', figure=fig_5_2)]), width='auto')])])],
                color='rgba(7, 133, 242, 0.7)', inverse=True
            ), width='auto', style={'padding': 10})
            ])
        ],
        fluid=True,
        style={'padding': 40, 'background-image': 'url("/assets/Stardew_Background.jpeg")', 'background-size': 'cover'})

@app.callback(
    Output('fig_1_1', 'figure'),
    Output('fig_1_2', 'figure'),
    Output('fig_1_3', 'figure'),
    Output('fig_1_4', 'figure'),
    Output('fig_2_1', 'figure'),
    Output('fig_2_2', 'figure'),
    Output('fig_2_3', 'figure'),
    Output('fig_2_4', 'figure'),
    Output('fig_3_1', 'figure'),
    Output('fig_3_2', 'figure'),
    Output('fig_3_3', 'figure'),
    Output('fig_3_4', 'figure'),
    Output('fig_3_5', 'figure'),
    Output('fig_3_6', 'figure'),
    Output('fig_3_7', 'figure'),
    Output('fig_3_8', 'figure'),
    Output('fig_4_1', 'figure'),
    Output('fig_4_2', 'figure'),
    Output('fig_4_3', 'figure'),
    Output('fig_4_4', 'figure'),
    Output('fig_5_1', 'figure'),
    Output('fig_5_2', 'figure'),
    Output('fig_5_3', 'figure'),
    Output('fig_5_4', 'figure'),
    Input('refresh_button', 'n_clicks')
)

def refresh_figures(button_click):
    fig_1_1, fig_1_2, fig_1_3, fig_1_4, fig_2_1, fig_2_2, fig_2_3, fig_2_4, fig_3_1, fig_3_2, fig_3_3, fig_3_4, fig_3_5, fig_3_6, fig_3_7, fig_3_8, fig_4_1, fig_4_2, fig_4_3, fig_4_4, fig_5_1, fig_5_2, fig_5_3, fig_5_4 = refresh_data()
    return fig_1_1, fig_1_2, fig_1_3, fig_1_4, fig_2_1, fig_2_2, fig_2_3, fig_2_4, fig_3_1, fig_3_2, fig_3_3, fig_3_4, fig_3_5, fig_3_6, fig_3_7, fig_3_8, fig_4_1, fig_4_2, fig_4_3, fig_4_4, fig_5_1, fig_5_2, fig_5_3, fig_5_4

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)


# In[ ]:




