import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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
            
            # Read HTML tables (the first table in the response)
            data[key] = pd.read_html(response.text, header=0)[0]  # Read the first table
            
            # Cleaning the data
            data[key].columns = data[key].columns.droplevel(1)  # Remove multi-level columns
            data[key] = data[key].T  # Transpose to make the years as rows
            data[key].columns = data[key].iloc[0]  # Set the first row as column names
            data[key] = data[key][1:]  # Drop the first row (used as columns now)
            data[key] = data[key].astype(float)  # Convert all data to float
            data[key]['Year'] = ['TTM', '2024', '2023', '2022', '2021', '2020']  # Add years
        except Exception as e:
            print(f"Error retrieving data from {url}: {e}")
    
    return data

# Function to plot data
def plot_dataframe(data):
    # Define the financial metrics for each category
    income_metrics = ['Revenue', 'Revenue Growth (YoY) (%)', 'Gross Margin (%)', 'Operating Margin (%)', 'Profit Margin (%)', 'Interest Expense']
    balance_metrics = ['Cash & Equivalents', 'Property, Plant & Equipment', 'Long-Term Debt', 'Retained Earnings', 'Book Value Per Share']
    cash_metrics = ['Free Cash Flow', 'Free Cash Flow Per Share']
    ratio_metrics = ['Debt / Equity Ratio', 'Current Ratio', 'Return on Equity (ROE) (%)', 'Return on Assets (ROA) (%)', 'Return on Capital (ROIC) (%)']
    
    for key, df in data.items():
        st.write(f"Available columns in {key}: {df.columns.tolist()}")
        
        # Plot for income statement
        if key == 'income_statement':
            for metric in income_metrics:
                if metric in df.columns:
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot()

        # Plot for balance sheet
        if key == 'balance_sheet':
            for metric in balance_metrics:
                if metric in df.columns:
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot()

        # Plot for cash flow
        if key == 'cash_flow':
            for metric in cash_metrics:
                if metric in df.columns:
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot()

        # Plot for ratios
        if key == 'ratios':
            for metric in ratio_metrics:
                if metric in df.columns:
                    sns.barplot(data=df, x='Year', y=metric)
                    plt.title(f"{metric} over Years")
                    plt.xlabel('Year')
                    plt.ylabel(metric)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot()

# Streamlit UI
st.title("Stock Financial Data Viewer")

# User input for stock symbol
stock_symbol = st.text_input("Enter Stock Symbol:")

if stock_symbol:
    # Fetch financial data for the entered stock symbol
    data = get_financial_data(stock_symbol)

    if data:
        st.write(f"Showing data for: {stock_symbol}")
        
        # Select financial data type (income_statement, balance_sheet, etc.)
        financial_type = st.selectbox("Select Financial Data Type", ['income_statement', 'balance_sheet', 'cash_flow', 'ratios'])

        if financial_type in data:
            st.dataframe(data[financial_type])  # Display the selected financial data type in a table

            # Plot the data
            plot_dataframe(data)
    else:
        st.write("No data found. Please check the stock symbol or try again later.")
