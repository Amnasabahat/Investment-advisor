import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Function to fetch financial data for a stock symbol
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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }

            # Make the request with headers
            response = requests.get(url, headers=headers)
            data[key] = pd.read_html(response.text)[0]
            # Clean the data
            data[key].columns = data[key].columns.droplevel(1)  # Dropping second-level header
            data[key] = data[key].T  # Transpose
            data[key].columns = data[key].iloc[0]  # Set first row as columns
            data[key] = data[key][1:]  # Drop first row

            # Handle percent columns and other cleaning
            percent_columns = [col for col in data[key].columns if data[key][col].astype(object).str.contains('%').any()]
            data[key].rename(columns={col: f"{col} (%)" for col in percent_columns}, inplace=True)
            data[key].replace('-', '0', inplace=True)  # Replace '-' with '0'
            data[key] = data[key].replace('%', '', regex=True)  # Remove '%'
            data[key] = data[key].astype(float)  # Convert to numeric
            data[key]['Year'] = ['TTM', '2024', '2023', '2022', '2021', '2020']  # Add 'Year' column
        except Exception as e:
            st.error(f"Error retrieving data from {url}: {e}")

    return data

# Streamlit UI elements
st.title("Stock Financial Data Viewer")

# Stock Symbol Input
stock_symbol = st.text_input("Enter Stock Symbol:", value="PSX")

if stock_symbol:
    data = get_financial_data(stock_symbol)

    # Let the user select which financial data to visualize
    financial_type = st.selectbox("Select Financial Data Type", ["income_statement", "balance_sheet", "cash_flow", "ratios"])

    # Display the selected financial data
    st.write(f"Showing data for: {financial_type}")
    st.dataframe(data[financial_type])

    # Financial Metrics for plotting
    if financial_type == 'income_statement':
        metrics = ['Revenue', 'Revenue Growth (YoY) (%)', 'Gross Margin (%)', 'Operating Margin (%)', 'Profit Margin (%)', 'Interest Expense']
    elif financial_type == 'balance_sheet':
        metrics = ['Cash & Equivalents', 'Property, Plant & Equipment', 'Long-Term Debt', 'Retained Earnings', 'Book Value Per Share']
    elif financial_type == 'cash_flow':
        metrics = ['Free Cash Flow', 'Free Cash Flow Per Share']
    elif financial_type == 'ratios':
        metrics = ['Debt / Equity Ratio', 'Current Ratio', 'Return on Equity (ROE) (%)', 'Return on Assets (ROA) (%)', 'Return on Capital (ROIC) (%)']

    # Let the user select which metric to plot
    metric = st.selectbox("Select Metric to Plot", metrics)

    if metric in data[financial_type].columns:
        # Plot the data for the selected metric
        st.write(f"Plotting {metric} over Years")
        fig, ax = plt.subplots()
        sns.barplot(data=data[financial_type], x='Year', y=metric, ax=ax)
        plt.title(f"{metric} over Years")
        plt.xlabel('Year')
        plt.ylabel(metric)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

# Additional sections for financial models

# Gordon Growth Model
st.header("Gordon Growth Model (Dividend Discount Model)")

D1 = st.number_input("Enter next year's dividend (D1):", min_value=0.0, value=2.0)
r = st.number_input("Enter required rate of return (r):", min_value=0.0, value=0.08)
g = st.number_input("Enter growth rate (g):", min_value=0.0, value=0.05)

if r > g:
    ggm_valuation = D1 / (r - g)
    st.write(f"Estimated stock value using Gordon Growth Model: ${ggm_valuation:.2f}")
else:
    st.error("Required return must be greater than the growth rate.")

# Discounted Cash Flow Model
st.header("Discounted Cash Flow (DCF) Valuation")

recent_free_cash_flow = st.number_input("Enter recent free cash flow:", min_value=0.0, value=5.0)
growth_rate = st.number_input("Enter expected growth rate of cash flow:", min_value=0.0, value=0.05)
discount_rate = st.number_input("Enter discount rate:", min_value=0.0, value=0.08)

projected_cash_flows = []
for year in range(1, 6):
    future_cash_flow = recent_free_cash_flow * ((1 + growth_rate) ** year)
    present_value = future_cash_flow / ((1 + discount_rate) ** year)
    projected_cash_flows.append(present_value)

fair_value = sum(projected_cash_flows)
st.write(f"Fair Value of the Stock (DCF): ${fair_value:.2f}")

# PEG Ratio Calculation
st.header("PEG Ratio")

pe_ratio = st.number_input("Enter Price-to-Earnings (P/E) ratio:", min_value=0.0, value=15.0)
growth_rate_peg = st.number_input("Enter expected growth rate (g) for PEG:", min_value=0.0, value=0.05)

if growth_rate_peg != 0:
    peg = pe_ratio / growth_rate_peg
    st.write(f"PEG Ratio: {peg:.2f}")
else:
    st.error("Growth rate cannot be zero.")

