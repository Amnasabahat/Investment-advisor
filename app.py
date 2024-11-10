import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import StringIO  # Import StringIO from io module

# Function to fetch financial data
def get_financial_data(stock_symbol):
    urls = {
        "income_statement": f"https://stockanalysis.com/quote/psx/{stock_symbol}/financials/",
        "balance_sheet": f"https://stockanalysis.com/quote/psx/{stock_symbol}/financials/balance-sheet/",
        "cash_flow": f"https://stockanalysis.com/quote/psx/{stock_symbol}/financials/cash-flow-statement/",
        "ratios": f"https://stockanalysis.com/quote/psx/{stock_symbol}/financials/ratios/"
    }

    data = {}

    for key, url in urls.items():
        try:
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }

            # Make the request with headers
            response = requests.get(url, headers=headers)
            # Wrap the HTML response in StringIO and read it
            html_content = StringIO(response.text)
            data[key] = pd.read_html(html_content, header=0)[0]  # Read the first table
            # Clean the DataFrame
            data[key].columns = data[key].columns.droplevel(1)
            data[key] = data[key].T
            data[key].columns = data[key].iloc[0]
            data[key] = data[key][1:]
            data[key].replace('-', '0', inplace=True)
            data[key] = data[key].astype(float)
            data[key]['Year'] = ['TTM', '2024', '2023', '2022', '2021', '2020']
        except Exception as e:
            st.error(f"Error retrieving data from {url}: {e}")

    return data

# Function to plot the data
def plot_dataframe(data):
    # Define the metrics for plotting
    income_metrics = ['Revenue', 'Revenue Growth (YoY) (%)', 'Gross Margin (%)', 'Operating Margin (%)', 'Profit Margin (%)', 'Interest Expense']
    balance_metrics = ['Cash & Equivalents', 'Property, Plant & Equipment', 'Long-Term Debt', 'Retained Earnings', 'Book Value Per Share']
    cash_metrics = ['Free Cash Flow', 'Free Cash Flow Per Share']
    ratio_metrics = ['Debt / Equity Ratio', 'Current Ratio', 'Return on Equity (ROE) (%)', 'Return on Assets (ROA) (%)', 'Return on Capital (ROIC) (%)']

    for key, df in data.items():
        if key == 'income_statement':
            for metric in income_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    st.bar_chart(df.set_index('Year')[metric])
        if key == 'balance_sheet':
            for metric in balance_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    st.bar_chart(df.set_index('Year')[metric])
        if key == 'cash_flow':
            for metric in cash_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    st.bar_chart(df.set_index('Year')[metric])
        if key == 'ratios':
            for metric in ratio_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    st.bar_chart(df.set_index('Year')[metric])

# Streamlit UI Setup
st.title("Stock Financial Data Viewer")

# Input field for Stock Symbol
stock_symbol = st.text_input("Enter Stock Symbol:", "PSX")

# Button to fetch financial data
if st.button("Fetch Financial Data"):
    if stock_symbol:
        # Fetch financial data for the given stock symbol
        data = get_financial_data(stock_symbol)

        # Display fetched data in table format for each category
        financial_type = st.selectbox("Select Financial Data Type", ["income_statement", "balance_sheet", "cash_flow", "ratios"])
        
        if financial_type in data:
            st.subheader(f"{financial_type.replace('_', ' ').title()} Data")
            st.dataframe(data[financial_type])

        # Plot graphs based on the selected financial data type
        plot_dataframe(data)

    else:
        st.warning("Please enter a valid stock symbol.")
