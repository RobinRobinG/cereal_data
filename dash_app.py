from text_reco_flask.text_recognition import *
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import re
cereal_df = pd.read_csv("data/cereal.csv")



server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.requests_pathname_prefix = '' 
app.config.suppress_callback_exceptions = True


url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


layout_index = html.Div([
    dcc.Link(   'Cereal Calorie Compare', href='/page-1', className='button'),
    dcc.Link(   'Nutrition Facts', href='/page-2', className='button'),
])


layout_page_1 = html.Div(   children=[
                html.Div(   children=[  html.H1(    children='Cereal Calorie Compare'),
                                        dcc.Link(   children='Nutrition Facts', 
                                                    href='/page-2',
                                                    className='button')],className="heading"),
                dcc.Dropdown(
                            id='input',
                            options=[{'label': i, 'value': i} for i in cereal_df.name],
                            multi=True,
                            placeholder='Enter a cereal name',
                            value=['All-Bran','Cheerios']),
                html.Div(   id='output-graph'),
                #dcc.Link(   'HOME', 
                            #href='/',
                            #className='button home'),
],className="main-content")

words = []
layout_page_2 = html.Div(   children=[
                html.Div(   children=[  html.H1(    children='Nutrition Facts'),
                                        dcc.Link(   children=   'Calorie Compare', 
                                                    href='/page-1',
                                                    className='button')],className="heading"),
               dcc.Upload(
                            id='upload-image',
                            children=   html.Div(['Drag and Drop or  ',
                                        html.A( 'Select Files')
                             ]),
                            className = "upload_area",
                            # Allow multiple files to be uploaded
                            multiple=True
                            ),
                html.Div(   id='output-image-upload',
                            className='preview_image'),
                html.Div(   id='output-graph2'),
                html.Br(),
                #dcc.Link(   'HOME', 
                            #href='/',
                            #className='button home'),
],className="main-content")


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
    if not user_input:
        html.H3(    "Select a cereal brand.")
    else:
        traces = []
        for i, user_input in enumerate(user_input):
            df_filtered = cereal_df[cereal_df['name'] == user_input]
            traces.append({'x':df_filtered.name, 'y':(df_filtered.calories/df_filtered.cups), 'name': user_input, 'type':'bar'})       
        return dcc.Graph(
            id='user_input',
            figure={
                'data':traces,
                'layout': {
                    'title': 'Calories per cup',
                    'paper_bgcolor': 'rgb(255,255,255,0.3)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'legend': dict(orientation='h'),
                    'bordercolor': '#333',
                        }
                    },
            config={
                'displayModeBar': False
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
        html.Div([

                
                html.Div(   children=[
                  dcc.Input(  id='input_2',
                            value=words[max_index],
                            type='text',
                            style={'display': 'none'})
                  ]),
                html.Div([  html.Img(   src=contents,
                                        id='uploaded_image', 
                                        style= {'width': '300px'})], className ='uploaded_image'),
                html.P(words[max_index], 
                    style={ 'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'},
                    className='text_out', 
                )
        ],className ='box_and_text')
    ],className ='uploaded_content')


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
                    #{'x': df_filtered.name, 'y': df_filtered.calories/df_filtered.cups, 'type':'bar', 'name':'Calories per serving'},
                    {'x': df_filtered.name, 'y': df_filtered.fiber/df_filtered.cups, 'type':'bar', 'name':'Fiber per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.sugars/df_filtered.cups, 'type':'bar', 'name':'Sugar per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.protein/df_filtered.cups, 'type':'bar', 'name':'Protein per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.fat/df_filtered.cups, 'type':'bar', 'name':'Fat per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.sodium/df_filtered.cups/1000, 'type':'bar', 'name':'Sodium per serving', },
                    {'x': df_filtered.name, 'y': df_filtered.carbo/df_filtered.cups, 'type':'bar', 'name':'Carbo per serving', },

                ],
                'layout': {
                    'title': 'Grams in a cup',
                    'paper_bgcolor': 'rgb(255,255,255,0.3)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'legend': dict(orientation='h'),
                    'bordercolor': '#333',
                }
            },
            config={
                'displayModeBar': False
            },
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
