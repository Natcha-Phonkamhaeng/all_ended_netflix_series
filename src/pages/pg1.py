import pandas as pd
from dash import Dash, html, Output, Input, dcc, callback
import dash_bootstrap_components as dbc
import dash
import plotly.express as px
import plotly.graph_objects as go

dash.register_page(__name__, path='/', name='Overview', description='Overview of Netflix Movie/Series 2013-2021')

df = pd.read_csv('netflix.csv')

# ******************************* Data Cleaning *******************************
df = df[df['date_added'].notnull()]

df['date_added'] = df['date_added'].str.replace(',','').astype('datetime64')
df['year added'] = df['date_added'].dt.year
df['netflix org'] = df['year added'] - df['release_year']
df['netflix org'] = df['netflix org'].apply(lambda x: 'yes' if x == 0 else 'no')
df['year added'] = df['year added'].astype('str')
# Select data from 2013 - 2021
df = df[df['year added'] > '2012']

# Pie chart
dfShow = df.copy()
dfPie = dfShow[['type']].value_counts().to_frame('count').reset_index()
figPie = px.pie(dfPie, values='count', names='type', title='Proportion for Movies VS Series 2013-2021')

# Bar Chart
dfBar = dfShow[['type', 'year added']].groupby('year added').value_counts().to_frame('count').reset_index()
fig = go.Figure()
fig.add_trace(go.Bar(x=dfBar[dfBar['type']=='TV Show']['year added'].to_list(),
                y=dfBar[dfBar['type']=='TV Show']['count'].to_list(),
                name='TV Show',
                marker_color='#ee0000'
                ))
fig.add_trace(go.Bar(x=dfBar[dfBar['type']=='Movie']['year added'].to_list(),
                y=dfBar[dfBar['type']=='Movie']['count'].to_list(),
                name='Movie',
                marker_color='rgb(26, 118, 255)'
                ))

fig.update_layout(
    title='Monthly Contents between Movies and Series',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Number of contents',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)
#************************* app layout *************************

layout = html.Div([
    dbc.Row([
      dbc.Col([
          html.H2('Netflix Original Movies-Series Dashboard')
          ],
          style={'textAlign':'center', 'color':'grey'})
      ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=figPie, id='pie-fig')
            ])
        ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=fig, id='bar-fig')
            ])
        ])
    ])











