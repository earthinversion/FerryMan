import os
import dash
from dash import dcc
from dash import html
import pandas as pd
import wikipedia


species_data = pd.read_csv('speices_parameters.csv')
species_nm=species_data['scientific_name'].values
species_name=[]
for specnm in species_nm:
    species_name.append(specnm.replace("_"," ").title())
# print(species_name)

dv_0=(species_data['dv_0'].values)*(9/5)+32
dv_1=(species_data['dv_1'].values)*(9/5)+32
dv_2=(species_data['dv_2'].values)*(9/5)+32
dv_3=(species_data['dv_3'].values)*(9/5)+32

sm_0=species_data['sm_0'].values
sm_1=species_data['sm_1'].values
sm_2=species_data['sm_2'].values
sm_3=species_data['sm_3'].values

baseaddress='https://raw.githubusercontent.com/IEScoders/ObservingEarthWithData/master/Habitat_LOGO/'

desert_b=baseaddress+'desert-b.jpg'
desert_d=baseaddress+'desert-d.jpg'
farm_b=baseaddress+'farm-b.jpg'
farm_d=baseaddress+'farm-d.jpg'
forest_b=baseaddress+'forest-b.jpg'
forest_d=baseaddress+'forest-d.jpg'
mount_b=baseaddress+'mon-b.jpg'
mount_d=baseaddress+'mon-d.jpg'
urban_b=baseaddress+'urban-b.jpg'
urban_d=baseaddress+'urban-d.jpg'
water_b=baseaddress+'water-b.jpg'
water_d=baseaddress+'water-d.jpg'
snow_b=baseaddress+'cool-b.jpg'
snow_d=baseaddress+'cool-d.jpg'

months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
with open('nasalogo.txt', 'r') as myfile: #read the long web address of nasa space apps logo
    nasasrc=myfile.read().replace('\n', '')

temperature_data={}
temperature_data[species_name[0]]={'x': ["Temp","Temp","Temp","Temp","Temp","Temp","Temp"],'y': [dv_0[0], dv_1[0], dv_1[0], (dv_1[0]+dv_2[0])/2,dv_2[0],dv_2[0],dv_3[0]]}

for i in range(1,len(species_name)):
    temperature_data.update({species_name[i]:{'x': ["Temp","Temp","Temp","Temp","Temp","Temp","Temp"],'y': [dv_0[i], dv_1[i], dv_1[i], (dv_1[i]+dv_2[i])/2,dv_2[i],dv_2[i],dv_3[i]]}})


rainfall_data={}
rainfall_data[species_name[0]]={'x': ["Rain","Rain","Rain","Rain","Rain","Rain","Rain"],'y': [sm_0[0], sm_1[0],sm_2[0],sm_3[0]]}

for i in range(1,len(species_name)):
    rainfall_data.update({species_name[i]:{'x': ["Rain","Rain","Rain","Rain","Rain","Rain","Rain"],'y': [sm_0[i], sm_1[i],sm_2[i],sm_3[i]]}})

ei_index_des='''
__0__: _Unsurvivable_    __1-10__: _Hard to tolerate_    __11-20__: _Tolerable_    __21-60__: _Preferable_    __More than 60__: _Very Comfortable_
'''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title='FerryMan' #add the app name in the tab
server = app.server

app.layout = html.Div(
html.Div([
    html.Div([
            html.Img(
                src="https://raw.githubusercontent.com/IEScoders/ObservingEarthWithData/master/Logo/header3.png", #logo for the webpage
                className='nine columns',
                style={
                    'maxHeight': '15vh',
                    'maxWidth': '100vh',
                    'float': 'right',
                    'position': 'relative',
                    'margin-top': 10,
                    'margin-left': 10
                },
            ),
            html.Img(
                src="https://raw.githubusercontent.com/IEScoders/ObservingEarthWithData/master/Logo/logo.jpg", #logo for the webpage
                className='two columns',
                style={
                    'maxHeight': '10vh',
                    'maxWidth': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 20,
                    'margin-right': 0
                },
            )
        ], className = "row"),
        html.Div([
            html.H3('Motivation', #some information about the project
                    className = 'nine columns')
        ],className = 'row'),
        html.Div([
            html.P('The biological kingdom always amazed us with its diversity and surprise. In a context of fast-changing world of climate and environment, we need to predict and prevent the invasions of some threatening species and find new home for endangered ones. Motivated by this, we used global land surface temperature and precipitation from NASA satellite in combination of different species habitat database to plot the region of comfort for different species. Our ultimate goal is to help those species can go on a ferry and reach their dream homes.', #some information about the project
                    className = 'twelve columns')
        ],className = 'row'),
        html.Div([
            html.H3('Details', #some information about the project
                    className = 'nine columns')
        ],className = 'row'),
        html.Div([
            html.P('We hope Ferryman would be a favorite website for all animal lovers and people curious about the biological world. Our website introduces different species with their information and images, showing their current distribution and present their "comfort" temperature and rainfall environment. For a more in-depth analysis, we applied the method of Sutherst and Maywald (1985) to estimate the Ecological Index (EI) which reflects how well the species could live in different locations.',className = 'twelve columns')
        ],className = 'row'),
    html.Div([
    html.H4('Select the species to ferry', style={'textAlign': 'center','color': 'blue'}, #request to select
    className = "four columns")], className="row"),
    html.Div([
    dcc.Dropdown( #dropdown menu to select the species
        id='dropdown',
        options=[{'label': i, 'value': i} for i in list(species_name)],
        value=species_name[2],className = 'four columns'
    ),html.H4(id='questionspecies',children='Do you know about this species?', style={'textAlign': 'center','color': 'green','marginLeft': 140}, #request to select
    className = "six columns")], className="row"),
    html.Div([html.Img(
                id='species_image',
                className='six columns',
                style={
                    'height': '60vh',
                    'width': '60vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 5,
                    'margin-right': 10
                },
            ),html.P(id='species_info',className='six columns', style={'textAlign': 'left','marginLeft': 50})], className="row"),
    html.Div([html.P(id='my-div',className='six columns'),html.Div(
                    [
                        html.P('Source: ', style = {'display': 'inline'}),
                        html.A(id='wikilink')
                    ], className = "six columns",
                       style = {'fontSize': 18, 'padding-top': 0}
                )],className="row"),
    html.Div([dcc.Markdown('---')], className="row"),
    html.Div([
    html.H4('The Ecoclimatic Index (EI) plot', style={'color': 'green'}, #request to select
    className = "eight columns")], className="row"),
    html.Div([
        dcc.RadioItems( 
        id='radioei_plot',
        options=[{'label': i, 'value': i} for i in list(months)],
        value=months[0],className = 'twelve columns',labelStyle={'display': 'inline-block','marginRight': 40})
    ], className="row"),
    html.Div([
        html.Img(
                id='ei_plot_image',
                className='six columns',
                style={
                    'height': '100%',
                    'width': '100%',
                    'float': 'center',
                    'position': 'relative',
                    'margin-top': 10,
                    'margin-right': 0
                },
            ),
    ],className='row'),
    html.Div([
    dcc.Markdown(children=ei_index_des, className="twelve columns")], className="row"),
    html.Div([dcc.Markdown('---')], className="row"),
    html.Div([html.H4(children='''
    Climatic condition for survival
    ''',className = 'six columns',style={'textAlign': 'center'}),html.H4('Preferred Habitat',className = 'six columns', style={'textAlign': 'center'})], className="row"), #parameters range
    html.Div([dcc.Graph(
        id='example-graph',className = 'eight columns',  style={"height" : "40vh", "width" : "65vh"}
    ),html.Div([html.Img(
                id='hab_desert',
                className='two columns',
                style={
                    'height': '10vh',
                    'width': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 80,
                    'margin-left': 170
                },
            ),
            html.Img(
                id='hab_water',
                className='two columns',
                style={
                    'height': '10vh',
                    'width': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 80,
                    'margin-left': 5
                },
            ),
            html.Img(
                id='hab_farm',
                className='two columns',
                style={
                    'height': '10vh',
                    'width': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 80,
                    'margin-left': 5
                },
            ),
            html.Img(
                id='hab_urban',
                className='two columns',
                style={
                    'height': '10vh',
                    'width': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 80,
                    'margin-left': 5
                },
            ),
            html.Img(
                id='hab_forest',
                className='two columns',
                style={
                    'height': '10vh',
                    'width': '10vh',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 80,
                    'margin-left': 5
                },
            )])], className="row"),
            html.Div([dcc.Markdown('---')], className="row"),
            html.Div([
    dcc.Dropdown( #dropdown menu to select the species
        id='dropdowntemp',
        options=[{'label': i, 'value': i} for i in list(months)],
        value=months[0],className = 'six columns',style={'textAlign': 'center','marginLeft': 150}
    )], className="row"),
    html.Div([html.Img(
                id='species_temp',
                className='six columns',
                style={
                    'height': '100%',
                    'width': '100%',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 20,
                    'margin-left': 0
                },
            ),html.Img(
                id='species_prep',
                className='six columns',
                style={
                    'height': '100%',
                    'width': '100%',
                    'float': 'left',
                    'position': 'relative',
                    'margin-top': 20,
                    'margin-left': 0
                },
            )], className="row"),
            html.Div([dcc.Markdown('---')], className="row"),
            html.Div([
                html.H4(children='Expert on the species to contact', style={'color': 'green'}, #request to select
    className = "six columns")], className="row"),
            html.Div([
                dcc.Markdown(id='expert', #request to select
    className = "six columns")
            ], className="row"
        ),
            html.Div([dcc.Markdown('---')], className="row")
], className='ten columns offset-by-one')
)


# @app.callback(
#     dash.dependencies.Output('ei_plot_image', 'src'),
#     [dash.dependencies.Input('dropdown', 'value')],
#     [dash.dependencies.State('buttoneijan', 'n_clicks')])
# def update_species_ei(n_clicks,value):
#     src=species_data['ei_plot_jan'][species_name.index(value)]
#     return src


@app.callback(
    dash.dependencies.Output('species_prep', 'src'),
    [dash.dependencies.Input('dropdown', 'value'),dash.dependencies.Input('dropdowntemp', 'value')]
    )
def update_image_src(selector,value):
    if value == months[0]:
        src=species_data['mi_plot_jan'][species_name.index(selector)]
    elif value == months[1]:
        src=species_data['mi_plot_feb'][species_name.index(selector)]
    elif value == months[2]:
        src=species_data['mi_plot_mar'][species_name.index(selector)]
    elif value == months[3]:
        src=species_data['mi_plot_apr'][species_name.index(selector)]
    elif value == months[4]:
        src=species_data['mi_plot_may'][species_name.index(selector)]
    elif value == months[5]:
        src=species_data['mi_plot_jun'][species_name.index(selector)]
    elif value == months[6]:
        src=species_data['mi_plot_jul'][species_name.index(selector)]
    elif value == months[7]:
        src=species_data['mi_plot_aug'][species_name.index(selector)]
    elif value == months[8]:
        src=species_data['mi_plot_sep'][species_name.index(selector)]
    elif value == months[9]:
        src=species_data['mi_plot_oct'][species_name.index(selector)]
    elif value == months[10]:
        src=species_data['mi_plot_nov'][species_name.index(selector)]
    elif value == months[11]:
        src=species_data['mi_plot_dec'][species_name.index(selector)]
    else:
        src=species_data['mi_plot_jan'][species_name.index(selector)]
    # src='https://raw.githubusercontent.com/IEScoders/ObservingEarthWithData/master/Analysis/solenopsis_invicta_12_TI.png'
    return src



@app.callback(
    dash.dependencies.Output('species_temp', 'src'),
    [dash.dependencies.Input('dropdown', 'value'),dash.dependencies.Input('dropdowntemp', 'value')]
    )
def update_image_src(selector,value):
    if value == months[0]:
        src=species_data['ti_plot_jan'][species_name.index(selector)]
    elif value == months[1]:
        src=species_data['ti_plot_feb'][species_name.index(selector)]
    elif value == months[2]:
        src=species_data['ti_plot_mar'][species_name.index(selector)]
    elif value == months[3]:
        src=species_data['ti_plot_apr'][species_name.index(selector)]
    elif value == months[4]:
        src=species_data['ti_plot_may'][species_name.index(selector)]
    elif value == months[5]:
        src=species_data['ti_plot_jun'][species_name.index(selector)]
    elif value == months[6]:
        src=species_data['ti_plot_jul'][species_name.index(selector)]
    elif value == months[7]:
        src=species_data['ti_plot_aug'][species_name.index(selector)]
    elif value == months[8]:
        src=species_data['ti_plot_sep'][species_name.index(selector)]
    elif value == months[9]:
        src=species_data['ti_plot_oct'][species_name.index(selector)]
    elif value == months[10]:
        src=species_data['ti_plot_nov'][species_name.index(selector)]
    elif value == months[11]:
        src=species_data['ti_plot_dec'][species_name.index(selector)]
    else:
        src=species_data['ti_plot_jan'][species_name.index(selector)]
    return src

@app.callback(
    dash.dependencies.Output('ei_plot_image', 'src'),
    [dash.dependencies.Input('dropdown', 'value'),dash.dependencies.Input('radioei_plot', 'value')]
    )
def update_image_src(selector,value):
    if value == months[0]:
        src=species_data['ei_plot_jan'][species_name.index(selector)]
    elif value == months[1]:
        src=species_data['ei_plot_feb'][species_name.index(selector)]
    elif value == months[2]:
        src=species_data['ei_plot_mar'][species_name.index(selector)]
    elif value == months[3]:
        src=species_data['ei_plot_apr'][species_name.index(selector)]
    elif value == months[4]:
        src=species_data['ei_plot_may'][species_name.index(selector)]
    elif value == months[5]:
        src=species_data['ei_plot_jun'][species_name.index(selector)]
    elif value == months[6]:
        src=species_data['ei_plot_jul'][species_name.index(selector)]
    elif value == months[7]:
        src=species_data['ei_plot_aug'][species_name.index(selector)]
    elif value == months[8]:
        src=species_data['ei_plot_sep'][species_name.index(selector)]
    elif value == months[9]:
        src=species_data['ei_plot_oct'][species_name.index(selector)]
    elif value == months[10]:
        src=species_data['ei_plot_nov'][species_name.index(selector)]
    elif value == months[11]:
        src=species_data['ei_plot_dec'][species_name.index(selector)]
    else:
        src=species_data['ei_plot_jan'][species_name.index(selector)]
    return src


@app.callback(
    dash.dependencies.Output('wikilink', 'href'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_info(selector):
    webinfo = wikipedia.page(selector)
    return "{}".format(webinfo.url)

@app.callback(
    dash.dependencies.Output('wikilink', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_info(selector):
    webinfo = wikipedia.page(selector)
    return "{}".format(webinfo.title)

@app.callback(
    dash.dependencies.Output('expert', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_info(selector):
    desc='''
    Expert Name: {}
    Contact: {}
    Reference: {}
    '''.format(species_data['expert'][species_name.index(selector)],species_data['expart_contact'][species_name.index(selector)],species_data['reference'][species_name.index(selector)])
    return desc

@app.callback(
    dash.dependencies.Output(component_id='my-div', component_property='children'),
    [dash.dependencies.Input('dropdown', 'value')]
)
def update_output_div(input_value):
    source_image=species_data['pic_sources'][species_name.index(input_value)]
    return 'Source: {}'.format(source_image)

@app.callback(
    dash.dependencies.Output(component_id='questionspecies', component_property='children'),
    [dash.dependencies.Input('dropdown', 'value')]
)
def update_output_div(selector):
    return 'Do you know about {} or {}?'.format(selector,species_data['nick_name'][species_name.index(selector)].replace("_"," ").title())

@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_image_src(selector):
    data=[ #data for the plot
                {'x':rainfall_data[selector]['x'],'y':rainfall_data[selector]['y'],'type':'box','name':'Monthly Precipitation (mm)','boxmedian': False},
                {'x':temperature_data[selector]['x'],'y':temperature_data[selector]['y'],'type':'box','name':'Mean monthly Temperature (deg F)','boxmedian': False},
            ]
    print (selector)
    figure = {
        'data': data,
        'layout': {
            'title':'Survival Parameters',
            'xaxis' : dict(
                titlefont=dict(
                family='Helvetica, monospace',
                size=20,
                color='#7f7f7f'
            )),
            'yaxis' : dict(
                title='Values',
                titlefont=dict(
                family='Helvetica, monospace',
                size=20,
                color='#7f7f7f'
            ))
        }
    }
    return figure


@app.callback(
    dash.dependencies.Output('species_info', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_info(selector):
    desc=wikipedia.summary(selector)
    webinfo = wikipedia.page(selector)
    return desc


@app.callback(
    dash.dependencies.Output('species_image', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_image(selector):
    src=species_data['pic_link'][species_name.index(selector)]
    return src



## Habitat logo callbacks
@app.callback(
    dash.dependencies.Output('hab_desert', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_hab(selector):
    if species_data['desert'][species_name.index(selector)] == 1:
        src=desert_b
    else:
        src=desert_d
    return src

@app.callback(
    dash.dependencies.Output('hab_water', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_hab(selector):
    if species_data['freshwater'][species_name.index(selector)] == 1:
        src=water_b
    else:
        src=water_d
    return src

@app.callback(
    dash.dependencies.Output('hab_farm', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_hab(selector):
    if species_data['agricultural_land'][species_name.index(selector)] == 1:
        src=farm_b
    else:
        src=farm_d
    return src

@app.callback(
    dash.dependencies.Output('hab_urban', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_hab(selector):
    if species_data['urban'][species_name.index(selector)] == 1:
        src=urban_b
    else:
        src=urban_d
    return src

@app.callback(
    dash.dependencies.Output('hab_forest', 'src'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_species_hab(selector):
    if species_data['forests'][species_name.index(selector)] == 1:
        src=forest_b
    else:
        src=forest_d
    return src
if __name__ == '__main__':
    app.run_server(debug=True)
