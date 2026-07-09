import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from openai import OpenAI
import json
import re

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
# QUERY PARSER FUNCTIONS
# ============================================================
def parse_year_query(question):
    """Extract year from question"""
    years = re.findall(r'\b(20\d{2})\b', question)
    return int(years[0]) if years else None

def parse_quarter_query(question):
    """Extract quarter from question"""
    quarters = re.findall(r'\bQ([1-4])\b|\b([1-4])(?:st|nd|rd|th)\s+quarter\b', question, re.IGNORECASE)
    if quarters:
        return int(quarters[0][0] or quarters[0][1])
    return None

def parse_hour_query(question):
    """Extract hour from question"""
    hour_patterns = [
        r'\b(\d{1,2}):(00|30)\b',
        r'\b(\d{1,2})h\b',
        r'\b(\d{1,2})\s*(am|pm)\b',
        r'hour\s+(\d{1,2})\b',
    ]
    for pattern in hour_patterns:
        matches = re.findall(pattern, question, re.IGNORECASE)
        if matches:
            hour = int(matches[0][0] if isinstance(matches[0], tuple) else matches[0])
            if len(matches[0]) > 1 and matches[0][1].lower() == 'pm' and hour < 12:
                hour += 12
            return hour
    return None

def query_specific_data(data, year=None, quarter=None, hour=None):
    """Query data for specific year/quarter/hour"""
    results = {}
    
    if year:
        quarterly = data['quarterly']
        year_data = quarterly[quarterly['Year'] == year]
        if len(year_data) > 0:
            results['year'] = {
                'year': year,
                'avg_demand': year_data['Demand_MW'].mean(),
                'min_demand': year_data['Demand_MW'].min(),
                'max_demand': year_data['Demand_MW'].max(),
                'quarters_count': len(year_data),
                'is_historical': year <= 2025,
                'is_forecast': year > 2025
            }
    
    if year and quarter:
        quarterly = data['quarterly']
        quarter_data = quarterly[(quarterly['Year'] == year) & (quarterly['Quarter'] == quarter)]
        if len(quarter_data) > 0:
            results['quarter'] = {
                'year': year,
                'quarter': quarter,
                'demand': quarter_data['Demand_MW'].iloc[0],
                'is_historical': year <= 2025,
                'is_forecast': year > 2025,
                'date': str(quarter_data['Quarter_End_Date'].iloc[0])
            }
    
    if hour is not None:
        hourly_pattern = data['hourly_pattern']
        hour_data = hourly_pattern[hourly_pattern['Hour'] == hour]
        if len(hour_data) > 0:
            results['hour'] = {
                'hour': hour,
                'avg_demand': hour_data['Avg_Demand_MW'].iloc[0],
                'std_demand': hour_data['Std_Demand_MW'].iloc[0],
                'min_demand': hour_data['Min_Demand_MW'].iloc[0],
                'max_demand': hour_data['Max_Demand_MW'].iloc[0]
            }
    
    return results

def get_fsi_baseline(data, year, quarter):
    """Get baseline FSI data for a specific quarter"""
    fsi_data = data['fsi_detail']
    baseline = fsi_data[(fsi_data['Year'] == year) & (fsi_data['Quarter'] == quarter)]
    
    if len(baseline) == 0:
        return None
    
    row = baseline.iloc[0]
    return {
        'year': year,
        'quarter': quarter,
        'demand_mw': row['Demand_MW'],
        'price_kwh': row['Price_per_kWh'],
        'arrears_bn': row['Arrears_Billions_GBP'],
        'fsi': row['Financial_Stress_Index'],
        'date': row['Quarter_End_Date']
    }

def simulate_fsi(baseline, price_change_pct=0, demand_change_pct=0, arrears_change_bn=0):
    """Simulate FSI with variable changes"""
    
    # Apply changes
    new_demand = baseline['demand_mw'] * (1 + demand_change_pct / 100)
    new_price = baseline['price_kwh'] * (1 + price_change_pct / 100)
    new_arrears = baseline['arrears_bn'] + arrears_change_bn
    
    # Calculate new FSI
    # FSI = (Demand × Price) + Arrears
    baseline_fsi = baseline['fsi']
    new_fsi = (new_demand * new_price) + new_arrears
    
    # Calculate impacts
    impact = new_fsi - baseline_fsi
    impact_pct = (impact / baseline_fsi * 100) if baseline_fsi != 0 else 0
    
    return {
        'baseline_demand': baseline['demand_mw'],
        'new_demand': new_demand,
        'baseline_price': baseline['price_kwh'],
        'new_price': new_price,
        'baseline_arrears': baseline['arrears_bn'],
        'new_arrears': new_arrears,
        'baseline_fsi': baseline_fsi,
        'new_fsi': new_fsi,
        'impact': impact,
        'impact_pct': impact_pct
    }

# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================
def create_demand_forecast_chart(data):
    """Fixed: Demand historical vs forecast"""
    df = data['quarterly'].copy()
    df = df.sort_values('Quarter_End_Date')
    
    fig = go.Figure()
    
    historical = df[df['Data_Type'].str.contains('Historical', na=False)]
    forecast = df[df['Data_Type'].str.contains('Forecast', na=False)]
    
    fig.add_trace(go.Scatter(
        x=historical['Quarter_End_Date'],
        y=historical['Historical_Demand_MW'],
        mode='lines+markers',
        name='Historical (2015-2025)',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Demand: %{y:.2f} MW<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast['Quarter_End_Date'],
        y=forecast['Forecast_Demand_MW'],
        mode='lines+markers',
        name='Forecast (2026-2035)',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=6),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Forecast: %{y:.2f} MW<extra></extra>'
    ))
    
    fig.update_layout(
        title='Quarterly Electricity Demand: Historical vs Forecast',
        xaxis_title='Quarter',
        yaxis_title='Demand (MW)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True
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
    """Enhanced chatbot with specific query support"""
    
    question_lower = user_question.lower()
    stats = get_comprehensive_stats(data)
    
    # Check if using AI
    if use_ai and os.getenv('OPENAI_API_KEY'):
        return get_ai_response(user_question, data, stats, conversation_history)
    
    # === PARSE SPECIFIC QUERIES ===
    year = parse_year_query(user_question)
    quarter = parse_quarter_query(user_question)
    hour = parse_hour_query(user_question)
    
    # Query specific data if parameters found
    if year or hour:
        specific_data = query_specific_data(data, year=year, quarter=quarter, hour=hour)
        
        # YEAR-SPECIFIC QUERY
        if 'year' in specific_data and ('demand' in question_lower or year):
            yr = specific_data['year']
            period_type = "Historical" if yr['is_historical'] else "Forecast"
            return f"""📊 **Electricity Demand in {yr['year']} ({period_type}):**

• Average Demand: **{yr['avg_demand']:.2f} MW**
• Minimum: {yr['min_demand']:.2f} MW
• Maximum: {yr['max_demand']:.2f} MW
• Data Points: {yr['quarters_count']} quarters

{'This is actual historical data from operational records.' if yr['is_historical'] else 'This is forecast data from Prophet predictive model.'}"""
        
        # QUARTER-SPECIFIC QUERY
        if 'quarter' in specific_data:
            q = specific_data['quarter']
            period_type = "Historical" if q['is_historical'] else "Forecast"
            return f"""📅 **Q{q['quarter']} {q['year']} Electricity Demand ({period_type}):**

• Demand: **{q['demand']:.2f} MW**
• Quarter End Date: {q['date']}
• Period Type: {period_type}

{'Based on actual operational data.' if q['is_historical'] else 'Based on Prophet forecast model.'}"""
        
        # HOUR-SPECIFIC QUERY
        if 'hour' in specific_data and ('hour' in question_lower or ':' in user_question or 'am' in question_lower or 'pm' in question_lower):
            h = specific_data['hour']
            return f"""🕐 **Average Demand at {h['hour']:02d}:00 (Across All Historical Days):**

• Average Demand: **{h['avg_demand']:.2f} MW**
• Standard Deviation: ±{h['std_demand']:.2f} MW
• Minimum Recorded: {h['min_demand']:.2f} MW
• Maximum Recorded: {h['max_demand']:.2f} MW

This represents the typical demand at {h['hour']:02d}:00 across the entire historical period (2015-2025)."""
    
    # === EXISTING GENERIC RESPONSES ===
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

**📊 Specific Queries (NEW!):**
✅ "What is demand in 2024?" (any year 2015-2035)
✅ "What is demand in Q1 2024?" (specific quarter)
✅ "What is avg demand at 18:00?" (any hour 0-23)
✅ "Compare 2024 vs 2025"

**📚 General Topics:**
✅ Demand (historical 2015-2025 & forecast 2026-2035)
✅ Seasonal patterns (Winter, Spring, Summer, Autumn)
✅ Weekday vs Weekend patterns
✅ Weather impact (Temperature, Rainfall)
✅ Financial metrics (Tariffs, Arrears, Debt)
✅ Financial Stress Index

**🎯 Quick Stats:**
- Historical Avg Demand: {stats['demand']['historical_avg']:.0f} MW
- Forecast Avg Demand: {stats['demand']['forecast_avg']:.0f} MW
- Peak Season: {stats['seasonal']['peak_season']}
- Avg Tariff: £{stats['financial']['avg_tariff']:.4f}/kWh

**💬 Try asking:**
- "What is demand in 2024?"
- "What is avg demand at 18:00?"
- "What are the seasonal patterns?"
- "Compare weekday vs weekend"
- "What's the financial stress index?"
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
        
        # Page selector
        page_mode = st.radio(
            "📌 Select Mode",
            ["Analytics Dashboard", "FSI Scenario Tool"],
            horizontal=True
        )
        
        st.divider()
        
        # Topic selector (only for Analytics Dashboard)
        if page_mode == "Analytics Dashboard":
            topic = st.selectbox(
                "📌 Select Topic",
                ["Overview", "Demand & Forecast", "Seasonal & Temporal", "Weather Impact", "Financial Metrics"]
            )
        else:
            topic = None
        
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

def show_fsi_scenario_page(data):
    """FSI Scenario Analysis Page"""
    
    st.title("📊 Financial Stress Index - Scenario Analysis")
    st.markdown("""Simulate the impact of changes in electricity prices, demand, and consumer debt 
    on the Financial Stress Index (FSI) for England & Wales.""")
    
    st.divider()
    
    # Get available years and quarters from FSI data
    fsi_data = data['fsi_detail']
    available_years = sorted(fsi_data['Year'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Select Period")
        selected_year = st.selectbox("Year", available_years, index=len(available_years)//2)
        selected_quarter = st.selectbox("Quarter", [1, 2, 3, 4])
    
    with col2:
        st.subheader("⚙️ Adjust Variables")
        price_change = st.slider(
            "Price Change (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            help="Adjust electricity price by percentage"
        )
        demand_change = st.slider(
            "Demand Change (%)",
            min_value=-20,
            max_value=20,
            value=0,
            step=2,
            help="Adjust electricity demand by percentage"
        )
        arrears_change = st.slider(
            "Arrears Change (£bn)",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Adjust consumer arrears/debt in billions of pounds"
        )
    
    st.divider()
    
    # Get baseline data
    baseline = get_fsi_baseline(data, selected_year, selected_quarter)
    
    if baseline is None:
        st.error(f"❌ No FSI data available for Q{selected_quarter} {selected_year}")
        st.info("Please select a different period with available data.")
        return
    
    # Calculate scenario
    result = simulate_fsi(baseline, price_change, demand_change, arrears_change)
    
    # Display results
    st.subheader(f"📊 FSI Scenario Results: Q{selected_quarter} {selected_year}")
    
    # Metrics in 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Baseline FSI",
            f"£{result['baseline_fsi']:,.2f}",
            help="Current FSI value"
        )
    
    with col2:
        st.metric(
            "New FSI",
            f"£{result['new_fsi']:,.2f}",
            delta=f"{result['impact_pct']:+.1f}%",
            delta_color="inverse",
            help="FSI after applying changes"
        )
    
    with col3:
        st.metric(
            "Impact",
            f"£{result['impact']:+,.2f}",
            help="Change in FSI (billions)"
        )
    
    st.divider()
    
    # Detailed breakdown
    st.subheader("📄 Detailed Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Baseline (Current)**")
        breakdown_df_baseline = pd.DataFrame({
            'Variable': ['Demand', 'Price', 'Arrears', '**FSI Total**'],
            'Value': [
                f"{result['baseline_demand']:,.0f} MW",
                f"£{result['baseline_price']:.4f}/kWh",
                f"£{result['baseline_arrears']:.2f}bn",
                f"**£{result['baseline_fsi']:,.2f}**"
            ]
        })
        st.dataframe(breakdown_df_baseline, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**Scenario (After Changes)**")
        breakdown_df_new = pd.DataFrame({
            'Variable': ['Demand', 'Price', 'Arrears', '**FSI Total**'],
            'Value': [
                f"{result['new_demand']:,.0f} MW ({demand_change:+}%)",
                f"£{result['new_price']:.4f}/kWh ({price_change:+}%)",
                f"£{result['new_arrears']:.2f}bn ({arrears_change:+.1f}bn)",
                f"**£{result['new_fsi']:,.2f}** ({result['impact_pct']:+.1f}%)"
            ]
        })
        st.dataframe(breakdown_df_new, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Visualization - Before vs After
    st.subheader("📈 Visual Comparison")
    
    fig = go.Figure()
    
    # Bar chart comparing baseline vs scenario
    categories = ['Baseline FSI', 'Scenario FSI']
    values = [result['baseline_fsi'], result['new_fsi']]
    colors = ['steelblue', 'coral' if result['impact'] > 0 else 'lightgreen']
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker=dict(color=colors),
        text=[f"£{v:,.2f}" for v in values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>FSI: £%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'FSI Comparison: Q{selected_quarter} {selected_year}',
        yaxis_title='Financial Stress Index (£)',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Component breakdown chart
    st.subheader("📊 Component Breakdown")
    
    fig2 = go.Figure()
    
    components_baseline = [
        ('Demand × Price', result['baseline_demand'] * result['baseline_price']),
        ('Arrears', result['baseline_arrears'])
    ]
    
    components_scenario = [
        ('Demand × Price', result['new_demand'] * result['new_price']),
        ('Arrears', result['new_arrears'])
    ]
    
    fig2.add_trace(go.Bar(
        name='Baseline',
        x=[c[0] for c in components_baseline],
        y=[c[1] for c in components_baseline],
        marker_color='steelblue',
        text=[f"£{c[1]:,.2f}" for c in components_baseline],
        textposition='outside'
    ))
    
    fig2.add_trace(go.Bar(
        name='Scenario',
        x=[c[0] for c in components_scenario],
        y=[c[1] for c in components_scenario],
        marker_color='coral',
        text=[f"£{c[1]:,.2f}" for c in components_scenario],
        textposition='outside'
    ))
    
    fig2.update_layout(
        title='FSI Components: Baseline vs Scenario',
        yaxis_title='Value (£ billions)',
        barmode='group',
        template='plotly_white',
        height=400,
        legend=dict(x=0.7, y=0.98)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Interpretation
    st.divider()
    st.subheader("💡 Interpretation")
    
    if result['impact'] > 0:
        impact_text = "🗔 **Increased financial stress**"
        explanation = f"""The scenario results in a **{abs(result['impact_pct']):.1f}% increase** in the Financial Stress Index, 
        adding £{abs(result['impact']):.2f} billion in financial burden. This suggests:
        - Higher consumer electricity costs
        - Increased risk of payment defaults
        - Greater affordability challenges for households"""
    elif result['impact'] < 0:
        impact_text = "🟢 **Reduced financial stress**"
        explanation = f"""The scenario results in a **{abs(result['impact_pct']):.1f}% decrease** in the Financial Stress Index, 
        reducing financial burden by £{abs(result['impact']):.2f} billion. This suggests:
        - Lower consumer electricity costs
        - Improved affordability
        - Reduced risk of arrears and debt"""
    else:
        impact_text = "➪ **No change**"
        explanation = "The scenario parameters result in no net change to the Financial Stress Index."
    
    st.markdown(impact_text)
    st.markdown(explanation)
    
    # Formula explanation
    st.divider()
    with st.expander("📚 How is FSI Calculated?"):
        st.markdown("""
        **Financial Stress Index Formula:**
        
        ```
        FSI = (Electricity Demand × Price per kWh) + Customer Arrears/Debt
        ```
        
        **Components:**
        - **Demand (MW)**: Quarterly average electricity demand in megawatts
        - **Price (£/kWh)**: Average variable unit price per kilowatt-hour
        - **Arrears (£bn)**: Total customer arrears and debt in billions of pounds
        
        **What it measures:**
        FSI combines consumption costs and payment difficulties to identify periods when 
        consumers face elevated financial stress from electricity expenses.
        
        **Data sources:**
        - Demand: UK National Grid ESO
        - Prices: BEIS/DESNZ Quarterly Energy Prices
        - Arrears: Ofgem financial vulnerability data
        """)

if __name__ == "__main__":
    main()
