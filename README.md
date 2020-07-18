# BudgetApp-Dash
App designed with Plotly Dash for viewing transaction data from Mint. Data is summarized into your top 7 categories and remaining categories are grouped into the "Other" category.

### Expected format
Date | Description | Original Descrition | Amount | Transaction Type | Category | Account Name | Labels | Notes 
---- | ----------- | ------------------- | ------ | ---------------- | -------- | ------------ | ------ | -----
03/21/2020 | Netflix | NETFLIX.COM | 8.99| debit | Movies & DVDs | Credit Card 1| | Example 


## How to Use:
### Step 1:
Load Mint excel/csv file. 
![Image of Load Page](https://github.com/rchr157/BudgetApp-Dash/blob/master/screenshots/shot1-load.JPG)

### Step2:
Select type of plot and date. Plot options include:
- Monthly Breakdown: Pie Chart Overview of Total Expenses for the month
- Net Income: Bar Chart showing Income vs Expenses and overall net income for date specified
- Individual Category: Pie Chart showing makeup of category selected.
![Image of Main Page](https://github.com/rchr157/BudgetApp-Dash/blob/master/screenshots/shot2-main.JPG)

### Monthly Breakdown
Total expense for the month selected is shown in the title.
Percent and actual total for each category is shown in pie chart.
![Image of Monthly Breakdown](https://github.com/rchr157/BudgetApp-Dash/blob/master/screenshots/shot3a-monthbreak.JPG)

### Net Income
This plot option takes in an additional start date. 
Plots show Income vs Expenses along with the Net Income
![Image of Net Income](https://github.com/rchr157/BudgetApp-Dash/blob/master/screenshots/shot3b-netincome.JPG)


### Individual Category
Provides closer look at selected category over specified period.
Looks at monthly total, maximum, and average. Also provies the average total over the specified date.
![Image of Individual Categories](https://github.com/rchr157/BudgetApp-Dash/blob/master/screenshots/shot3c-individualcat.JPG)

## Optional Features

### Apply Filters
You can filter the data by 
- Date
- Account
- Category

