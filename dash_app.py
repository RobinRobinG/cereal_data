from flask import Flask
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
cereal_df = pd.read_csv("data/cereal.csv")


server = Flask(__name__)
app = dash.Dash(__name__, server = server)
app.config.requests_pathname_prefix = '' 



app.layout = html.Div(children=[
                html.H2(    children='User Input'),
                dcc.Input(  id='input', 
                            value='', 
                            name= 'cereal',
                            placeholder='Enter a cereal name',
                            type='text',
                            className='input'),

                dcc.Dropdown(
                            id='y-axis-input',
                            options=[{'label': i, 'value': i} for i in cereal_df[:3]],
                            value='',
                            className='input'),
                html.Div(   id='output-graph', 
                            style={'margin': 30}),

                html.Div(   id='output-graph2', 
                            style={'margin': 30}),

],style={'text-align':'center'})


@app.callback(
    Output(component_id='output-graph2', component_property='children'),
    [Input(component_id='input', component_property='value'),
    Input(component_id='y-axis-input', component_property='value'),]
)

def update_graph(user_input):

    df_filtered = cereal_df.query('name.str.contains("'+user_input+'")')


    return dcc.Graph(
        id='allcereals',
        figure={
            'data': [
                {'x': cereal_df.name, 'y': df_filtered.calories/df_filtered.cups, 'type':'bar', 'name':'Calories per serving'},
                #{'x': df_filtered.name, 'y': df_filtered.fiber, 'type':'bar', 'name':'Fiber per serving', },
                #{'x': df_filtered.name, 'y': df_filtered.sugars, 'type':'bar', 'name':'Sugar per serving', },

            ],
            'layout': {
                'title':    'Nutritionals per Cup',
                'height': 680,
                'legend': {
                            'orientation': 'h',
                            "x": 2,
                            'xanchor': 'center'
                            },
                'margin': {
                            'l': 100,
                            'r': 80,
                            't': 100,
                            'b': 200,
                            },
                #'annotations': annotation,
                'hovermode': 'closest',
                'yaxis': {
                            'title': 'Calories',
                            'showgrid': True,
                            },
                'xaxis': {
                            'showgrid': True,
                            'title': 'Cereal Brand'
                            },
            }
        }
    )

def update_graph(user_input, y_axis_input):

    df_filtered = cereal_df.query('name.str.contains("'+user_input+'")')


    return dcc.Graph(

        id='allcereals_rating',
        figure={
            'data': [
                {'x': cereal_df.name, 'y': df_filtered.calories/df_filtered.cups, 'type':'bar', 'name':'Calories per serving'},
                #{'x': df_filtered.name, 'y': df_filtered.fiber, 'type':'bar', 'name':'Fiber per serving', },
                #{'x': df_filtered.name, 'y': df_filtered.sugars, 'type':'bar', 'name':'Sugar per serving', },

            ],
            'layout': {
                'title':    'Nutritionals per Cup',
                'height': 680,
                'legend': {
                            'orientation': 'h',
                            "x": 2,
                            'xanchor': 'center'
                            },
                'margin': {
                            'l': 100,
                            'r': 80,
                            't': 100,
                            'b': 200,
                            },
                #'annotations': annotation,
                'hovermode': 'closest',
                'yaxis': {
                            'title': 'Calories',
                            'showgrid': True,
                            },
                'xaxis': {
                            'showgrid': True,
                            'title': 'Cereal Brand'
                            },
            }
        }
    )



@server.route('/')
def myDashApp():
    return app

if __name__ == '__main__':
    #print(cereal_df.name[])
    app.run_server(debug=True, port=8050)
