from text_reco_flask.text_recognition import *
from flask import Flask,session
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
cereal_df = pd.read_csv("data/cereal.csv")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(__name__, server = server,external_stylesheets=external_stylesheets)
app.config.requests_pathname_prefix = '' 
app.config['suppress_callback_exceptions'] = True
words = []

app.layout = html.Div(children=[
                html.H2(    children='User Input',
                            ),

                dcc.Input(  id='input', 
                            value='', 
                            placeholder='Enter a cereal name',
                            type='text',
                            style={'width': 300}),
               dcc.Upload(
                    id='upload-image',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                html.Div(id='output-image-upload'),
                html.Div(   id='output-graph', 
                            style={'margin': 30}),

                html.Div(   id='output-graph2', 
                            style={'margin': 30}),
],style={'text-align':'center'})

def parse_contents(contents, filename, date):
    words = LetterFinding("text_reco_flask/frozen_east_text_detection.pb",contents[23:], 0.05)
    #only consider de first word that appears.
    index = 0;
    while(len(words[index]) < 3):
        index+=1

    return html.Div([
        html.H5(filename),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents,id='uploaded_image'),
        html.Hr(),
        html.Div(children=[
                dcc.Input(  id='input_2', 
                            value=words[index], 
                            type='text',
                            style={'display': 'none'})]
                 ),
        html.Pre(words[index], style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])
#Draw graph if the text is updated.
@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')])
def update_graph(user_input):
    if(len(user_input) >0):
        df_filtered = cereal_df.query('name.str.contains("'+user_input+'")')
        return dcc.Graph(

            id='allcereals_rating',
            figure={
                'data': [
                    {'x': df_filtered.name, 'y': df_filtered.calories, 'type':'bar', 'name':'Calories per serving'},
                    {'x': df_filtered.name, 'y': df_filtered.fiber, 'type':'bar', 'name':'Fiber per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.sugars, 'type':'bar', 'name':'Sugar per serving', },

                ],
                'layout': {
                    'title': 'Nutritionals per 100g'
                }
            }
        )
#Draw graph if an image is uploaded
@app.callback(
    Output(component_id='output-graph2', component_property='children'),
    [Input(component_id='input_2', component_property='value')])
def update_graph(user_input):
    if(len(user_input) >0):
        df_filtered = cereal_df.query('name.str.contains("'+user_input+'")')
        return dcc.Graph(

            id='allcereals_rating',
            figure={
                'data': [
                    {'x': df_filtered.name, 'y': df_filtered.calories, 'type':'bar', 'name':'Calories per serving'},
                    {'x': df_filtered.name, 'y': df_filtered.fiber, 'type':'bar', 'name':'Fiber per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.sugars, 'type':'bar', 'name':'Sugar per serving', },

                ],
                'layout': {
                    'title': 'Nutritionals per 100g'
                }
            }
        )

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children




@server.route('/')
def myDashApp():

    return app

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
