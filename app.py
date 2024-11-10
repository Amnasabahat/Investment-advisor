import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def get_financial_data(stock_symbol):
    # URLs to scrape data from
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
            # Use lxml for parsing HTML tables
            data[key] = pd.read_html(response.text, header=0)[0]  # Read the first table

            # Data processing steps to clean up the data
            data[key].columns = data[key].columns.droplevel(1)  # Dropping extra header levels
            data[key] = data[key].T  # Transpose the dataframe
            data[key].columns = data[key].iloc[0]  # Set first row as column names
            data[key] = data[key][1:]  # Remove the first row which was used as column names

            # Cleaning data: Replace '-' with '0' and convert percentage columns
            data[key].replace('-', '0', inplace=True)
            data[key] = data[key].apply(pd.to_numeric, errors='coerce')

            # Add a 'Year' column for display purposes
            data[key]['Year'] = ['TTM', '2024', '2023', '2022', '2021', '2020']
        except Exception as e:
            st.error(f"Error retrieving data from {url}: {e}")
    
    return data

def plot_dataframe(data):
    # Predefined metrics for plotting
    income_metrics = ['Revenue', 'Revenue Growth (YoY) (%)', 'Gross Margin (%)', 'Operating Margin (%)', 'Profit Margin (%)', 'Interest Expense']
    balance_metrics = ['Cash & Equivalents', 'Property, Plant & Equipment', 'Long-Term Debt', 'Retained Earnings', 'Book Value Per Share']
    cash_metrics = ['Free Cash Flow', 'Free Cash Flow Per Share']
    ratio_metrics = ['Debt / Equity Ratio', 'Current Ratio', 'Return on Equity (ROE) (%)', 'Return on Assets (ROA) (%)', 'Return on Capital (ROIC) (%)']

    # Iterate through the data for plotting
    for key, df in data.items():
        st.write(f"Available columns in {key}: {df.columns.tolist()}")
        if key == 'income_statement':
            for metric in income_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)
        if key == 'balance_sheet':
            for metric in balance_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)
        if key == 'cash_flow':
            for metric in cash_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)
        if key == 'ratios':
            for metric in ratio_metrics:
                if metric in df.columns:
                    st.subheader(f"{metric} over Years")
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)

# Streamlit UI Elements
st.title("Stock Financial Data Viewer")
stock_symbol = st.text_input("Enter Stock Symbol:", "PSX")

if stock_symbol:
    data = get_financial_data(stock_symbol)
    if data:
        st.subheader(f"Showing data for: {stock_symbol}")
        # Allow user to select the type of financial data to display
        financial_type = st.selectbox("Select Financial Data Type", ['income_statement', 'balance_sheet', 'cash_flow', 'ratios'])
        if financial_type in data:
            st.dataframe(data[financial_type])
            plot_dataframe(data)
    else:
        st.error("No data found. Please check the stock symbol or try again later.")
