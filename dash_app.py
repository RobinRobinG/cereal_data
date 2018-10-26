from text_reco_flask.text_recognition import *
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import re
cereal_df = pd.read_csv("data/cereal.csv")

#server = Flask(__name__)
app = dash.Dash(__name__)
app.config.requests_pathname_prefix = '' 
app.config.suppress_callback_exceptions = True


url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


layout_index = html.Div([
    dcc.Link('Navigate to "/page-1"', href='/page-1'),
    html.Br(),
    dcc.Link('Navigate to "/page-2"', href='/page-2'),
])


layout_page_1 = html.Div(children=[
                html.H1(    children='Know Your Cereal'),
                dcc.Dropdown(
                            id='input',
                            options=[{'label': i, 'value': i} for i in cereal_df.name],
                            placeholder='Enter a cereal name',
                            value=''),
                html.Div(   id='output-graph'),
                html.Br(),
                dcc.Link('Navigate to "/"', href='/'),
                html.Br(),
                dcc.Link('Navigate to "/page-2"', href='/page-2'),

],className="main-content")

words = []
layout_page_2 = html.Div(   children=[
                html.H1(    children='Know Your Cereal'),
               dcc.Upload(
                            id='upload-image',
                            children=html.Div(['Drag and Drop or ',html.A('Select Files')
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
                html.Div(   id='output-image-upload'),
                html.Div(   id='output-graph2'),
                html.Br(),
                dcc.Link('Navigate to "/"', href='/'),
                html.Br(),
                dcc.Link('Navigate to "/page-1"', href='/page-1'),
])


def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        layout_index,
        layout_page_1,
        layout_page_2,
    ])


app.layout = serve_layout



# Index callbacks
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/page-1":
        return layout_page_1
    elif pathname == "/page-2":
        return layout_page_2
    else:
        return layout_index



# Page 1 callbacks
@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')])
def update_graph(user_input):
    if(len(user_input) >0):
        df_filtered = cereal_df.query('name.str.contains("'+user_input+'")')
        return dcc.Graph(

            id='text',
            figure={
                'data': [
                    {'x': df_filtered.name, 'y': df_filtered.calories, 'type':'bar', 'name':'Calories per serving'},
                    {'x': df_filtered.name, 'y': df_filtered.fiber, 'type':'bar', 'name':'Fiber per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.sugars, 'type':'bar', 'name':'Sugar per serving', },
                ],
                'layout': {
                    'title': 'Nutritionals per 100g',
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)'
                }
            }
        )

# Page 2 callbacks
def parse_contents(contents, filename, date):
    words = LetterFinding("text_reco_flask/frozen_east_text_detection.pb",contents[23:], 0.05)
    #only consider de first word that appears.
    index = 0;
    max_index=0;
    max_results =0;
    while(index < len(words)):
        cleanString = re.sub('\W+','', words[index] )
        print(cleanString)
        df_filtered = cereal_df.query('name.str.contains("'+cleanString+'",False)')
        results = len(df_filtered)
        print(results)
        if(len(cleanString) > 2 and results > max_results):
            max_results = results
            max_index = index
        index+=1
    print(words[max_index])
    print(max_results)
    return html.Div([
        html.H5(filename),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents,id='uploaded_image'),
        html.Hr(),
        html.Div(children=[
                dcc.Input(  id='input_2', 
                            value=words[max_index], 
                            type='text',
                            style={'display': 'none'})]
                 ),
        html.Pre(words[max_index], style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(
    Output(component_id='output-graph2', component_property='children'),
    [Input(component_id='input_2', component_property='value')])
def update_graph(user_input):
    if(len(user_input) >0):
        cleanString = re.sub('\W+','', user_input)
        df_filtered = cereal_df.query('name.str.contains("'+cleanString+'",False)')
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

# @server.route('/')
# def myDashApp():
#     return app


if __name__ == '__main__':
    app.run_server(debug=True)
