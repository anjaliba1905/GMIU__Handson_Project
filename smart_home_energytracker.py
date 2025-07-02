import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import os
from pathlib import Path
import numpy as np

# Page configuration
st.set_page_config(
    page_title="🏠 Home Energy Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    .energy-tip {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
    }
    .warning-box {
        background: linear-gradient(90deg, #ff6b6b 0%, #ffa726 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# File name
CSV_FILE = "home_energy_consumption.csv"

# Functions
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            'User','Date', 'Day', 'AC_Usage', 'Fridge_Usage', 'Washing_Machine_Usage', 
            'Solar_Usage', 'Total_Consumption', 'Home_Type', 'Family_Size', 
            'Outside_Temperature', 'Usage_Duration_Hours'
        ])
        df.to_csv(CSV_FILE, index=False)

def save_to_csv(data):
    df = pd.read_csv(CSV_FILE)
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame()

def calculate_consumption(ac_use, fridge_use, wm_use, solar_use, home_type, family_size, temp, duration):
    base_consumption = 0
    home_multipliers = {"1BHK": 1.0, "2BHK": 1.5, "3BHK": 2.0, "4BHK+": 2.5}
    base_consumption += home_multipliers.get(home_type, 1.0) * 2
    base_consumption += family_size * 0.5

    if ac_use:
        ac_consumption = 3 + (max(0, temp - 25) * 0.2)
        base_consumption += ac_consumption
    if fridge_use:
        fridge_consumption = 2 + (max(0, temp - 20) * 0.1)
        base_consumption += fridge_consumption
    if wm_use:
        base_consumption += 4
    if solar_use:
        base_consumption -= min(base_consumption * 0.6, 10)

    base_consumption *= (duration / 8)
    return max(0, round(base_consumption, 2))

def get_energy_tips(consumption):
    if consumption > 15:
        return "🚨 High consumption! Consider using solar panels, LED bulbs, and energy-efficient appliances."
    elif consumption > 10:
        return "⚠️ Moderate consumption. Try to use AC wisely and unplug unused devices."
    else:
        return "✅ Great job! You're maintaining low energy consumption."

def create_consumption_chart(df):
    if df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['Total_Consumption'],
        mode='lines+markers',
        name='Energy Consumption',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2')
    ))
    avg_consumption = df['Total_Consumption'].mean()
    fig.add_hline(y=avg_consumption, line_dash="dash", 
                  annotation_text=f"Average: {avg_consumption:.1f} kWh",
                  line_color="red")
    fig.update_layout(
        title="📈 Energy Consumption Trend",
        xaxis_title="Date",
        yaxis_title="Energy Consumption (kWh)",
        template="plotly_white",
        height=400
    )
    return fig

def create_appliance_usage_chart(df):
    if df.empty:
        return None
    appliances = ['AC_Usage', 'Fridge_Usage', 'Washing_Machine_Usage', 'Solar_Usage']
    usage_counts = df[appliances].sum()
    fig = px.pie(
        values=usage_counts.values,
        names=['🌡️ AC', '❄️ Fridge', '👕 Washing Machine', '☀️ Solar'],
        title="🔌 Appliance Usage Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def main():
    initialize_csv()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏠 Smart Home Energy Consumption Tracker ⚡</h1>
        <p>Monitor, Analyze, and Optimize Your Home's Energy Daily Usage</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Inputs
    with st.sidebar:
        st.header("📝 Daily Energy Log")
        st.write("Track your daily energy consumption")
        user_name = st.sidebar.text_input("👤 Enter Your Name")

        selected_date = st.date_input("📅 Select Date", datetime.date.today())
        day_of_week = selected_date.strftime("%A")
        st.write(f"📆 Day: **{day_of_week}**")

        st.subheader("🏠 Home Information")
        home_type = st.selectbox("🏠 Home Type", ["1BHK", "2BHK", "3BHK", "4BHK+"])
        family_size = st.slider("👥 Family Size", 1, 10, 4)

        st.subheader("🌡️ Environmental Factors")
        outside_temp = st.slider("🌡️ Outside Temperature (°C)", 15, 45, 30)
        usage_duration = st.slider("⏰ Usage Duration (hours)", 1, 24, 8)

        st.subheader("🔌 Appliance Usage Today")
        col1, col2 = st.columns(2)
        with col1:
            ac_use = st.checkbox("🌡️ AC")
            fridge_use = st.checkbox("❄️ Fridge")
        with col2:
            wm_use = st.checkbox("👕 Washing Machine")
            solar_use = st.checkbox("☀️ Solar Panels")

        consumption = calculate_consumption(
            ac_use, fridge_use, wm_use, solar_use, 
            home_type, family_size, outside_temp, usage_duration
        )

        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: white; margin-bottom: 0;">⚡ Today's Consumption</h3>
            <h2 style="color: #FFD700; margin-top: 0;">{consumption} kWh</h2>
        </div>
        """, unsafe_allow_html=True)

        tip = get_energy_tips(consumption)
        st.markdown(f'<div class="energy-tip">💡 {tip}</div>', unsafe_allow_html=True)

        if st.button("💾 Save Today's Data", type="primary"):
            data = {
                'User': user_name,
                'Date': selected_date.strftime("%Y-%m-%d"),
                'Day': day_of_week,
                'AC_Usage': ac_use,
                'Fridge_Usage': fridge_use,
                'Washing_Machine_Usage': wm_use,
                'Solar_Usage': solar_use,
                'Total_Consumption': consumption,
                'Home_Type': home_type,
                'Family_Size': family_size,
                'Outside_Temperature': outside_temp,
                'Usage_Duration_Hours': usage_duration
            }
            save_to_csv(data)
            st.success("✅ Data saved successfully!")

    # Personalized greeting (moved inside main function)
    if user_name:
        st.markdown(f"### 👋 Welcome, **{user_name}**! Here's your energy dashboard.")

    # Main content
    df = load_data()

    if not df.empty:
        st.subheader("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_consumption = df['Total_Consumption'].mean()
            st.metric("🔥 Average Daily Consumption", f"{avg_consumption:.1f} kWh")
        with col2:
            total_consumption = df['Total_Consumption'].sum()
            st.metric("⚡ Total Consumption", f"{total_consumption:.1f} kWh")
        with col3:
            max_consumption = df['Total_Consumption'].max()
            st.metric("📈 Peak Consumption", f"{max_consumption:.1f} kWh")
        with col4:
            days_tracked = len(df)
            st.metric("📅 Days Tracked", f"{days_tracked}")

        col1, col2 = st.columns(2)
        with col1:
            chart = create_consumption_chart(df)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        with col2:
            pie = create_appliance_usage_chart(df)
            if pie:
                st.plotly_chart(pie, use_container_width=True)

        st.subheader("📈 Detailed Analysis")
        if len(df) >= 7:
            df['Date'] = pd.to_datetime(df['Date'])
            weekly_avg = df.groupby(df['Date'].dt.day_name())['Total_Consumption'].mean().round(2)
            fig = px.bar(
                x=weekly_avg.index,
                y=weekly_avg.values,
                title="📅 Average Consumption by Day of Week",
                labels={'x': 'Day of Week', 'y': 'Average Consumption (kWh)'},
                color=weekly_avg.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

        if len(df) > 5:
            fig = px.scatter(
                df, 
                x='Outside_Temperature', 
                y='Total_Consumption',
                size='Family_Size',
                color='Home_Type',
                title="🌡️ Temperature vs Energy Consumption",
                labels={'Outside_Temperature': 'Temperature (°C)', 'Total_Consumption': 'Consumption (kWh)'}
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("💰 Cost Analysis")
        electricity_rate = st.slider("⚡ Electricity Rate (₹/kWh)", 3.0, 10.0, 6.0)
        daily_cost = df['Total_Consumption'] * electricity_rate
        monthly_cost = daily_cost.sum() * (30 / len(df))
        yearly_cost = monthly_cost * 12
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Daily Avg Cost", f"₹{daily_cost.mean():.2f}")
        with col2:
            st.metric("💳 Est. Monthly Cost", f"₹{monthly_cost:.2f}")
        with col3:
            st.metric("💰 Est. Yearly Cost", f"₹{yearly_cost:.2f}")

        st.subheader("📋 Historical Data")
        if st.checkbox("Show Raw Data"):
            st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"energy_consumption_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("📝 No data available yet. Please add your first entry using the sidebar!")
        st.subheader("📊 Sample Dashboard Preview")
        sample_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        sample_data = {
            'Date': sample_dates,
            'Total_Consumption': np.random.normal(12, 3, 30),
            'AC_Usage': np.random.choice([True, False], 30),
            'Fridge_Usage': [True] * 30,
            'Washing_Machine_Usage': np.random.choice([True, False], 30),
            'Solar_Usage': np.random.choice([True, False], 30)
        }
        sample_df = pd.DataFrame(sample_data)
        chart = create_consumption_chart(sample_df)
        if chart:
            st.plotly_chart(chart, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌱 <strong>Go Green!</strong> Track your energy consumption and save the planet! 🌍</p>
        <p>Made with ❤️ using Streamlit | 🔋 Energy Tracker v2.0</p>
    </div>
    """, unsafe_allow_html=True)

# Run main
if __name__ == "__main__":
    main()
