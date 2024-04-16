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
st.set_page_config(page_title="Sales Report", page_icon="💲", layout="wide")

# Markdown for header and description
st.markdown("<h1 style='text-align: center; color: red;'>Sales Report</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: black;'>This interactive report is created as an example of exploratory sales data analysis.</p>", unsafe_allow_html=True)

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
url = "https://raw.githubusercontent.com/ngolos/sales_dashboard/main/merged_data.csv"
df = load_data(url)

# Filters for product family, manager, and sector
office = df['regional_office'].drop_duplicates()
office_choice = st.multiselect('Select your office from 3 options:', options=sorted(office), default='West')


#product_family = st.selectbox('Select Product Family', df['product'].unique())
#manager = st.selectbox('Select Manager', df['sales_agent'].unique())
#sector = st.selectbox('Select Sector', df['sector'].unique())



# Calculate and display sales for the last quarter
latest_date = df['close_date'].max()
latest_year = latest_date.year
latest_quarter = latest_date.quarter

# Filter for "Won" deals in the latest quarter
won_deals_last_quarter = df[(df['deal_stage'] == 'Won') & 
                            (df['close_date'].dt.year == latest_year) & 
                            (df['close_date'].dt.quarter == latest_quarter)]

# Calculate total sales
total_sales_last_quarter = won_deals_last_quarter['close_value'].sum()

# Display sales information, ensuring the sum is a float
if pd.notna(total_sales_last_quarter):
    st.subheader(f'Total Sales for Last Quarter (Q{latest_quarter} {latest_year})')
    st.write(f"Total sales: ${total_sales_last_quarter:,.2f}")
else:
    st.write("No sales data available for the last quarter.")

# Calculate total sales per quarter
df['quarter_year'] = df['close_date'].dt.to_period('Q')

# Group data to sum values for won and lost deals
quarterly_data = df.groupby(['quarter_year', 'deal_stage', 'regional_office', 'manager', 'series', 'product', 'sector']).agg({'close_value': 'sum', 'sales_price': 'sum'}).reset_index()

# Filter to show 'Won' and 'Lost' deals for the sales chart
quarterly_sales_won = quarterly_data[quarterly_data['deal_stage'] == 'Won']
quarterly_sales_lost = quarterly_data[quarterly_data['deal_stage'] == 'Lost']

# Count opportunities per quarter for the count chart
quarterly_opportunities = df.groupby(['quarter_year', 'deal_stage']).size().reset_index(name='count')

# Calculate sums and counts for each group
grouped = df.groupby(['quarter_year', 'deal_stage']).agg({
    'close_value': 'sum', 
    'sales_price': 'sum',
    'deal_stage': 'size',
    'days_to_close': 'mean'
}).rename(columns={'deal_stage': 'count', 'days_to_close': 'average_days_to_close'}).reset_index()

# Calculating the average values depending on deal stage
grouped['average_value'] = grouped.apply(
    lambda x: x['close_value'] / x['count'] if x['deal_stage'] == 'Won' else x['sales_price'] / x['count'], axis=1
)

# Round the last two columns to 2 decimal places
grouped['average_days_to_close'] = grouped['average_days_to_close'].round(1)
grouped['average_value'] = grouped['average_value'].round(2)
st.dataframe(grouped)

# Filter for chart
average_values_chart_data = grouped[['quarter_year', 'deal_stage', 'average_value']]




# Get the latest date from data or use current date to find the last quarter
last_date = df['close_date'].max()
last_quarter = last_date.to_period('Q') if pd.notnull(last_date) else pd.Timestamp('now').to_period('Q')

# Expand 'Engaging' deals across quarters
engaging_df = df[df['deal_stage'] == 'Engaging']
expanded_rows = []

for index, row in engaging_df.iterrows():
    start_q = row['engage_quarter']
    end_q = last_quarter
    period = pd.period_range(start=start_q, end=end_q, freq='Q')
    for quarter in period:
        deal_stage = 'Ongoing' if quarter > start_q else 'Engaging'  # Conditionally set 'Engaging' or 'Ongoing'
        expanded_rows.append({
            'opportunity_id': row['opportunity_id'], 
            'sales_agent': row['sales_agent'], 
            'product': row['product'],
            'account': row['account'],
            'quarter_year': str(quarter),  # Convert the Period object to a string
            'deal_stage': deal_stage,
            'sales_price': row['sales_price'],
            'close_value': 0,
            'engage_date': row['engage_date'], 
            'year': row['year'], 
            'quarter':row['quarter'],
            'manager': row['manager'], 
            'regional_office':row['regional_office'], 
            'sector':row['sector'], 
            'series':row['series'],
       'engage_quarter':row['engage_quarter'],
        })
        
# Convert expanded rows into a DataFrame
expanded_df = pd.DataFrame(expanded_rows)

# Combine with existing data
# Combine with original data for each chart and compute necessary aggregations
combined_data = pd.concat([df, expanded_df])

# Convert expanded rows into a DataFrame
expanded_df = pd.DataFrame(expanded_rows)

# Combine with existing data
# Combine with original data for each chart and compute necessary aggregations
combined_data = pd.concat([df, expanded_df])
# Grouping and aggregation for charts
final_data = combined_data.groupby(['quarter_year', 'deal_stage']).agg({
    'close_value': 'sum', 
    'sales_price': 'sum',
    'deal_stage': 'size'
}).rename(columns={'deal_stage': 'count'}).reset_index()

# Calculate average values
final_data['average_value'] = final_data['sales_price'] / final_data['count']
final_data['quarter_year'] = final_data['quarter_year'].astype(str)
# Visualizations
col1, col2, col3 = st.columns(3)

# Define the domain and color range for deal_stage categories
color_scale = alt.Scale(domain=['Won', 'Lost', 'Engaging', 'Ongoing'],  # Update the list with actual stages
                        range=['steelblue', 'lightseagreen', '#7D3C98','silver'])  # Assign colors to each stage

# Chart 1: Total Sales Value by Quarter
with col1:
    st.subheader('Total Sales Value by Quarter')
    won_chart = alt.Chart(final_data.query("deal_stage=='Won'")).mark_line(point=True).encode(
        x=alt.X('quarter_year:N', title='', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('close_value:Q', title=''),
        color=alt.Color('deal_stage:N', scale=color_scale),
        tooltip=[alt.Tooltip('quarter_year:N', title='Quarter'), alt.Tooltip('close_value:Q', title='Total Sales')]
    )
    lost_chart = alt.Chart(final_data.query("deal_stage!='Won'")).mark_line(point=True).encode(
        x=alt.X('quarter_year:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('sales_price:Q',title=""),
        color=alt.Color('deal_stage:N', scale=color_scale),
        tooltip=['quarter_year', 'sales_price', 'deal_stage']
    )
    combined_chart = alt.layer(won_chart, lost_chart).resolve_scale(y='shared')
    st.altair_chart(combined_chart, use_container_width=True)

# Chart 2: Number of Opportunities by Quarter
stack_order = {
    'Won': 1,      # Lower number -> lower in the stack
    'Lost': 2,
    'Engaging': 3,
    'Ongoing': 4
}
# Assign a new column for sorting based on your defined order
final_data['sort_order'] = final_data['deal_stage'].map(stack_order)

with col2:
    st.subheader('Number of Opportunities by Quarter')
    opportunities_chart = alt.Chart(final_data).mark_bar().encode(
        x=alt.X('quarter_year:N', title="", axis=alt.Axis(labelAngle=0)),
         y=alt.Y('count:Q', stack='zero', title=""),  # Ensure stacking starts from zero
    color=alt.Color('deal_stage:N', scale=color_scale),  # Use your color scale
    order=alt.Order('sort_order:O', sort='ascending'),  # Control the stacking order with the order encoding
    tooltip=['quarter_year', 'count', 'deal_stage']
    )
    st.altair_chart(opportunities_chart, use_container_width=True)

# Chart 3: Average Opportunity Value by Quarter
with col3:
    st.subheader('Average Opportunity Value by Quarter')
    average_chart = alt.Chart(final_data).mark_line(point=True).encode(
        x=alt.X('quarter_year:N', title="", axis=alt.Axis(labelAngle=0)),
        y=alt.Y('average_value:Q',title=""),
        color=alt.Color('deal_stage:N', scale=color_scale),
        tooltip=['quarter_year', 'average_value', 'deal_stage']
    )
    st.altair_chart(average_chart, use_container_width=True)
#with col4:
#    st.subheader('Average Days to Close by Quarter')
#    days_chart = alt.Chart(grouped).mark_line(point=True).encode(
#        x=alt.X('quarter_year:N', title="", axis=alt.Axis(labelAngle=0)),
#        y=alt.Y('average_days_to_close:Q',title=""),
#        color=alt.Color('deal_stage:N', scale=color_scale),
#        tooltip=['quarter_year', 'average_value', 'deal_stage']
#    )
#    st.altair_chart(days_chart, use_container_width=True)
