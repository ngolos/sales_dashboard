import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import time
import requests
# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="Sales Report", 
    page_icon="💲", 
    layout="wide",
)

# Markdown for header and description
st.markdown("<h2 style='text-align: left; color: black;'>MavenTech Sales Performance</h1>", unsafe_allow_html=True)
#st.markdown("<p style='text-align: center; color: black;'>This interactive report is created as an example of exploratory sales data analysis.</p>", unsafe_allow_html=True)

# Hide the main menu and footer in Streamlit
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Define a function to fetch and process the data
@st.cache_data  # 👈 Add the caching decorator
def load_data(url):
    df = pd.read_csv(url, keep_default_na=False)
    # Ensure the close_value column is numeric
    df['close_value'] = df['close_value'].apply(pd.to_numeric)  # Coerce errors will convert non-convertible values to NaN
    df['days_to_close'] = df['days_to_close'].apply(pd.to_numeric)
    # Assuming df is already loaded and 'close_date' and 'engage_date' are datetime types
    df['engage_date'] = pd.to_datetime(df['engage_date'], errors='coerce')
    df['close_date'] = pd.to_datetime(df['close_date'], errors='coerce')
    # Add quarter-year for engage date
    df['engage_quarter'] = df['engage_date'].dt.to_period('Q')
    return df



# URL of the CSV file
url = "https://raw.githubusercontent.com/ngolos/sales_dashboard/main/cleaned_data.csv"
data = load_data(url)
data2 = [
    {"label": "Begin", "amount": 151087, "regional_office": "ALL"},
    {"label": "2017Q1", "amount": 714963, "regional_office": "ALL"},
    {"label": "2017Q2", "amount": 1040553, "regional_office": "ALL"},
    {"label": "2017Q3", "amount": 1749696,  "regional_office": "ALL"},
    {"label": "2017Q4", "amount": 235930,  "regional_office": "ALL"},
    {"label": "End", "amount": 0,  "regional_office": "ALL"},
    {"label": "Begin", "amount": 0, "regional_office": "Central"},
    {"label": "2017Q1", "amount": 0,  "regional_office": "Central"},
    {"label": "2017Q2", "amount": 0,  "regional_office": "Central"},
    {"label": "2017Q3", "amount": 824422,  "regional_office": "Central"},
    {"label": "2017Q4", "amount": 0,  "regional_office": "Central"},
    {"label": "End", "amount": 0,  "regional_office": "Central"},
    {"label": "Begin", "amount": 53541, "regional_office": "East"},
    {"label": "2017Q1", "amount": 243793,  "regional_office": "East"},
    {"label": "2017Q2", "amount": 343663,  "regional_office": "East"},
    {"label": "2017Q3", "amount": 331542,  "regional_office": "East"},
    {"label": "2017Q4", "amount": 97047,  "regional_office": "East"},
    {"label": "End", "amount": 0,  "regional_office": "East"},
    {"label": "Begin", "amount": 97546, "regional_office": "West"},
    {"label": "2017Q1", "amount": 471170,  "regional_office": "West"},
    {"label": "2017Q2", "amount": 696890,  "regional_office": "West"},
    {"label": "2017Q3", "amount": 593732,  "regional_office": "West"},
    {"label": "2017Q4", "amount": 138883,  "regional_office": "West"},
    {"label": "End", "amount": 0,  "regional_office": "West"},
]
source = pd.DataFrame(data2)

data3=[
    {"regional_office": "Central", "revenue":824422},
    {"regional_office": "East", "revenue":1069586},
    {"regional_office": "West", "revenue":1998221},
    {"regional_office": "ALL", "revenue":3892229},
]
engaged_deals=pd.DataFrame(data3)

###create dataframe for first block 
won_aggregate = data.query('deal_stage=="Won"').groupby(['regional_office', 'deal_stage', 'quarter']).agg({
        'close_value': 'sum',
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'close_value': 'Value', 'opportunity_id': 'Deal_Count', })

lost_aggregate = data.query('deal_stage=="Lost"').groupby(['regional_office', 'deal_stage', 'quarter']).agg({
        'sales_price': 'sum',    
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'sales_price': 'Value', 'opportunity_id': 'Deal_Count', })

engaging_aggregate = data.query('deal_stage=="Engaging"').groupby(['regional_office', 'deal_stage', 'engage_quarter']).agg({
        'sales_price': 'sum',    
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'engage_quarter':'quarter', 'sales_price': 'Value', 'opportunity_id': 'Deal_Count', })

won_aggregate_year = data.query('deal_stage=="Won"').groupby(['deal_stage', 'quarter']).agg({
        'close_value': 'sum',
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'close_value': 'Value', 'opportunity_id': 'Deal_Count', })

won_aggregate_year['regional_office']="ALL"
new_order=['regional_office', 'deal_stage', 'quarter', 'Value', 'Deal_Count',]
won_aggregate_year=won_aggregate_year.reindex(columns=new_order)


lost_aggregate_year = data.query('deal_stage=="Lost"').groupby(['deal_stage', 'quarter']).agg({
        'sales_price': 'sum',
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'sales_price': 'Value', 'opportunity_id': 'Deal_Count', })
lost_aggregate_year['regional_office']="ALL"
#new_order=['regional_office', 'deal_stage', 'quarter', 'close_value', 'Deal Count',]
lost_aggregate_year=lost_aggregate_year.reindex(columns=new_order)


engage_aggregate_year = data.query('deal_stage=="Engaging"').groupby(['deal_stage', 'engage_quarter']).agg({
        'sales_price': 'sum',
        'opportunity_id': 'count'        
    }).reset_index().rename(columns={'engage_quarter':'quarter', 'sales_price': 'Value', 'opportunity_id': 'Deal_Count', })
engage_aggregate_year['regional_office']="ALL"
#new_order=['regional_office', 'deal_stage', 'quarter', 'close_value', 'Deal Count',]
engage_aggregate_year=engage_aggregate_year.reindex(columns=new_order)


# Merging all dataframes
merged_data = pd.concat([won_aggregate, lost_aggregate, engaging_aggregate, won_aggregate_year, lost_aggregate_year, engage_aggregate_year])



# Filters for product family, manager, and sector
office = merged_data['regional_office'].drop_duplicates()
office_choice = st.selectbox('Select your office from 3 options:', options=sorted(office), index=0, )


#product_family = st.multiselectbox('Select Product Family', df['product'].unique())
#manager = st.selectbox('Select Manager', df['sales_agent'].unique())
#sector = st.selectbox('Select Sector', df['sector'].unique())

# Calculate and display sales for the last quarter
#latest_date = data['close_date'].max()
#latest_year = latest_date.year
latest_quarter = '2017Q4'
latest_year=2017
#st.write(latest_quarter)
import pandas as pd

# Assuming merged_data is already defined

year_filter = "2017"

# Extract the year from the quarter for easy comparison
merged_data['year'] = merged_data['quarter'].str[:4]

# Calculate total sales by 'Won' deals for the specified office and year
total_sales_won = merged_data.loc[(merged_data['regional_office'] == office_choice) & 
                                  (merged_data['deal_stage'] == 'Won') & 
                                  (merged_data['year'] == year_filter), 'Value'].sum()


#st.write(merged_data.query('deal_stage=="Engaging"'))
# Calculate sales for Q3 and Q4 for 'Won' deals
q3_sales = merged_data.loc[(merged_data['regional_office'] == office_choice) & 
                           (merged_data['deal_stage'] == 'Won') & 
                           (merged_data['quarter'] == '2017Q3') & 
                           (merged_data['year'] == year_filter), 'Value'].sum()

q4_sales = merged_data.loc[(merged_data['regional_office'] == office_choice) & 
                           (merged_data['deal_stage'] == 'Won') & 
                           (merged_data['quarter'] == '2017Q4') & 
                           (merged_data['year'] == year_filter), 'Value'].sum()

percent_change = ((q4_sales - q3_sales) / q3_sales) * 100 if q3_sales != 0 else 0

# Calculate won vs total deals percentage using groupby directly on the filtered data
deals_summary = merged_data.loc[(merged_data['regional_office'] == office_choice) & 
                                (merged_data['year'] == year_filter) &
                                (merged_data['deal_stage'].isin(['Won', 'Lost']))].groupby(['quarter', 'deal_stage'])['Deal_Count'].sum().unstack(fill_value=0)

deals_summary['percent_won'] = (deals_summary['Won'] / (deals_summary['Won'] + deals_summary['Lost'])) * 100
percent_won = deals_summary['percent_won']
# Output the results
#st.write("### Total sales for 'Won' deals in 2017:", total_sales_won)
#st.write("### Percentage change from Q3 to Q4 in 2017:", f"{percent_change:.2f}%")
#st.write("### Percentage of 'Won' deals for each quarter in 2017:")
#st.write(percent_won)
# Filter for "Won" deals in the latest quarter
won_deals_last_quarter = merged_data[(merged_data['deal_stage'] == 'Won') & (merged_data['regional_office']==office_choice) & (merged_data['quarter'] == latest_quarter)]
#lost_deals_last_quarter = merged_data[(merged_data['deal_stage'] == 'Lost') & (merged_data['regional_office']==office_choice) & (merged_data['quarter'] == latest_quarter)]
# Calculate total sales
total_sales_last_quarter = won_deals_last_quarter['Value'].sum()
pending_ratio= 100*((engaged_deals[engaged_deals['regional_office'] == office_choice]['revenue'].iloc[0])/total_sales_won)
# Calculating percentage of won deals to lost deals


col1, col2, col3, col4 = st.columns(4)
col1.metric(label=(f"Annual Sales: {office_choice}"), value=(f"$ {total_sales_won/1000000:,.2f}Mln"))
col2.metric(label=(f"Sales Performance in {latest_quarter}"), value=(f"$ {total_sales_last_quarter/1000000:,.2f}Mln"), delta=(f"{percent_change:.2f}% vs PQ"))
col3.metric(label=(f"% Won Deals in {latest_quarter}"), value=(f"{percent_won.iloc[3]:.1f}%"), delta=(f"{((percent_won.iloc[3]/percent_won.iloc[2])-1)*100:.2f}% vs PQ")) #st.write(latest_quarter)
col4.metric(label=(f"% Pending Deals Value /Annual Sales"), value=(f"{pending_ratio:.1f}%"), delta=None)





# TOP KPI's

st.write("---")

# Display sales information, ensuring the sum is a float
#st.write(f"Share of Engaging Deals by the End of Q42017 : ${total_sales_last_quarter:,.0f}")

#Filter df based on selection
won_data = merged_data[(merged_data['regional_office']==office_choice)& (merged_data['deal_stage']=="Won")]
lost_data =merged_data[(merged_data['regional_office']==office_choice)& (merged_data['deal_stage']=="Lost")]
engage_data =merged_data[(merged_data['regional_office']==office_choice)& (merged_data['deal_stage']=="Engaging")]
#on_data = merged_data.query('regional_office == "ALL" & deal_stage == "Won"')
def round_up_to_next_nearest(number, nearest):
    # Check if the number is already a multiple of the nearest
    if number % nearest == 0:
        return number
    else:
        return ((number // nearest) + 1) * nearest
    
  
import math
max_value_1 = merged_data.query(f'regional_office == "{office_choice}"')['Value'].max()
max_value_2 = merged_data.query(f'regional_office == "{office_choice}"')['Deal_Count'].max()
cumsum_max1 = merged_data.query(f'regional_office == "{office_choice}" & deal_stage == "Engaging"')['Value'].cumsum().max()
cumsum_max2 = merged_data.query(f'regional_office == "{office_choice}" & deal_stage == "Engaging"')['Deal_Count'].cumsum().max()
max_value1 = round_up_to_next_nearest(max(max_value_1, cumsum_max1), 250000)
max_value2 = round_up_to_next_nearest(max_value_2, 500)
#st.write(max_value1)

# Base encoding
base = alt.Chart(won_data).encode(
    x=alt.X('quarter:N', axis=alt.Axis(title='', labelAngle=0)),  # Set label angle and remove title
    tooltip=[
        alt.Tooltip('quarter', title='Quarter'), 
        alt.Tooltip('Value:Q', title='Value', format='$,.0f'),  # Formatting 'Value' as currency
        alt.Tooltip('Deal_Count', title='Deal Count', format=',.0f')
    ]
)

# Bar chart for 'Value' with tooltip
bar = base.mark_bar(color='royalblue').encode(
    y=alt.Y('Value:Q', scale=alt.Scale(domain=[0, max_value1]), axis=alt.Axis(title='', tickCount=5, format='$,.0f', grid=True))
)
# Text labels on bars
text = base.mark_text(align='center', baseline='middle', dy=-10, color='white').encode(
    y=alt.Y('mid:Q', scale=alt.Scale(domain=[0, max_value1]), axis=None),
    text=alt.Text('Value:Q', format='$,.0f')
).transform_calculate(
    mid='datum.Value / 2'
)
# Line chart for 'Deal_Count' with tooltip
line = base.mark_line(color='firebrick').encode(
    y=alt.Y('Deal_Count:Q', scale=alt.Scale(domain=[0, max_value2]), axis=alt.Axis(title=''))
)
text_line = base.mark_text(
    align='center',
    dy=-10,  # Adjust this value to position text above or below the line points
    color='firebrick'
).encode(
    y=alt.Y('Deal_Count:Q', scale=alt.Scale(domain=[0, max_value2]), axis=None),
    text=alt.Text('Deal_Count:Q')
)

# Combine the charts with independent y-axes and set chart properties
won = (bar + text + line+text_line).resolve_scale(
    y='independent'
).properties(
    #width=250,
    #height=350,
    title="Revenue & Number of Deals Secured per Quarter"
)



# Base encoding
base = alt.Chart(lost_data).encode(
    x=alt.X('quarter:N', axis=alt.Axis(title='', labelAngle=0)),  # Set label angle and remove title
    tooltip=[
        alt.Tooltip('quarter', title='Quarter'), 
        alt.Tooltip('Value:Q', title='Value', format='$,.0f'),  # Formatting 'Value' as currency
        alt.Tooltip('Deal_Count', title='Deal Count')
    ]
)

# Bar chart for 'Value'
bar = base.mark_bar(color='white', stroke='royalblue', strokeWidth=2).encode(
    y=alt.Y('Value:Q',  scale=alt.Scale(domain=[0, max_value1]), axis=alt.Axis(title='', tickCount=5, format='$,.0f', grid=True))  # Remove title
)
# Text labels on bars
text = base.mark_text(align='center', baseline='middle', dy=-10, color='blue').encode(
    y=alt.Y('mid:Q', scale=alt.Scale(domain=[0, max_value1]), axis=None),
    text=alt.Text('Value:Q', format='$,.0f')
).transform_calculate(
    mid='datum.Value / 2.75'
)

# Line chart for 'Deal_Count'
line = base.mark_line(color='firebrick').encode(
    y=alt.Y('Deal_Count:Q', scale=alt.Scale(domain=[0, max_value2]), axis=alt.Axis(title=''))  # Remove title
)

# Text labels on line
text_line = base.mark_text(
    align='center',
    dy=-10,  # Adjust this value to position text above or below the line points
    color='firebrick'
).encode(
    y=alt.Y('Deal_Count:Q', scale=alt.Scale(domain=[0, max_value2]), axis=None),
    text=alt.Text('Deal_Count:Q')
)

# Combine the charts with independent y-axes and set chart properties
lost = (bar + line +text + text_line).resolve_scale(
    y='independent'
).properties(
    #width=250,
    #height=350,
    title="Value $ and Number of Opportunities Lost by Quarter"
)





# The "base_chart" defines the transform_window, transform_calculate, and X axis
base_chart = alt.Chart(source[source['regional_office']==office_choice]).transform_window(
    window_sum_amount="sum(amount)",
    window_lead_label="lead(label)",
).transform_calculate(
    calc_lead="datum.window_lead_label === null ? datum.label : datum.window_lead_label",
    calc_prev_sum="datum.label === 'End' ? 0 : datum.window_sum_amount - datum.amount",
    calc_amount="datum.label === 'End' ? datum.window_sum_amount : datum.amount",
    calc_text_amount="(datum.label !== 'Begin' && datum.label !== 'End' && datum.calc_amount > 0 ? '+' : '') + datum.calc_amount",
    calc_center="(datum.window_sum_amount + datum.calc_prev_sum) / 2",
    calc_sum_dec="datum.window_sum_amount < datum.calc_prev_sum ? datum.window_sum_amount : ''",
    calc_sum_inc="datum.window_sum_amount > datum.calc_prev_sum ? datum.window_sum_amount : ''",
).encode(
    x=alt.X(
        "label:O",
        axis=alt.Axis(title="", labelAngle=0),
        sort=None,
    )
)

# alt.condition does not support multiple if else conditions which is why
# we use a dictionary instead. See https://stackoverflow.com/a/66109641
# for more information
color_coding = {
    "condition": [
        {"test": "datum.label === 'Begin' || datum.label === 'End'", "value": "black"},
        {"test": "datum.calc_amount < 0", "value": "slategrey"},
    ],
    "value": "slategrey",
}

bar = base_chart.mark_bar(size=55).encode(
    y=alt.Y("calc_prev_sum:Q", axis=alt.Axis(tickCount=5, title="", format='$,.0f'),  scale=alt.Scale(domain=[0, max_value1])),
    y2=alt.Y2("window_sum_amount:Q"),
    color=color_coding,
)

# The "rule" chart is for the horizontal lines that connect the bars
rule = base_chart.mark_rule(
    xOffset=-27.5,
    x2Offset=27.5,
).encode(
    y="window_sum_amount:Q",
    x2="calc_lead",
)

# Add values as text
text_pos_values_top_of_bar = base_chart.mark_text(
    baseline="bottom",
    dy=-4
).encode(
    text=alt.Text("calc_sum_inc:N"),
    y="calc_sum_inc:Q"
)
text_neg_values_bot_of_bar = base_chart.mark_text(
    baseline="top",
    dy=4
).encode(
    text=alt.Text("calc_sum_dec:N"),
    y="calc_sum_dec:Q"
)
text_bar_values_mid_of_bar = base_chart.mark_text(baseline="middle").encode(
    text=alt.Text("calc_text_amount:N"),
    y=alt.Y("calc_center:Q", ),
    color=alt.value("white"),
)

col3_chart=alt.layer(
    bar,
    rule,
    text_pos_values_top_of_bar,
    text_neg_values_bot_of_bar,
    text_bar_values_mid_of_bar
).properties(
    title="Cumulated Potential Revenue from Pending Deals",
    #width=250,
    #height=350,    
)

# Visualizations in Streamlit columns
col4, col5, col6 = st.columns(3, gap='medium')

with col4:
    st.subheader('Quarterly Revenue: Won Deals')  
    st.altair_chart(won, use_container_width=True)

with col5:
    st.subheader('Lost Opportunities')
    
    st.altair_chart(lost, use_container_width=True)

# Chart 3: Average Opportunity Value by Quarter
with col6:
    st.subheader('Open Deals')
    
    st.altair_chart(col3_chart, use_container_width=True)

#st.write('ALL - add - nature of engaging deals - group 1 column - office and core clientele, 2 column other offices. 3 without clients')
#st.write('ALL - split by deals - ')
#st.write('ALL - split by size to show potential grouping')

#st.write('Regions - 1. split inside teams and 2. activity 3. by client')
#with col4:
#    st.subheader('Average Days to Close by Quarter')
#    days_chart = alt.Chart(grouped).mark_line(point=True).encode(
#        x=alt.X('quarter_year:N', title="", axis=alt.Axis(labelAngle=0)),
#        y=alt.Y('average_days_to_close:Q',title=""),
#        color=alt.Color('deal_stage:N', scale=color_scale),
#        tooltip=['quarter_year', 'average_value', 'deal_stage']
#    )
#    st.altair_chart(days_chart, use_container_width=True)


def create_series_chart(source, series_name, product_order):
    # Filter for the specific series and any of the deal stages
    filtered_source = source.query(f"series == '{series_name}' and deal_stage in ['Won', 'Lost', 'Engaging']")
    
    # Create a chart for each product in the predefined order, only if it exists in the filtered source
    chart_list = []
    for product in product_order:
        if product in filtered_source['product'].unique():
            chart = alt.Chart(filtered_source.query(f"product == '{product}'")).mark_bar(size=5).encode(
                x=alt.X('engage_week_number:O', title='',
                        scale=alt.Scale(domain=list(range(1, 53))),
                        axis=alt.Axis(values=[13, 26, 39, 52], grid=True,
                                      labelExpr="datum.value == 13 ? 'Q1' : datum.value == 26 ? 'Q2' : datum.value == 39 ? 'Q3' : 'Q4'", labelAngle=0)),
                x2='close_week_number:O',
                y=alt.Y('new_opportunity_id:N', title='',  axis=alt.Axis(labelFontSize=8)),
                color=alt.Color(
                    'deal_stage:N', 
                    scale=alt.Scale(domain=['Won', 'Lost', 'Engaging'],
                                            range=['green', 'red', 'lightgrey']),  # Custom color per deal stage
                    legend=alt.Legend(orient='top')), 
                tooltip=[alt.Tooltip('manager:N', title="Manager"), alt.Tooltip('sales_agent:N', title="Agent"), alt.Tooltip('regional_office:N', title="Office"), alt.Tooltip('days_to_close:O', title="Days to close")]
            ).properties(
                width=250, height=120,
                title=f"{product} in {series_name}"
            )
            chart_list.append(chart)

    # Concatenate all product charts vertically
    if chart_list:
        final_chart = alt.vconcat(*chart_list).resolve_scale(x='shared')
    else:
        final_chart = alt.Chart().mark_text(text='No data available for this series').properties(width=250, height=120)
    
    return final_chart

# Define the order of products
product_order = ['GTXPro', 'GTXPlusPro', 'GTXBasic', 'GTXPlusBasic', 'MGAdvanced', 'MGSpecial', 'GTK500']

# Example usage of the function with your DataFrame 'data'
df1 = data.query('account=="Acme Corporation"')
gtx_chart = create_series_chart(df1, "GTX", product_order)
mg_chart = create_series_chart(df1, "MG", product_order)
gtk_chart = create_series_chart(df1, "GTK", product_order)

# Display or process your charts as needed
final_comparison_chart = alt.hconcat(gtx_chart, mg_chart, gtk_chart).resolve_scale(
    y='independent'
).properties(
    #title="Comparison of GTX, MG, and GTK Series"
)



# Assuming 'Won' deals are relevant for this plot
won_data = data[data['deal_stage'] == 'Won']

# Aggregate the data to count opportunities and sum close values by account and region
aggregated_data = won_data.groupby(['account', 'Client_Region']).agg(
    total_opportunities=('opportunity_id', 'count'),
    total_close_value=('close_value', 'sum')
).reset_index()

# Define a scale for shapes to ensure each region has a unique marker
shape_scale = alt.Scale(domain=aggregated_data['Client_Region'].unique(), 
                        range=['circle', 'square', 'triangle-up', 'diamond', 'cross'])

# Create a selection for the legend
legend_selection = alt.selection_multi(fields=['Client_Region'], bind='legend')

# Define interaction for zoom and pan
zoom = alt.selection_interval(bind='scales', encodings=['x'])

st.write("---")
# Create a scatterplot using mark_circle

won_data = data[data['deal_stage'] == 'Won']

# Aggregate the data to count opportunities and sum close values by account and region
aggregated_data = won_data.groupby(['account', 'Client_Region', 'sector']).agg(
    total_opportunities=('opportunity_id', 'count'),
    total_close_value=('close_value', 'sum')
).reset_index()

# Define a scale for shapes to ensure each region has a unique marker
shape_scale = alt.Scale(domain=aggregated_data['Client_Region'].unique(), 
                        range=['circle', 'square', 'triangle-up', 'diamond', 'cross'])

# Create a selection for the legend
legend_selection = alt.selection_multi(fields=['Client_Region'], bind='legend')

# Define interaction for zoom and pan
zoom = alt.selection_interval(bind='scales', encodings=['x'])

# Create a scatterplot using mark_circle
scatter_plot = alt.Chart(aggregated_data).mark_circle(size=60).encode(
    x=alt.X('total_opportunities:Q', title='Total Won Opportunities by Account'),
    y=alt.Y('total_close_value:Q', title='Sum of Close Value'),
    color=alt.Color('Client_Region:N', legend=alt.Legend(title='Client Region')),
    shape=alt.Shape('Client_Region:N', scale=shape_scale, legend=alt.Legend(title='Client Region Shapes')),
    opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.05)),
    tooltip=[alt.Tooltip('account:N', title='Account'), alt.Tooltip('sector:N', title='Sector'),alt.Tooltip('total_close_value:Q', title='Close Value')]
).properties(
    title='Client Split by regional offices',
    width=800,
    height=400
).add_selection(
    legend_selection,
    zoom
)




# Display the plot



#chart for office manager split
if office_choice != "ALL":
    # Assuming 'data' and 'office_choice' are predefined
    closed_deals = data[data['deal_stage'] == 'Won']

    # Group by required fields and sum up the closed value
    summary_table_by_manager = closed_deals.groupby(
        ['account', 'regional_office', 'manager', 'sales_agent', 'sector']
    )['close_value'].sum().reset_index()

    # Filter for the chosen office
    chart_office = summary_table_by_manager.query(f'regional_office == "{office_choice}"')

    # Assign unique colors to each manager
    unique_managers = chart_office['manager'].unique()
    colors = ['orange', 'blue', 'green', 'purple', 'red']  # Example color palette
    manager_colors = alt.Scale(domain=unique_managers, range=colors[:len(unique_managers)])

    # Calculate opacity for each sales agent within their manager's group
    chart_office['opacity_index'] = chart_office.groupby('manager')['sales_agent'].transform(lambda x: pd.factorize(x)[0])
    max_opacity_index = chart_office.groupby('manager')['opacity_index'].transform('max')
    chart_office['opacity'] = 0.05 + 0.95 * (chart_office['opacity_index'] / max_opacity_index)

    # Create the Altair chart
    chart = alt.Chart(chart_office).mark_bar(
        stroke='white',       # Border color
        strokeWidth=1         # Border width
    ).encode(
        y=alt.Y('account:N', sort='-x', title=""),
        x=alt.X('close_value:Q', title='Total Closed Value'),
        color=alt.Color('manager:N', scale=manager_colors, legend=alt.Legend(title="Manager")),
        opacity=alt.Opacity('opacity:Q', legend=alt.Legend(title="Sales Agent Distinction")),
        tooltip=['account', 'manager', 'sales_agent', 'close_value']
    ).properties(
        width=400,
        height=600,
        title=f'Split by Team - {office_choice} Office'
    )

    st.altair_chart(chart)
else:
    st.altair_chart(scatter_plot)


st.write("---")
st.altair_chart(final_comparison_chart)
