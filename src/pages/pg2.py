import pandas as pd
from dash import Dash, html, Output, Input, dcc, callback
import dash_bootstrap_components as dbc
import dash
import plotly.express as px
# import plotly.graph_objects as go

dash.register_page(__name__,path='/moviesoriginal', name='Movies Original')

data_canada = px.data.gapminder().query("country == 'Canada'")
dfTips = px.data.tips()

df = pd.read_csv('netflix.csv') ##### delete
df2 = pd.read_csv('netflix_tfidf.csv')

# ******************************* Data Cleaning *******************************
dfTop = df2.copy()

def top_ten_filt(*args, num=None):
    dfFilt = dfTop[dfTop['type'] == 'Movie']
    dfFilt = dfFilt[~dfFilt['country'].str.contains(',')].reset_index()
    dfFilt = dfFilt[[*args]].value_counts().sort_values(ascending=False)[:num].to_frame('count').reset_index()
    return dfFilt



def cleaning(data):
    new = data[data['date_added'].notnull()].copy()
    new['country'] = new['country'].fillna('other')
    new['date_added'] = new['date_added'].str.replace(',','').astype('datetime64')
    new['year added'] = new['date_added'].dt.year
    new['netflix org'] = new['year added'] - new['release_year']
    new['netflix org'] = new['netflix org'].apply(lambda x: 'Originals' if x == 0 else 'License')
    new['year added'] = new['year added'].astype('str')
    new['netflix org'] = new['netflix org'].astype('str')
    # Select data from 2013 - 2021
    new = new[new['year added'] > '2012']
    return new


def df_line_graph(data):
    data = data[data['type'] == 'Movie']
    dfMovie = data[['netflix org', 'year added']].groupby('year added').value_counts().to_frame('count').reset_index()
    year = dfMovie[dfMovie['netflix org']=='License']['year added'].to_list()
    countLicense = dfMovie[dfMovie['netflix org']=='License']['count'].to_list()
    countOrg = dfMovie[dfMovie['netflix org']=='Originals']['count'].to_list()

    movie = {
        'Year': year,
        'License': countLicense,
        'Originals': countOrg
    }

    dfMovie = pd.DataFrame.from_dict(movie)
    return dfMovie


def filt(movie_type, content_type):
    mask = (dfTfidf['country'] == 'other')
    dfMovieAll = dfTfidf[~mask]

    dfFilt = dfMovieAll.copy()
    dfFilt = dfFilt[dfFilt['type'] == content_type]
    mask = (dfFilt['netflix org'] == movie_type)
    dfFilt = dfFilt[mask]
    ctyOrg = dfFilt[['country']].groupby('country').value_counts().sort_values(ascending=False)[:10].reset_index()['country'].to_list()
    dfMovieFilt = dfFilt[dfFilt['country'].isin(ctyOrg)]
    return dfMovieFilt

def type_movie(type):
    df1 = dfTfidf[dfTfidf['type'] == type]
    cty = df1[['country']].groupby('country').value_counts().sort_values(ascending=False)[:10].reset_index()['country'].to_list()
    df1 = df1[df1['country'].isin(cty)]
    return df1

dfAll = cleaning(df)
dfTfidf = cleaning(df2)
dfMovie = df_line_graph(dfTfidf)
dfMovieOrg = filt('Originals', 'Movie')
dfMovieLic = filt('License', 'Movie')

allTop = top_ten_filt('country', num=10)['country'].to_list()
dfFiltEachTop = top_ten_filt('country', 'netflix org')
topLicense = dfFiltEachTop[dfFiltEachTop['netflix org'] == 'License'][0:10]['country'].to_list()
topOrg = dfFiltEachTop[dfFiltEachTop['netflix org'] == 'Originals'][0:10]['country'].to_list()


dfMovieOrg = dfMovieOrg[['country', 'year added']].groupby('country').value_counts().to_frame('count').reset_index()
dfMovieOrg = dfMovieOrg.sort_values(by='year added')

dfMovieLic = dfMovieLic[['country', 'year added']].groupby('country').value_counts().to_frame('count').reset_index()
dfMovieLic = dfMovieLic.sort_values(by='year added')

#************************* app layout *************************
fig2 = px.sunburst(dfTips, path=['day', 'time', 'sex'], values='total_bill').update_layout(margin=dict(l=1, r=10, t=5, b=15))

firstCard = dbc.Card([
    dbc.CardBody([
        dcc.Checklist(
                options=[{'label': x, 'value': x} for x in dfAll['netflix org'].unique()],
                # options=['License', 'Originals'],
                value=[],
                labelStyle={'display':'block'}, # making checkbox vertical
                id='checklist' 
                )
            ])
        ])

secondCard = dbc.Card([
    dbc.CardBody([
        dcc.Input(value='', placeholder='Search', id='input'),
            dcc.Checklist(
                options=[],
                value=[],
                labelStyle={'display':'block'},# making checkbox vertical
                id='country-checklist' 
                )
            ])
        ])


lineCard = dbc.Card([
    dbc.CardBody([
        dcc.Graph(figure={}, id='line-fig',style={'height':'18rem'})
        ])
    ],style={'height':'20rem'})


sunburstCard = dbc.Card([
    dbc.CardBody([
        dcc.Graph(figure={}, id='sun-fig',style={'height':'18rem'})
        ])
    ],style={'height':'18rem', 'border':'none'})
    

layout = html.Div([
    dbc.Row([
        dbc.Col([
            firstCard,
            html.Br(),
            secondCard
            ], width=3),
        dbc.Col([
            lineCard,
            sunburstCard
            ])
        ])
    ])


@callback(
    Output('country-checklist', 'options'),
    Output('line-fig', 'figure'),
    Output('sun-fig', 'figure'),
    Input('checklist', 'value'), # input value is list
    Input('country-checklist', 'value') 
    )
def update_graphs(select_checklist, select_country):
    # 1 logic
    # User check both or check nothing, and no check on country
    # Return Line charts and Sunburst charts of overview (2 lines for license and org)
    if (len(select_checklist) == 0 or len(select_checklist) == 2) and (len(select_country) == 0):
        fig = px.line(dfMovie, x='Year', y=['License', 'Originals']).update_layout(
                                                                                margin=dict(l=1, r=10, t=5, b=15),
                                                                                legend_title_text=None, 
                                                                                yaxis_title="No of Contents")

        # fig2 = px.sunburst(dfTips, path=['day', 'time', 'sex'], values='total_bill')
        df = top_ten_filt('country', 'netflix org', 'type_tfidf')
        df = df[df['country'].isin(allTop)]
        fig2 = px.sunburst(df, path=['country', 'netflix org', 'type_tfidf'], values='count')
        fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

        return allTop, fig, fig2

    # 2 Logic
    # User check only 1, and no country
    # Return Line chart and Sunburst chart filtered on license or org (only 1 line)
    if len(select_checklist) == 1 and len(select_country) == 0:
        dfM = dfTfidf[dfTfidf['type']=='Movie']
        dfGroup = dfM[['country', 'type_tfidf', 'netflix org']].groupby('type_tfidf').value_counts().to_frame('count').reset_index()

        dfLine = dfAll[dfAll['netflix org'].isin(select_checklist)]
        dfLine = dfLine[dfLine['type'] == 'Movie']
        dfLine = dfLine[['netflix org', 'year added']].groupby('year added').value_counts().to_frame('count').reset_index()
        year = dfLine['year added'].unique()
        count = dfLine[dfLine['netflix org']==select_checklist[0]]['count'].to_list()
        movie = {
            'Year': year,
            'Num_Content': count
            # 'Originals': countOrg
        }
        dfFilt = pd.DataFrame.from_dict(movie)

        if select_checklist[0] == 'Originals':
            dfOrg = dfGroup[dfGroup['netflix org'] =='Originals']
            fig = px.line(dfFilt, x='Year', y='Num_Content').update_layout(
                                                                margin=dict(l=1, r=10, t=5, b=15),
                                                                legend_title_text=None, 
                                                                yaxis_title="No of Contents",
                                                                xaxis_title=None)
            fig.update_traces(line_color='#ee0000')

            df = top_ten_filt('country', 'netflix org', 'type_tfidf')
            df = df[df['country'].isin(topOrg)]
            fig2 = px.sunburst(df, path=['country', 'netflix org', 'type_tfidf'], values='count')
            fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

            # fig2 = px.sunburst(dfTips, path=['day', 'time', 'sex'], values='total_bill')
            # fig2 = px.sunburst(dfOrg, path=['netflix org', 'country', 'type_tfidf'], values='count')
            # fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))
            return topOrg, fig, fig2
        else:
            dfLicense = dfGroup[dfGroup['netflix org'] =='License']
            fig = px.line(dfFilt, x='Year', y='Num_Content').update_layout(
                                                                margin=dict(l=1, r=10, t=5, b=15),
                                                                legend_title_text=None, 
                                                                yaxis_title="No of Contents",
                                                                xaxis_title=None)

            # fig2 = px.sunburst(dfLicense, path=['netflix org', 'country', 'type_tfidf'], values='count')
            fig2 = px.sunburst(dfTips, path=['day', 'time', 'sex'], values='total_bill')
            fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))
            return topLicense, fig, fig2
        # return dfMovieOrg['country'].unique().tolist(),fig

    # 3 Logic
    # User check only 1, and check 1 or more on country
    # Return Bar Chart (stack bar chart if selecte more than 1 country)
    if len(select_checklist) == 1 and len(select_country) >= 1:
        country_list = select_country
        dfM = dfTfidf[dfTfidf['type']=='Movie']
        dfM = dfTfidf[dfTfidf['country'].isin(country_list)]
        dfGroup = dfM[['country', 'type_tfidf', 'netflix org']].groupby('type_tfidf').value_counts().to_frame('count').reset_index()

        if select_checklist[0] == 'Originals':
            dfOrg = dfGroup[dfGroup['netflix org'] =='Originals'] 
            dfMovieOrg2 = dfMovieOrg[dfMovieOrg['country'].isin(country_list)]            
            fig = px.histogram(
                dfMovieOrg2,
                x=dfMovieOrg2['year added'].to_list(),
                y=dfMovieOrg2['count'].to_list(),
                color='country',
                barmode='group'
                )
            fig.update_layout(margin=dict(l=1, r=10, t=5, b=15),
                                legend_title_text=None, 
                                yaxis_title="No of Contents",
                                xaxis_title=None)

            fig2 = px.sunburst(dfOrg, path=['netflix org', 'country', 'type_tfidf'], values='count')
            fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

            return dfMovieOrg['country'].unique().tolist(), fig, fig2
        else:
            # **************** dcc.card on country is change on top 10
            dfMovieLic2 = dfMovieLic[dfMovieLic['country'].isin(country_list)]
            dfLicense = dfGroup[dfGroup['netflix org'] =='License']
            fig = px.histogram(
                dfMovieLic2,
                x=dfMovieLic2['year added'].to_list(),
                y=dfMovieLic2['count'].to_list(),
                color='country',
                barmode='group'
                )
            fig.update_layout(margin=dict(l=1, r=10, t=5, b=15),
                                legend_title_text=None, 
                                yaxis_title="No of Contents",
                                xaxis_title=None)

            fig2 = px.sunburst(dfLicense, path=['netflix org', 'country', 'type_tfidf'], values='count')
            # fig2 = px.sunburst(dfTips, path=['day', 'time', 'sex'], values='total_bill')
            fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

            return dfMovieLic['country'].unique().tolist(), fig, fig2

    # 4 Logic
    # if both are checked and country check only 1
    # Return Bar Chart
    if len(select_checklist) == 2 and len(select_country) == 1:
        dff = dfTfidf[dfTfidf['type'] == 'Movie']
        dff = dff[['country', 'year added', 'netflix org']].groupby('netflix org').value_counts().to_frame('count').reset_index().sort_values(by='year added')  
        dff['year added'] = dff['year added'].astype('str')
        dff = dff[dff['country'] == select_country[0]]

        dfM = dfTfidf[dfTfidf['type']=='Movie']
        dfM = dfTfidf[dfTfidf['country'].isin(select_country)]
        dfGroup = dfM[['country', 'type_tfidf', 'netflix org']].groupby('type_tfidf').value_counts().to_frame('count').reset_index()
        
        fig = px.histogram(dff, x='year added', y='count', color='netflix org', barmode='group')
        fig.update_layout(margin=dict(l=1, r=10, t=5, b=15),
                                legend_title_text=None, 
                                yaxis_title="No of Contents",
                                xaxis_title=None)
        fig2 = px.sunburst(dfGroup, path=['netflix org', 'type_tfidf'], values='count')
        fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

        # *************** 1. select_country must not change / 2. change color on bar
        return dfMovieOrg['country'].unique().tolist(), fig, fig2

    # 5 Logic
    # if both are checked or no check and country check more than 1
    # Return Bar Chart
    if (len(select_checklist) == 2 or len(select_checklist) == 0) and (len(select_country) >=1):
        country_list = select_country
        dff = dfTfidf[dfTfidf['country'].isin(country_list)]
        dff = dff[dff['type'] == 'Movie']
        dff = dff[['country', 'year added', 'netflix org']].groupby('netflix org').value_counts().to_frame('count').reset_index().sort_values(by='year added')  
        dff['year added'] = dff['year added'].astype('str')

        dfM = dfTfidf[dfTfidf['type']=='Movie']
        dfM = dfTfidf[dfTfidf['country'].isin(country_list)]
        dfGroup = dfM[['country', 'type_tfidf', 'netflix org']].groupby('type_tfidf').value_counts().to_frame('count').reset_index()
        

        fig = px.histogram(dff, x='year added', y='count', color='country', barmode='group')
        fig.update_layout(margin=dict(l=1, r=10, t=5, b=15),
                                legend_title_text=None, 
                                yaxis_title="No of Contents",
                                xaxis_title=None)

        fig2 = px.sunburst(dfGroup, path=['netflix org', 'country','type_tfidf'], values='count')
        fig2.update_layout(margin=dict(l=1, r=10, t=5, b=15))

        return dfMovieOrg['country'].unique().tolist(), fig, fig2


