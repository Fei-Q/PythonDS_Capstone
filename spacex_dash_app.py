# Import required libraries
import pandas as pd
import dash
from dash import dcc, html  # using the new unified dash imports
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    html.Br(),

    # TASK 1: Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie Chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: RangeSlider for selecting payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 100: '100'},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter Chart for payload vs. launch outcome
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: Callback for updating the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, use the entire dataset where launches were successful (class == 1)
        all_sites_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            all_sites_df, 
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # For a specific site, filter the dataframe and create a pie chart of success vs. failure
        selected_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = selected_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        fig = px.pie(
            outcome_counts,
            values='count',
            names='class',
            title=f"Launch Outcomes for Site {entered_site}"
        )
    return fig

# TASK 4: Callback for updating the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(entered_site, payload_range):
    # Unpack the payload slider values
    low, high = payload_range
    # Filter the DataFrame by the payload range
    df_payload = spacex_df[(spacex_df["Payload Mass (kg)"] >= low) &
                           (spacex_df["Payload Mass (kg)"] <= high)]
    
    if entered_site == 'ALL':
        # Scatter plot for all sites with payload and outcome, colored by Booster Version Category
        fig = px.scatter(
            df_payload,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Payload vs. Outcome for All Sites",
            hover_data=['Launch Site']
        )
    else:
        # Further filter the DataFrame to the selected launch site
        df_site = df_payload[df_payload["Launch Site"] == entered_site]
        fig = px.scatter(
            df_site,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Payload vs. Outcome for {entered_site}",
            hover_data=['Launch Site']
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
