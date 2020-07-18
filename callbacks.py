from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
from dash.exceptions import PreventUpdate

import base64
import datetime
import io
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from app import app
from layouts import layout_load_tab, layout_plot_tab

# Default Mint Categories
cat_path = r"\assets\categories.csv"
categories_df = pd.read_csv(cat_path)
category_list = list(categories_df.columns)



###### Callback Functions ######
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


# Update tabs
@app.callback([Output('tabs-content-inline', 'children'),
               Output('update-btn', 'n_clicks')],
              [Input('tabs-styled-with-inline', 'value')])
def display_page(tab):
    if tab == "Load":
        layout = layout_load_tab
        click = 0
    elif tab == "Plot":
        layout = layout_plot_tab
        click = 1
    return layout, click


# Update Text to indicate which file has been loaded
@app.callback(Output('load-text', 'children'),
              [Input('upload-data', 'filename')])
def update_load_text(filename):
    txt_str = ""
    if filename:
        txt_str = "File Loaded: {}".format(filename[0])
    return html.Div([
        html.Hr(),
        html.H5(txt_str)
        ])


# Transfer Data from upload file
@app.callback([Output('dataframe-json-dump', 'children'),
               Output('lists-json-dump', 'children'),
               Output('tabs-styled-with-inline', 'value')],
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def transfer_df(contents, filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = categorize_df(df)
        cat_list = list(df["Category2"].unique())
        acc_list = list(df["Account Name"].unique())
        comb_list = json.dumps([cat_list, acc_list])
        json_df = df.to_json(orient='split')
        return json_df, comb_list, "Plot"


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


def categorize_df(df):
    # Add column Category2 - Parent Category
    df["Parent-Cat"] = ""
    df['Category2'] = ""

    # Remove Credit Card Payments and money transfers, due to redundancy
    drop_mask1 = (df["Category"] != "Credit Card Payment") & (df["Category"] != "Transfer")
    df = df.loc[drop_mask1].copy()

    # Organize into Parent Category
    for column in category_list:
        col = list(categories_df[column].dropna())
        df.loc[df["Category"].str.contains("|".join(col)), "Parent-Cat"] = column

    # Leftover categories get added to Uncategorized
    df.loc[df["Parent-Cat"] == "", "Parent-Cat"] = 'Uncategorized'

    most = df.groupby("Parent-Cat")["Parent-Cat"].count().sort_values(ascending=False)
    most_list = list(most[:7].index)

    # Organize into Top 8 Categories
    for column in most_list:
        col = list(categories_df[column].dropna())
        df.loc[df["Category"].str.contains("|".join(col)), "Category2"] = column

    df.loc[df["Category2"] == "", "Category2"] = 'Other'

    return df


# Plot Data
@app.callback(Output('plot-figure', 'figure'),
              [Input('plot-btn', 'n_clicks')],
              [State('dataframe-json-dump', 'children'), State('plot-options', 'value'),
               State('date-picker', 'start_date'), State('date-picker', 'end_date'),
               State('category-dropdown', 'value'), State('account-checklist', 'value')])
def update_figure(nclick, json_dump, plt_opt, start_date, end_date, cat_opt, acct_opt):
    if (json_dump is None) | (nclick == 0) | (plt_opt is None):
        raise PreventUpdate
    else:
        json_dump = json.loads(json_dump)
        mod_df = pd.DataFrame(json_dump['data'], columns=json_dump['columns'])

        # Convert Date to datetime and set as index
        mod_df["Date"] = pd.to_datetime(mod_df["Date"])
        mod_df = mod_df.set_index(mod_df["Date"])

        # Filter data frame
        mod_df = filter_date(mod_df, start_date, end_date, plt_opt)
        mod_df = filter_categories(mod_df, cat_opt)
        mod_df = filter_accounts(mod_df, acct_opt)

        # Get figure to display in layout
        fig = get_plot_data(mod_df, plt_opt, cat_opt)

        return fig


def filter_date(df, start_date, end_date, plt_opt):
    if (plt_opt == "Monthly Breakdown") & (start_date is None):
        start_date = (df.index.sort_values(ascending=False)[0] -
                      datetime.timedelta(days=30)).strftime("%m-%d-%Y")
    elif start_date is None:
        start_date = df.index.sort_values(ascending=True)[0].strftime("%m-%d-%Y")
    if end_date is None:
        end_date = df.index.sort_values(ascending=False)[0].strftime("%m-%d-%Y")

    df = df[(df.index >= start_date) & (df.index <= end_date)]
    return df


def filter_categories(df, cat_opt):
    if type(cat_opt) == str:
        df = df[df['Category2'] == cat_opt]
    else:
        df = df[df['Category2'].isin(cat_opt)]
    return df


def filter_accounts(df, acct_opt):
    if type(acct_opt) == str:
        df = df[df["Account Name"] == acct_opt]
    else:
        df = df[df["Account Name"].isin(acct_opt)]
    return df


def get_plot_data(df, plt_opt, cat_opt):
    data2plot = pd.DataFrame()
    # total_income = df.loc[df['Category2'] == "income", "Amount"].sum()  # Get total income
    temp2_df = df[(df['Category2'] != "Income") & (df['Transaction Type'] == "debit")]  # Only include expenses

    if (plt_opt == "Monthly Breakdown") | (plt_opt == "Relative To Income"):
        fig = make_subplots(rows=2, cols=2,
                            specs=[[{"type": "domain", "colspan": 2, "rowspan": 2}, None],
                                   [None, None]])
        # Data for Pie Chart
        data2plot = temp2_df.groupby("Category2")["Amount"].sum()
        # if plt_opt == "Relative To Income":
        #     data2plot = data2plot/total_income

        # Create Plot Title
        start_month = temp2_df.index.sort_values(ascending=True)[0].strftime("%B %d %Y")
        end_month = temp2_df.index.sort_values(ascending=False)[0].strftime("%B %d %Y")
        if start_month == end_month:
            title_text = "{} for {}".format(plt_opt, start_month)
        else:
            title_text = "{} for {}-{}".format(plt_opt, start_month, end_month)
        # Plot Data in graph
        fig.add_trace(go.Pie(labels=data2plot.index, values=data2plot), row=1, col=1)
        fig.update_traces(hovertemplate="Category: %{label} <br>Amount:%{value:$,.2f}",
                          textposition='inside', textinfo='percent+label')
        fig.update_layout(height=800, title=title_text, legend_title="Categories")

    elif plt_opt == "Net Income":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Income vs Expense", "Net Income"))
        # Data for Bar Graphs
        data2plot["monthly_income"] = df[df["Category2"] == "Income"].groupby(pd.Grouper(freq="M"))["Amount"].sum()
        data2plot["monthly_expense"] = df[(df["Category2"] != "Income") & (df['Transaction Type'] == "debit")].groupby(
            pd.Grouper(freq="M"))["Amount"].sum()
        data2plot["monthly_net"] = data2plot["monthly_income"] - data2plot["monthly_expense"]
        data2plot = data2plot.round(2)
        # Plot Income vs Expense on First Graph
        fig.add_trace(go.Bar(name='Income', x=data2plot.index, y=data2plot["monthly_income"],
                             text=data2plot["monthly_income"]), row=1, col=1)
        fig.add_trace(go.Bar(name='Expense', x=data2plot.index, y=data2plot["monthly_expense"],
                             text=data2plot["monthly_expense"]), row=1, col=1)
        # Plot Net Income on Second Graph
        fig.update_layout(barmode='group', yaxis_title="USD ($)")
        fig.add_trace(go.Bar(name='Net', x=data2plot.index, y=data2plot["monthly_net"],
                             text=data2plot["monthly_net"]), row=2, col=1)
        fig.update_layout(height=800, xaxis_tickangle=-45, xaxis_title="Date", yaxis_title="USD ($)")

    elif plt_opt == "Individual Category":
        fig = make_subplots(rows=2, cols=2,
                            specs=[[{"type": "xy", "colspan": 2}, None],
                                   [{"type": "domain", "colspan": 2}, None]])
        # Data for Bar Graph
        data2plot = df.groupby(pd.Grouper(freq='M'))['Amount']. \
            agg(['mean', 'sum', 'max']).sort_values(by=['Date', 'sum'], ascending=[True, False]).round(2)
        # Plot Data onto First Graph
        fig.add_trace(go.Bar(name='Total', x=data2plot.index, y=data2plot["sum"]), row=1, col=1)
        fig.add_trace(go.Bar(name='Max', x=data2plot.index, y=data2plot["max"]), row=1, col=1)
        fig.add_trace(go.Bar(name='Month\'s Average', x=data2plot.index, y=data2plot["mean"]), row=1, col=1)

        fig.update_layout(barmode='group', xaxis_tickangle=-45, title="{}: {}".format(plt_opt, cat_opt),
                          xaxis_title="Date", yaxis_title="USD ($)")
        fig.update_traces(hovertemplate="Date: %{x} <br>Amount:%{y:$,.2f}")

        # Data for Pie Chart Breakdown
        d2p2 = df.groupby("Category")["Amount"].sum()
        # Plot Data onto Second Graph
        fig.add_trace(go.Pie(labels=d2p2.index, values=d2p2,
                             hovertemplate="Category: %{label} <br>Amount:%{value:$,.2f}",
                             textposition='inside', textinfo='percent+label'), row=2, col=1)

        fig.update_layout(height=800, title="{} Breakdown".format(cat_opt))
    else:
        # General Overview of Top Expense Categories
        gb_df = df[df["Category2"] != "Income"].groupby("Category2")["Amount"].sum()
        fig = px.bar(x=gb_df.index, y=gb_df)
    return fig


# Update Category Options
@app.callback([Output('category-dropdown', 'options'),
               Output('category-dropdown', 'value'),
               Output('category-dropdown', 'multi')],
              [Input('plot-options', 'value')],
              [State('lists-json-dump', 'children')])
def update_categories(opt, json_dump):
    if json_dump is None:
        raise PreventUpdate
    else:
        cat_list = json.loads(json_dump)[0]
        options = [{'label': i, 'value': i} for i in cat_list]

        multi = False if opt == "Individual Category" else True
        val_list = cat_list[0] if opt == "Individual Category" else cat_list

    return options, val_list, multi


# Update account list
@app.callback([Output('account-checklist', 'options'),
              Output('account-checklist', 'value')],
              [Input('update-btn', 'n_clicks')],
              [State('lists-json-dump', 'children')])
def update_accounts(tab, json_dump):
    if json_dump is None:
        raise PreventUpdate
    elif tab == 1:  # (json_dump is not None) & (nclicks == 'Plot')
        account_list = json.loads(json_dump)[1]
        options = [{'label': i, 'value': i} for i in account_list]
        return options, account_list
    else:
        raise PreventUpdate
