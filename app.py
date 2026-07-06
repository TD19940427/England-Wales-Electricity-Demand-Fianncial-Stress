import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from openai import OpenAI
import json

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Comprehensive Electricity Analytics Chatbot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stChatMessage {
        background-color: #ffffff;
    }
    .topic-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_all_data():
    """Load ALL exported data files"""
    try:
        data = {}
        
        # Core demand and forecast
        data['quarterly'] = pd.read_csv('data/26_PowerBI_Complete_2015_2035.csv')
        data['quarterly']['Quarter_End_Date'] = pd.to_datetime(data['quarterly']['Quarter_End_Date'])
        
        data['monthly'] = pd.read_csv('data/27_Monthly_Complete_2015_2035.csv')
        data['monthly']['Month'] = pd.to_datetime(data['monthly']['Month'])
        
        data['yearly'] = pd.read_csv('data/23_Yearly_Historical_and_Forecast_Combined.csv')
        
        # Detailed demand data (historical)
        data['hourly'] = pd.read_csv('data/01_Hourly_Demand.csv')
        data['hourly']['DateTime'] = pd.to_datetime(data['hourly']['DateTime'])
        
        data['daily'] = pd.read_csv('data/02_Daily_Demand.csv')
        data['daily']['Date'] = pd.to_datetime(data['daily']['Date'])
        
        data['monthly_detail'] = pd.read_csv('data/04_Monthly_Demand.csv')
        data['monthly_detail']['Month'] = pd.to_datetime(data['monthly_detail']['Month'])
        
        # Patterns
        data['hourly_pattern'] = pd.read_csv('data/15a_Hourly_Pattern.csv')
        data['weekday_pattern'] = pd.read_csv('data/15b_Weekday_Pattern.csv')
        data['weekend_comparison'] = pd.read_csv('data/15c_Weekend_Comparison.csv')
        data['seasonal_pattern'] = pd.read_csv('data/15d_Seasonal_Pattern.csv')
        
        # Weather impact
        data['temperature_bins'] = pd.read_csv('data/14a_Temperature_Bins.csv')
        data['rainfall_bins'] = pd.read_csv('data/14b_Rainfall_Bins.csv')
        
        # Financial
        data['tariff'] = pd.read_csv('data/10_Quarterly_Tariff_EnglandWales.csv')
        data['tariff']['Quarter_End_Date'] = pd.to_datetime(data['tariff']['Quarter_End_Date'])
        
        data['arrears'] = pd.read_csv('data/11_Quarterly_Arrears_Debt.csv')
        data['arrears']['Quarter_End_Date'] = pd.to_datetime(data['arrears']['Quarter_End_Date'])
        
        data['financial_stress'] = pd.read_csv('data/12_Financial_Stress_Index.csv')
        data['financial_stress']['Quarter_End_Date'] = pd.to_datetime(data['financial_stress']['Quarter_End_Date'])
        
        # Data dictionary
        data['dictionary'] = pd.read_csv('data/00_DATA_DICTIONARY.csv')
        
        return data
        
    except FileNotFoundError as e:
        st.error(f"⚠️ Data file not found: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        return None

# ============================================================
# COMPREHENSIVE ANALYSIS FUNCTIONS
# ============================================================
def get_comprehensive_stats(data):
    """Get statistics across all dimensions"""
    
    stats = {}
    
    # Demand trends
    quarterly = data['quarterly']
    historical = quarterly[quarterly['Data_Type'].str.contains('Historical', na=False)]
    forecast = quarterly[quarterly['Data_Type'].str.contains('Forecast', na=False)]
    
    stats['demand'] = {
        'historical_avg': historical['Demand_MW'].mean(),
        'forecast_avg': forecast['Demand_MW'].mean(),
        'historical_min': historical['Demand_MW'].min(),
        'historical_max': historical['Demand_MW'].max(),
        'forecast_min': forecast['Demand_MW'].min(),
        'forecast_max': forecast['Demand_MW'].max(),
        'trend_change': ((forecast['Demand_MW'].mean() / historical['Demand_MW'].mean()) - 1) * 100
    }
    
    # Seasonal patterns
    seasonal = data['seasonal_pattern']
    stats['seasonal'] = {
        'winter_avg': seasonal[seasonal['Season'] == 'Winter']['Avg_Demand_MW'].values[0] if len(seasonal[seasonal['Season'] == 'Winter']) > 0 else 0,
        'summer_avg': seasonal[seasonal['Season'] == 'Summer']['Avg_Demand_MW'].values[0] if len(seasonal[seasonal['Season'] == 'Summer']) > 0 else 0,
        'spring_avg': seasonal[seasonal['Season'] == 'Spring']['Avg_Demand_MW'].values[0] if len(seasonal[seasonal['Season'] == 'Spring']) > 0 else 0,
        'autumn_avg': seasonal[seasonal['Season'] == 'Autumn']['Avg_Demand_MW'].values[0] if len(seasonal[seasonal['Season'] == 'Autumn']) > 0 else 0,
    }
    stats['seasonal']['peak_season'] = max(stats['seasonal'], key=stats['seasonal'].get).replace('_avg', '').capitalize()
    
    # Weekday vs Weekend
    weekend_comp = data['weekend_comparison']
    stats['weekend'] = {
        'weekday_avg': weekend_comp[weekend_comp['Is_Weekend'] == 0]['Avg_Demand_MW'].values[0],
        'weekend_avg': weekend_comp[weekend_comp['Is_Weekend'] == 1]['Avg_Demand_MW'].values[0],
    }
    stats['weekend']['difference_pct'] = ((stats['weekend']['weekend_avg'] / stats['weekend']['weekday_avg']) - 1) * 100
    
    # Weather impact
    temp_bins = data['temperature_bins']
    stats['weather'] = {
        'temp_coldest_demand': temp_bins['Avg_Demand_MW'].max(),
        'temp_warmest_demand': temp_bins['Avg_Demand_MW'].min(),
        'temp_range': temp_bins['Temperature_Bin'].iloc[0] + ' to ' + temp_bins['Temperature_Bin'].iloc[-1]
    }
    
    # Financial
    tariff = data['tariff']
    arrears = data['arrears']
    fsi = data['financial_stress']
    
    stats['financial'] = {
        'avg_tariff': tariff['Quarterly_Price_per_kWh'].mean(),
        'min_tariff': tariff['Quarterly_Price_per_kWh'].min(),
        'max_tariff': tariff['Quarterly_Price_per_kWh'].max(),
        'total_arrears': arrears['Arrears_Billions_GBP'].sum(),
        'avg_fsi': fsi['Financial_Stress_Index'].mean(),
        'crisis_quarters': fsi['Is_Crisis_Period'].sum()
    }
    
    return stats

# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================
def create_demand_forecast_chart(data):
    """Demand historical vs forecast"""
    df = data['quarterly']
    
    fig = go.Figure()
    
    historical = df[df['Data_Type'].str.contains('Historical', na=False)]
    forecast = df[df['Data_Type'].str.contains('Forecast', na=False)]
    
    fig.add_trace(go.Scatter(
        x=historical['Quarter_End_Date'],
        y=historical['Demand_MW'],
        mode='lines+markers',
        name='Historical (2015-2025)',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast['Quarter_End_Date'],
        y=forecast['Demand_MW'],
        mode='lines+markers',
        name='Forecast (2026-2035)',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Electricity Demand: Historical vs Forecast',
        xaxis_title='Time',
        yaxis_title='Demand (MW)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_seasonal_chart(data):
    """Seasonal demand patterns"""
    df = data['seasonal_pattern']
    
    fig = px.bar(
        df,
        x='Season',
        y='Avg_Demand_MW',
        error_y='Std_Demand_MW',
        title='Seasonal Demand Patterns',
        labels={'Avg_Demand_MW': 'Average Demand (MW)', 'Season': 'Season'},
        color='Season',
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=400
    )
    
    return fig

def create_weekday_chart(data):
    """Weekday vs weekend comparison"""
    df = data['weekday_pattern']
    
    fig = px.bar(
        df,
        x='Day_Name',
        y='Avg_Demand_MW',
        error_y='Std_Demand_MW',
        title='Demand by Day of Week',
        labels={'Avg_Demand_MW': 'Average Demand (MW)', 'Day_Name': 'Day'},
        color='Avg_Demand_MW',
        color_continuous_scale='Blues',
        height=400
    )
    
    return fig

def create_hourly_pattern_chart(data):
    """Hourly demand pattern"""
    df = data['hourly_pattern']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Hour'],
        y=df['Avg_Demand_MW'],
        mode='lines+markers',
        name='Average Demand',
        line=dict(color='#1f77b4', width=2),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='24-Hour Demand Pattern',
        xaxis_title='Hour of Day',
        yaxis_title='Average Demand (MW)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_weather_impact_chart(data):
    """Temperature impact on demand"""
    df = data['temperature_bins']
    
    fig = px.bar(
        df,
        x='Temperature_Bin',
        y='Avg_Demand_MW',
        error_y='Std_Demand_MW',
        title='Demand vs Temperature',
        labels={'Avg_Demand_MW': 'Average Demand (MW)', 'Temperature_Bin': 'Temperature Range (°C)'},
        color='Avg_Demand_MW',
        color_continuous_scale='RdYlBu_r',
        height=400
    )
    
    return fig

def create_financial_stress_chart(data):
    """Financial stress index over time"""
    df = data['financial_stress']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Quarter_End_Date'],
        y=df['Financial_Stress_Index'],
        mode='lines+markers',
        name='Financial Stress Index',
        line=dict(color='#d62728', width=2),
        marker=dict(
            size=8,
            color=['red' if x == 1 else 'blue' for x in df['Is_Crisis_Period']],
        )
    ))
    
    fig.update_layout(
        title='Financial Stress Index Over Time',
        xaxis_title='Quarter',
        yaxis_title='Financial Stress Index',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_tariff_arrears_chart(data):
    """Tariff vs arrears"""
    tariff = data['tariff']
    arrears = data['arrears']
    
    # Merge datasets
    merged = pd.merge(tariff, arrears, on='Quarter_End_Date', how='inner')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=merged['Quarter_End_Date'],
        y=merged['Quarterly_Price_per_kWh'],
        mode='lines+markers',
        name='Tariff (£/kWh)',
        yaxis='y',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=merged['Quarter_End_Date'],
        y=merged['Arrears_Billions_GBP'],
        mode='lines+markers',
        name='Arrears (£ Billions)',
        yaxis='y2',
        line=dict(color='#d62728', width=2)
    ))
    
    fig.update_layout(
        title='Electricity Tariff vs Arrears/Debt',
        xaxis_title='Quarter',
        yaxis=dict(title='Tariff (£/kWh)', titlefont=dict(color='#2ca02c')),
        yaxis2=dict(title='Arrears (£ Billions)', overlaying='y', side='right', titlefont=dict(color='#d62728')),
        template='plotly_white',
        height=400
    )
    
    return fig

# ============================================================
# COMPREHENSIVE CHATBOT
# ============================================================
def get_comprehensive_response(user_question, data, conversation_history, use_ai=False):
    """Comprehensive chatbot covering all topics"""
    
    question_lower = user_question.lower()
    stats = get_comprehensive_stats(data)
    
    # Check if using AI
    if use_ai and os.getenv('OPENAI_API_KEY'):
        return get_ai_response(user_question, data, stats, conversation_history)
    
    # Rule-based responses for all topics
    
    # === DEMAND QUESTIONS ===
    if 'historical' in question_lower and 'average' in question_lower and 'demand' in question_lower:
        return f"📊 The average historical electricity demand (2015-2025) was **{stats['demand']['historical_avg']:.2f} MW**."
    
    if 'forecast' in question_lower and ('average' in question_lower or '2030' in question_lower or 'future' in question_lower):
        return f"🔮 The average forecast electricity demand (2026-2035) is **{stats['demand']['forecast_avg']:.2f} MW**."
    
    if 'trend' in question_lower or ('demand' in question_lower and 'change' in question_lower):
        direction = "decrease" if stats['demand']['trend_change'] < 0 else "increase"
        return f"📈 The forecast shows a **{abs(stats['demand']['trend_change']):.2f}% {direction}** compared to historical average demand."
    
    # === SEASONAL QUESTIONS ===
    if 'season' in question_lower or 'winter' in question_lower or 'summer' in question_lower:
        return f"""❄️☀️ **Seasonal Demand Patterns:**
- Winter: {stats['seasonal']['winter_avg']:.2f} MW (highest)
- Spring: {stats['seasonal']['spring_avg']:.2f} MW
- Summer: {stats['seasonal']['summer_avg']:.2f} MW (lowest)
- Autumn: {stats['seasonal']['autumn_avg']:.2f} MW

**Peak Season:** {stats['seasonal']['peak_season']} has the highest demand."""
    
    # === WEEKDAY/WEEKEND QUESTIONS ===
    if 'weekday' in question_lower or 'weekend' in question_lower or 'week' in question_lower:
        return f"""📅 **Weekday vs Weekend Demand:**
- Weekday Average: {stats['weekend']['weekday_avg']:.2f} MW
- Weekend Average: {stats['weekend']['weekend_avg']:.2f} MW
- Difference: {stats['weekend']['difference_pct']:.2f}%

Weekend demand is {'lower' if stats['weekend']['difference_pct'] < 0 else 'higher'} than weekday demand."""
    
    # === WEATHER QUESTIONS ===
    if 'temperature' in question_lower or 'weather' in question_lower or 'cold' in question_lower or 'hot' in question_lower:
        return f"""🌡️ **Weather Impact on Demand:**
- Coldest conditions: {stats['weather']['temp_coldest_demand']:.2f} MW
- Warmest conditions: {stats['weather']['temp_warmest_demand']:.2f} MW
- Temperature range analyzed: {stats['weather']['temp_range']}

Demand is highest during cold weather (heating) and hot weather (cooling)."""
    
    if 'rainfall' in question_lower or 'rain' in question_lower:
        return "🌧️ Rainfall has minimal direct impact on electricity demand compared to temperature. However, it affects renewable generation (hydro, solar reduction)."
    
    # === FINANCIAL QUESTIONS ===
    if 'tariff' in question_lower or 'price' in question_lower or 'cost' in question_lower:
        return f"""💷 **Electricity Tariff Information:**
- Average Quarterly Tariff: £{stats['financial']['avg_tariff']:.4f}/kWh
- Minimum: £{stats['financial']['min_tariff']:.4f}/kWh
- Maximum: £{stats['financial']['max_tariff']:.4f}/kWh

Tariffs have varied significantly over the analysis period."""
    
    if 'arrear' in question_lower or 'debt' in question_lower:
        return f"""💳 **Customer Arrears & Debt:**
- Total Arrears (cumulative): £{stats['financial']['total_arrears']:.2f} billion
- Average per quarter: £{stats['financial']['total_arrears'] / len(data['arrears']):.2f} billion

Customer debt has accumulated over the period analyzed."""
    
    if 'financial stress' in question_lower or 'crisis' in question_lower or 'affordability' in question_lower:
        return f"""📉 **Financial Stress Index:**
- Average FSI: {stats['financial']['avg_fsi']:.2f}
- Crisis Periods Detected: {stats['financial']['crisis_quarters']} quarters

The Financial Stress Index combines demand, tariffs, and arrears to identify periods of customer financial difficulty."""
    
    # === COMPARISON QUESTIONS ===
    if 'compare' in question_lower or 'difference' in question_lower or 'vs' in question_lower:
        diff = stats['demand']['forecast_avg'] - stats['demand']['historical_avg']
        return f"""⚖️ **Comprehensive Comparison:**

**Demand:**
- Historical Average: {stats['demand']['historical_avg']:.2f} MW
- Forecast Average: {stats['demand']['forecast_avg']:.2f} MW
- Difference: {diff:.2f} MW ({stats['demand']['trend_change']:.2f}%)

**Seasonal:**
- Peak Season: {stats['seasonal']['peak_season']}
- Weekday vs Weekend: {stats['weekend']['difference_pct']:.2f}% difference

**Financial:**
- Average Tariff: £{stats['financial']['avg_tariff']:.4f}/kWh
- Total Arrears: £{stats['financial']['total_arrears']:.2f} billion"""
    
    # === PEAK DEMAND ===
    if 'peak' in question_lower or 'maximum' in question_lower or 'highest' in question_lower:
        return f"""⚡ **Peak Demand Analysis:**
- Historical Peak: {stats['demand']['historical_max']:.2f} MW
- Forecast Peak: {stats['demand']['forecast_max']:.2f} MW
- Peak Season: {stats['seasonal']['peak_season']}
- Peak Weather Condition: Cold temperatures drive highest demand"""
    
    # === MINIMUM DEMAND ===
    if 'minimum' in question_lower or 'lowest' in question_lower:
        return f"""📉 **Minimum Demand Analysis:**
- Historical Minimum: {stats['demand']['historical_min']:.2f} MW
- Forecast Minimum: {stats['demand']['forecast_min']:.2f} MW
- Lowest Season: Summer typically sees minimum demand"""
    
    # === DEFAULT COMPREHENSIVE RESPONSE ===
    return f"""I can help you with comprehensive electricity analytics across multiple dimensions:

**📊 Topics I Cover:**
✅ Demand (historical 2015-2025 & forecast 2026-2035)
✅ Seasonal patterns (Winter, Spring, Summer, Autumn)
✅ Weekday vs Weekend patterns
✅ Weather impact (Temperature, Rainfall)
✅ Financial metrics (Tariffs, Arrears, Debt)
✅ Financial Stress Index
✅ Hourly & daily patterns

**🎯 Quick Stats:**
- Historical Avg Demand: {stats['demand']['historical_avg']:.0f} MW
- Forecast Avg Demand: {stats['demand']['forecast_avg']:.0f} MW
- Peak Season: {stats['seasonal']['peak_season']}
- Avg Tariff: £{stats['financial']['avg_tariff']:.4f}/kWh
- Total Arrears: £{stats['financial']['total_arrears']:.1f}B

**💬 Try asking:**
- "What are the seasonal patterns?"
- "Compare weekday vs weekend demand"
- "How does temperature affect demand?"
- "What's the financial stress index?"
- "Show me tariff trends"
"""

def get_ai_response(user_question, data, stats, conversation_history):
    """AI-powered comprehensive response"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "⚠️ OpenAI API key not found."
    
    data_context = f"""
    You are an expert electricity analytics consultant with access to comprehensive UK electricity data (2015-2035).
    
    **Available Data Dimensions:**
    1. DEMAND: Historical (2015-2025) and forecast (2026-2035)
    2. SEASONAL: Winter, Spring, Summer, Autumn patterns
    3. TEMPORAL: Hourly patterns, weekday vs weekend
    4. WEATHER: Temperature and rainfall impact on demand
    5. FINANCIAL: Electricity tariffs, customer arrears/debt
    6. STRESS: Financial stress index tracking affordability crises
    
    **Key Statistics:**
    - Historical Avg Demand: {stats['demand']['historical_avg']:.2f} MW
    - Forecast Avg Demand: {stats['demand']['forecast_avg']:.2f} MW
    - Trend: {stats['demand']['trend_change']:.2f}%
    - Peak Season: {stats['seasonal']['peak_season']}
    - Weekday vs Weekend: {stats['weekend']['difference_pct']:.2f}% difference
    - Avg Tariff: £{stats['financial']['avg_tariff']:.4f}/kWh
    - Total Arrears: £{stats['financial']['total_arrears']:.2f} billion
    - Avg Financial Stress: {stats['financial']['avg_fsi']:.2f}
    
    Answer questions clearly and use specific numbers. Mention when charts are available in the sidebar.
    """
    
    try:
        client = OpenAI(api_key=api_key)
        
        messages = [{"role": "system", "content": data_context}]
        
        for msg in conversation_history:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_question})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ============================================================
# MAIN APP
# ============================================================
def main():
    # Header
    st.markdown('<div class="main-header">⚡ Comprehensive Electricity Analytics Chatbot</div>', unsafe_allow_html=True)
    
    # Load data
    data = load_all_data()
    
    if data is None:
        st.stop()
    
    # Get comprehensive stats once (avoid repeated calculations in loops)
    stats = get_comprehensive_stats(data)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analytics Dashboard")
        
        # Topic selector
        topic = st.selectbox(
            "📌 Select Topic",
            ["Overview", "Demand & Forecast", "Seasonal & Temporal", "Weather Impact", "Financial Metrics"]
        )
        
        st.divider()
        
        # Show relevant metrics based on topic
        if topic == "Overview" or topic == "Demand & Forecast":
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Historical Avg",
                    f"{stats['demand']['historical_avg']:.0f} MW",
                    help="2015-2025"
                )
            with col2:
                st.metric(
                    "Forecast Avg",
                    f"{stats['demand']['forecast_avg']:.0f} MW",
                    delta=f"{stats['demand']['trend_change']:.1f}%",
                    help="2026-2035"
                )
        
        if topic == "Overview" or topic == "Seasonal & Temporal":
            st.metric(
                "Peak Season",
                stats['seasonal']['peak_season'],
                help="Highest demand season"
            )
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Weekday", f"{stats['weekend']['weekday_avg']:.0f} MW")
            with col2:
                st.metric("Weekend", f"{stats['weekend']['weekend_avg']:.0f} MW")
        
        if topic == "Overview" or topic == "Financial Metrics":
            st.metric(
                "Avg Tariff",
                f"£{stats['financial']['avg_tariff']:.4f}/kWh"
            )
            st.metric(
                "Total Arrears",
                f"£{stats['financial']['total_arrears']:.1f}B"
            )
            st.metric(
                "Financial Stress",
                f"{stats['financial']['avg_fsi']:.2f}",
                delta=f"{stats['financial']['crisis_quarters']} crisis periods"
            )
        
        st.divider()
        
        # Visualization options
        st.subheader("📈 Visualizations")
        
        viz_options = {
            "Demand & Forecast": ["Demand Forecast", "Yearly Trend"],
            "Seasonal & Temporal": ["Seasonal Patterns", "Weekday Patterns", "Hourly Pattern"],
            "Weather Impact": ["Temperature Impact"],
            "Financial Metrics": ["Tariff vs Arrears", "Financial Stress Index"]
        }
        
        if topic in viz_options:
            viz_type = st.selectbox("Select Chart", viz_options[topic])
        else:
            viz_type = st.selectbox("Select Chart", ["Demand Forecast", "Seasonal Patterns", "Financial Stress Index"])
        
        if st.button("Generate Chart", use_container_width=True):
            st.session_state['show_viz'] = True
            st.session_state['viz_type'] = viz_type
        
        st.divider()
        
        # Data info
        st.subheader("ℹ️ Data Coverage")
        st.info(f"""**Time Period:**
        - Historical: 2015-2025
        - Forecast: 2026-2035
        
        **Data Points:**
        - {len(data['hourly']):,} hourly records
        - {len(data['daily']):,} daily records
        - {len(data['quarterly'])} quarters
        
        **Dimensions:**
        Demand, Seasonal, Weather, Financial""")
        
        # AI toggle
        st.divider()
        st.subheader("🔑 AI Mode")
        use_ai = st.checkbox("Use AI Chatbot", value=False)
        
        if use_ai:
            api_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                help="For advanced AI responses"
            )
            if api_key_input:
                os.environ['OPENAI_API_KEY'] = api_key_input
    
    # Main content
    col1_width, col2_width = 2, 1
    
    # Use pre-computed stats instead of creating new columns repeatedly
    cols = st.columns([col1_width, col2_width])
    
    with cols[0]:
        st.subheader("💬 Ask Me Anything")
        
        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [
                {
                    "role": "assistant",
                    "content": "Hello! 👋 I'm your comprehensive electricity analytics assistant. I can answer questions about:\n\n📊 Demand (historical & forecast)\n❄️ Seasonal patterns\n📅 Weekday/weekend trends\n🌡️ Weather impact\n💷 Financial metrics (tariffs, arrears, debt)\n\nWhat would you like to know?"
                }
            ]
        
        if 'conversation_history' not in st.session_state:
            st.session_state['conversation_history'] = []
        
        # Display messages
        for message in st.session_state['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about demand, seasonal patterns, weather, finances..."):
            st.session_state['messages'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = get_comprehensive_response(
                        prompt, data, 
                        st.session_state['conversation_history'],
                        use_ai
                    )
                    
                    if use_ai:
                        st.session_state['conversation_history'].append({"role": "user", "content": prompt})
                        st.session_state['conversation_history'].append({"role": "assistant", "content": response})
                    
                    st.markdown(response)
            
            st.session_state['messages'].append({"role": "assistant", "content": response})
    
    with cols[1]:
        st.subheader("📈 Visualizations")
        
        if st.session_state.get('show_viz', False):
            viz_type = st.session_state.get('viz_type', 'Demand Forecast')
            
            if viz_type == "Demand Forecast":
                fig = create_demand_forecast_chart(data)
            elif viz_type == "Seasonal Patterns":
                fig = create_seasonal_chart(data)
            elif viz_type == "Weekday Patterns":
                fig = create_weekday_chart(data)
            elif viz_type == "Hourly Pattern":
                fig = create_hourly_pattern_chart(data)
            elif viz_type == "Temperature Impact":
                fig = create_weather_impact_chart(data)
            elif viz_type == "Tariff vs Arrears":
                fig = create_tariff_arrears_chart(data)
            elif viz_type == "Financial Stress Index":
                fig = create_financial_stress_chart(data)
            else:
                fig = create_demand_forecast_chart(data)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👈 Select a topic and chart type, then click 'Generate Chart'")

if __name__ == "__main__":
    main()
