import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

plot_options = [
    {"label": "Monthly Breakdown", "value": "Monthly Breakdown"},
    # {"label": "Relative To Income", "value": "Relative To Income"},
    {"label": "Net Income", "value": "Net Income"},
    {"label": "Individual Category", "value": "Individual Category"}
]


# Layout for first tab: Load Tab
layout_load_tab = html.Div([
    html.Div(id='upload-container', children=[
        dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.H1(
                        children='Welcome!',
                        style={
                            'textAlign': 'center',
                            'color': '#82c91e'
                        }
                    ),
                    'Drag and Drop', html.Br(),
                    'or',
                    html.Br(),
                    html.Button('Select File', id='upload-button')
                    ], style={'fontSize': '22px'}),
                # Allow multiple files to be uploaded
                multiple=True
            )]),
    html.H6(id="load-text",
            style={
                'textAlign': 'center',
                'color': '#82c91e'
            }
            )
    ])

######### PLOT TAB #########
layout_plot_tab = html.Div([
    html.Div(
        # Left column container
        id="left-column",
        children=[
            html.Button("Plot", n_clicks=0, id='plot-btn'),
            html.P("Select Type of Plot"),
            dcc.Dropdown(
                id="plot-options",
                options=plot_options,
                placeholder="Select Plot Option",
                searchable=False,
                clearable=False),
            html.Br(),
            html.P("Filter By Date"),
            dcc.DatePickerRange(
                id="date-picker",
                clearable=True,
                display_format='MM/DD/YYYY',
                start_date_placeholder_text="Start MM/DD/YYYY",
                end_date_placeholder_text="End MM/DD/YYYY",
                day_size=45,
                with_portal=True,
                number_of_months_shown=3
            ),
            html.Br(),
            html.P("Filter by Categories"),
            dcc.Dropdown(
                id="category-dropdown",
                placeholder="Select Category",
                searchable=False,
                multi=True
                ),
            html.P("Filter by Accounts"),
            dcc.Dropdown(
                id="account-checklist",
                placeholder="Select Accounts",
                searchable=False,
                multi=True
                ),
        ], className="pretty_container four columns"
    ),
    # Hidden Button to update account list
    html.Button("Update", n_clicks=0, id='update-btn', style={'display': 'none'}),
    # Right Column Container
    html.Div(
            id='right-column',
            children=[
                html.Div([
                    dcc.Graph(id='plot-figure', figure=go.Figure()),
                    ], className="pretty_graph_container seven columns one columns"
                )
            ])
])

