import json
import pickle

import requests
from dash import Dash
from dash import Input, Output
from dash import dcc
from dash import html

data = pickle.load(open('resources/movies', 'rb'))
vector = pickle.load(open('resources/model', 'rb'))
app = Dash()

app.layout = html.Div(
    id='main', children=[
        html.Div(children=[
            html.H1('Movie Recommender System!!!', style={'text-align': 'center', 'background-color': 'Tomato'}),
            dcc.Dropdown(id='movie-list', options=list(data['original_title']),
                         style={'margin': 'auto', 'padding': '10px'}),
            html.Br(),
            html.Br(),
            html.Div(id='selected-movie', children=[], style={'margin': 'auto', 'height': 500,
                                                              'padding': '20px'}),
            html.Br()
        ]),
        html.Div(id='recommended-movies', children=[], style={'margin': 'auto', 'padding': '20px'}),
        html.Br()
    ]
)


@app.callback(
    Output(component_id='recommended-movies', component_property='children'),
    Input(component_id='movie-list', component_property='value'),
    prevent_initial_call=True
)
def add_recommended_movies(*args):
    movie = args[0]
    if movie:
        idx = data.loc[data['original_title'] == movie]['id']
        id_list = get_recommendation(index=idx.index.values[0])
        sn_list = list(data.iloc[id_list, :]['id'])
        return get_recommended_movies(sn_list)


@app.callback(
    Output(component_id='selected-movie', component_property='children'),
    Input(component_id='movie-list', component_property='value'),
    prevent_initial_call=True
)
def update_component(*args):
    movie = args[0]
    if movie:
        idx = list(data.loc[data['original_title'] == movie]['id'])
        movie_data = get_movie_json(idx[0])
        return get_movies_banner(movie_data)


def get_movies_banner(movie_data):
    poster_path = 'https://image.tmdb.org/t/p/w500/{}'.format(movie_data.get('poster_path'))
    genres = ' | '.join(list(map(lambda x: x.get('name'), movie_data.get('genres'))))
    rating = round(movie_data.get('vote_average'), 1)
    banner = [
        html.Div(id='banner', children=[
            html.Img(id='poster', src=poster_path,
                     width=350, height=400, style={'margin': 'auto', 'padding': '5px',
                                                   'border': '5px solid', 'border-radius': '10%',
                                                   'float': 'left'}),
            html.Div(id='movie-info', style={'margin': 'auto', 'width': 700, 'padding': '10px', 'float': 'right'},
                     children=[
                         html.H2(movie_data.get('title')), html.Hr(),
                         html.I(children=[
                             html.P(movie_data.get('overview'), style={'margin': 'auto', 'padding': '5px'})]),
                         html.P('Genres : {}'.format(genres)),
                         html.P('Rating : {}'.format(rating))
                     ])
        ])
    ]
    return banner


def get_recommended_movies(sn_list):
    children = [html.H2('Recommended Movies'), html.Hr()]
    for sn in sn_list:
        movie_data = get_movie_json(sn)
        poster_path = 'https://image.tmdb.org/t/p/w500/{}'.format(movie_data.get('poster_path'))
        children.append(
            html.Img(id='poster', src=poster_path,
                     width=230, height=270, style={'margin': 'auto', 'padding': '5px',
                                                   'border': '5px', 'border-radius': '10%'}))
    return children


def get_movie_json(idx):
    info = dict(
        api_key='bb9ff19337cecdbb8b3c8b5bf95348da'
    )
    res = requests.get(url='http://api.themoviedb.org/3/movie/{}'.format(idx), params=info, verify=False)
    return json.loads(res.text)


def get_recommendation(index):
    co_sim = list(enumerate(vector[index]))
    co_sim.sort(key=lambda x: x[1])
    co_sim.reverse()
    return [val[0] for val in co_sim[1:6]]


if '__main__' == __name__:
    app.run_server(debug=True)
