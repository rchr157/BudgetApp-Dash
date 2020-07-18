import dash
import dash_core_components as dcc
import dash_html_components as html

from app import server
from app import app
from layouts import layout_load_tab, layout_plot_tab
import callbacks

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'fontSize': '24px'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#82c91e',
    'color': 'white',
    'padding': '6px',
    'fontSize': '24px'
}

app.index_string = ''' 
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(
        id="app-container",
        children=[
            # Banner
            html.Div(
                id="banner",
                className="banner",
                children=[html.Img(src=app.get_asset_url("budget.png"))]
            ),
            html.Div(id="hidden-container",
                     children=[
                        # hidden Div to trigger javascript file for graph resizing
                        html.Div(id="output-clientside"),
                        # hidden Div for storing data needed for graphs
                        html.Div(id='dataframe-json-dump', style={'display': 'none'}),
                        html.Div(id='lists-json-dump', style={'display': 'none'}),
                         ]),
            html.Div(id="tab-container",
                     children=[
                        dcc.Tabs(id='tabs-styled-with-inline', value='Load', children=[
                            dcc.Tab(label='Load', value='Load', style=tab_style, selected_style=tab_selected_style),
                            dcc.Tab(label='Plots', value='Plot', style=tab_style, selected_style=tab_selected_style)
                        ], style=tabs_styles),
                        html.Div(id='tabs-content-inline')
                         ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
