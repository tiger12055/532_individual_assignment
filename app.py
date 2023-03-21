import dash
from dash import dcc
#import dash_core_components as dcc
from dash import html
#import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output
from dash import dash_table

# Load data
df = pd.read_csv('data/raw/HousingData.csv')
df = df.dropna(subset=['bedrooms', 'bathrooms', 'sqft_living', 'price', 'lat', 'long'])
df = df[(df['sqft_living'] >= 200) & (df['sqft_living'] <= 3290) & (df['price'] >= 200) & (df['price'] <= 500000)& (df['bathrooms'] <= 5)]

table_columns = [
    {"name": "Price", "id": "price"},
    {"name": "Bedrooms", "id": "bedrooms"},
    {"name": "Bathrooms", "id": "bathrooms"},
    {"name": "Sqft Living", "id": "sqft_living"},
    {"name": "Condition", "id": "condition"},
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2("Seattle Housing Listings"),
                width={"size": 12},
                className="mb-4 mt-4"
            ),
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Price Range (in USD)", className="mb-2"),
                        dcc.RangeSlider(
                            id="price",
                            min=df['price'].min(),
                            max=df['price'].max(),
                            step=25,
                            value=[df['price'].min(), df['price'].max()],
                            marks={int(i): f"${i:,.0f}" for i in range(int(df['price'].min()), int(df['price'].max() + 1), 85000)},
                            allowCross=False,
                            className="mb-4"
                        ),
                        html.Label("Number of Bedrooms", className="mb-2"),
                        dcc.RangeSlider(
                            id="bedrooms",
                            min=df['bedrooms'].min(),
                            max=df['bedrooms'].max(),
                            step=1,
                            value=[df['bedrooms'].min(), df['bedrooms'].max()],
                            marks={i: f"{i}" for i in range(int(df['bedrooms'].min()), int(df['bedrooms'].max()) + 1)},
                            allowCross=False,
                            className="mb-4"
                        ),
                        html.Label("Number of Bathrooms", className="mb-2"),
                        dcc.RangeSlider(
                            id="bathrooms",
                            min=df['bathrooms'].min(),
                            max=df['bathrooms'].max(),
                            step=0.5,
                            value=[df['bathrooms'].min(), df['bathrooms'].max()],
                            marks={i: f"{i}" for i in range(int(df['bathrooms'].min()), int(df['bathrooms'].max()) + 1)},
                            allowCross=False,
                            className="mb-4"
                        ),
                        html.Label("Square Feet", className="mb-2"),
                        dcc.RangeSlider(
                            id="sqft_living",
                            min=df['sqft_living'].min(),
                            max=df['sqft_living'].max(),
                            step=500,
                            value=[df['sqft_living'].min(), df['sqft_living'].max()],
                            marks={int(i): f"{i:,.0f}" for i in range(int(df['sqft_living'].min()), int(df['sqft_living'].max() + 1), 300)},
                            allowCross=False,
                            className="mb-4"
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="map", className="mb-4"),
                        dcc.Graph(id="price_histogram", className="mb-4"),
                    ],
                    width=9,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Top 10 Cheapest Houses", className="mb-4"),
                        dash_table.DataTable(
                            id='table',
                            columns=table_columns,
                            style_cell={'textAlign': 'left'},
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            page_current=0,
                            page_size=10,
                            page_action='custom',
                            sort_action='custom',
                            sort_mode='multi',
                            sort_by=[]
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
    ],
    fluid=True,
)

@app.callback(
    [Output("map", "figure"),
     Output("price_histogram", "figure"),
     Output("table", "data")],
    [Input("price", "value"),
     Input("bedrooms", "value"),
     Input("bathrooms", "value"),
     Input("sqft_living", "value")]
)
def update_figures(price, bedrooms, bathrooms, sqft_living):
    # Filter data based on user inputs
    filtered_df = df[
        (df["price"] >= price[0]) & (df["price"] <= price[1]) &
        (df["bedrooms"] >= bedrooms[0]) & (df["bedrooms"] <= bedrooms[1]) &
        (df["bathrooms"] >= bathrooms[0]) & (df["bathrooms"] <= bathrooms[1]) &
        (df["sqft_living"] >= sqft_living[0]) & (df["sqft_living"] <= sqft_living[1])
    ]

    # Create map figure
    map_figure = {
        "data": [
            {
                "type": "scattermapbox",
                "lat": filtered_df["lat"],
                "lon": filtered_df["long"],
                "mode": "markers",
                "marker": {"size": 6, "color": "#3399FF"},
                "text": filtered_df.apply(lambda row: f"Price: ${row['price']:,.0f}  Sqft Living: {row['sqft_living']:,}", axis=1),
                "hoverinfo": "text"
            }
        ],
        "layout": {
            "autosize": True,
            "mapbox": {
                "style": "open-street-map",
                "center": {"lat": filtered_df["lat"].mean(), "lon": filtered_df["long"].mean()},
                "zoom": 9
            },
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0}
        }
    }

    # Create price histogram figure
    histogram_figure = {
        "data": [
            {
                "type": "histogram",
                "x": filtered_df["price"],
                "nbinsx": int((price[1] - price[0]) / 5000),
                "marker": {"color": "#3399FF"}
            }
        ],
        "layout": {
            "title": "Price Distribution",
            "xaxis": {"title": "Price", "tickformat": "$,.0f"},
            "yaxis": {"title": "Count"},
            "bargap": 0.1
        }
    }

    table_data = filtered_df[["price", "bedrooms", "bathrooms", "sqft_living", "condition"]].copy()


    table_data = table_data.nsmallest(10, "price")
    table_data["price"] = table_data["price"].apply(lambda x: f"${x:,.0f}")
    table_data["sqft_living"] = table_data["sqft_living"].apply(lambda x: f"{x:,.0f}")

    table_data_list = table_data.to_dict("records")

    return map_figure, histogram_figure, table_data_list

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)