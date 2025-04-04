import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def format_currency(value):
    return "₹{:,.2f}".format(value).replace(",", "~").replace("~", ",")

@st.cache_data
def parse_currency(value):
    return float(value.replace("₹", "").replace(",", ""))

@st.cache_data
def mba_roi_calculator(total_fees, pre_mba_salary, post_mba_salary, duration, living_expenses=0, scholarship=0, loan_interest=0, salary_growth=0, post_mba_growth=0, loan_term=10):
    total_cost = total_fees + (living_expenses * duration) - scholarship
    opportunity_cost = sum(pre_mba_salary * ((1 + salary_growth) ** year) for year in range(1, duration + 1))
    total_investment = total_cost + opportunity_cost
    
    monthly_interest_rate = loan_interest / (12 * 100)
    months = loan_term * 12
    emi = (total_cost * monthly_interest_rate * (1 + monthly_interest_rate) ** months) / ((1 + monthly_interest_rate) ** months - 1)
    total_loan_repayment = emi * months
    
    cumulative_diff = 0
    break_even_years = float('inf')
    for year in range(1, 51):
        pre_salary = pre_mba_salary * ((1 + salary_growth) ** (year + duration))
        post_salary = post_mba_salary * ((1 + post_mba_growth) ** year)
        annual_diff = post_salary - pre_salary - (emi * 12 if year <= loan_term else 0)
        cumulative_diff += annual_diff
        if cumulative_diff >= total_investment and break_even_years == float('inf'):
            break_even_years = year + duration
    
    total_post_mba_earnings = sum(post_mba_salary * ((1 + post_mba_growth) ** year) for year in range(1, loan_term + 1))
    total_pre_mba_earnings = sum(pre_mba_salary * ((1 + salary_growth) ** (year + duration)) for year in range(loan_term))
    net_gain = (total_post_mba_earnings - total_pre_mba_earnings - total_loan_repayment) / loan_term
    roi_percentage = (net_gain / total_investment) * 100
    
    return {
        "Total Fees": format_currency(total_cost),
        "Opportunity Cost": format_currency(opportunity_cost),
        "Monthly EMI": format_currency(emi),
        "Total Loan Repayment": format_currency(total_loan_repayment),
        "Total Investment": format_currency(total_investment),
        "Break-even Years": round(break_even_years, 2) if break_even_years < 50 else "Not Achievable",
        "ROI Percentage": f"{roi_percentage:.2f}%"
    }

def display_dashboard():
    st.set_page_config(page_title="MBA ROI Calculator", layout="wide")
    st.markdown("<h1 style='text-align: center; font-size: 55px; margin-bottom: 10px;'>📊 MBA ROI Calculator</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📌 Input Parameters")
        total_fees = st.text_input("Total Fees (₹)", value="21,50,000")
        pre_mba_salary = st.text_input("Pre-MBA Salary (₹)", value="11,00,000")
        post_mba_salary = st.text_input("Post-MBA Salary (₹)", value="16,00,000")
        duration = st.number_input("Program Duration (years)", value=2, step=1)
        living_expenses = st.text_input("Living Expenses per Year (₹)", value="2,00,000")
        loan_interest = st.number_input("Loan Interest Rate (%)", value=8.7, step=0.1)
        salary_growth = st.number_input("Pre-MBA Salary Growth Rate (%)", value=10, step=1) / 100
        post_mba_growth = st.number_input("Post-MBA Salary Growth Rate (%)", value=15, step=1) / 100
        loan_term = st.number_input("Loan Repayment Term (years)", value=10, step=1)
    
    results = mba_roi_calculator(parse_currency(total_fees), parse_currency(pre_mba_salary), parse_currency(post_mba_salary), duration, parse_currency(living_expenses), loan_interest=loan_interest, salary_growth=salary_growth, post_mba_growth=post_mba_growth, loan_term=loan_term)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h2 style='text-align: left; font-size: 35px;'>📌 ROI Breakdown</h2>", unsafe_allow_html=True)
        for key, value in results.items():
            st.metric(label=key, value=value)
    
    with col2:
        years = list(range(1, loan_term + 1))
        pre_mba_salaries = [parse_currency(pre_mba_salary) * ((1 + salary_growth) ** (year + duration)) for year in years]
        post_mba_salaries = [parse_currency(post_mba_salary) * ((1 + post_mba_growth) ** year) for year in years]
        
        df = pd.DataFrame({"Years": years, "Pre-MBA Salary": pre_mba_salaries, "Post-MBA Salary": post_mba_salaries})
        st.markdown("<br>", unsafe_allow_html=True)
        st.line_chart(df.set_index("Years"), use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-size: 26px;'>📌 Loan Repayment & Salary Projection</h2>", unsafe_allow_html=True)
    
    emi = float(results["Monthly EMI"].replace("₹", "").replace(",", ""))
    total_cost = parse_currency(total_fees) + parse_currency(living_expenses) * duration
    monthly_interest_rate = loan_interest / (12 * 100)
    remaining_loan = total_cost
    df_detail = []
    
    for i in years:
        interest_payment = remaining_loan * monthly_interest_rate * 12
        principal_payment = min(emi * 12 - interest_payment, remaining_loan)
        loan_paid = principal_payment + interest_payment
        remaining_loan -= principal_payment
        df_detail.append([i, format_currency(loan_paid), format_currency(total_cost - remaining_loan), format_currency(remaining_loan), format_currency(pre_mba_salaries[i-1]), format_currency(post_mba_salaries[i-1])])
    
    if remaining_loan > 0:
        final_interest = remaining_loan * monthly_interest_rate * 12
        final_payment = remaining_loan + final_interest
        df_detail[-1][1] = format_currency(final_payment)
        df_detail[-1][2] = format_currency(total_cost)  # Correctly indented
        df_detail[-1][3] = format_currency(0)
    
    df_detail = pd.DataFrame(df_detail, columns=["Year", "Loan Paid", "Cumulative Loan Paid", "Remaining Loan", "Pre-MBA Salary", "Post-MBA Salary"])
    st.dataframe(df_detail.style.hide(axis='index'), use_container_width=True)

if __name__ == "__main__":
    display_dashboard()
