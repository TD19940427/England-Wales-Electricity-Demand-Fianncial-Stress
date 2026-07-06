# ⚡ Comprehensive Electricity Analytics Chatbot

An interactive Streamlit chatbot application for comprehensive UK electricity analytics from 2015-2035, including demand forecasts, seasonal patterns, weather impact, and financial metrics.

## 🎯 Features

### **Complete Data Coverage**

* **📊 Demand Analytics**: Historical (2015-2025) and 10-year forecasts (2026-2035)
* **❄️ Seasonal Patterns**: Winter, Spring, Summer, Autumn demand analysis
* **📅 Temporal Patterns**: Hourly patterns, weekday vs weekend comparison
* **🌡️ Weather Impact**: Temperature and rainfall effects on electricity demand
* **💷 Financial Metrics**: Tariffs, customer arrears, debt tracking
* **📉 Financial Stress Index**: Affordability crisis detection and monitoring
* **🔮 Prophet Forecasts**: AI-powered 10-year demand predictions

### **Interactive Features**

* **Natural Language Q&A**: Ask questions in plain English
* **AI-Powered Responses**: Optional OpenAI integration for intelligent answers
* **Rule-Based Fallback**: Works without API keys
* **Real-Time Visualizations**: 7 different chart types covering all dimensions
* **Topic Navigation**: Organized by analysis categories
* **Conversation History**: Context-aware follow-up questions

## 📊 Data Dimensions

### 1. **Demand & Forecast**
* Historical demand (2015-2025): 146,568 hourly records
* Forecast demand (2026-2035): Prophet model predictions
* Quarterly, monthly, daily, hourly granularity

### 2. **Seasonal & Temporal Patterns**
* Four seasons (Winter, Spring, Summer, Autumn)
* Seven days of week analysis
* 24-hour daily patterns
* Weekday vs weekend comparison

### 3. **Weather Impact**
* Temperature bins and demand correlation
* Rainfall analysis
* Cold weather heating impact
* Hot weather cooling demand

### 4. **Financial Metrics**
* Quarterly electricity tariffs (£/kWh)
* Customer arrears and debt (£ billions)
* Financial Stress Index (FSI)
* Crisis period identification

## 🚀 Quick Start

### Prerequisites

* Python 3.8 or higher
* pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/electricity-analytics-chatbot.git
   cd electricity-analytics-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify data files**
   
   The `data` folder should contain these files:
   ```
   data/
   ├── 26_PowerBI_Complete_2015_2035.csv
   ├── 27_Monthly_Complete_2015_2035.csv
   ├── 23_Yearly_Historical_and_Forecast_Combined.csv
   ├── 01_Hourly_Demand.csv
   ├── 02_Daily_Demand.csv
   ├── 04_Monthly_Demand.csv
   ├── 15a_Hourly_Pattern.csv
   ├── 15b_Weekday_Pattern.csv
   ├── 15c_Weekend_Comparison.csv
   ├── 15d_Seasonal_Pattern.csv
   ├── 14a_Temperature_Bins.csv
   ├── 14b_Rainfall_Bins.csv
   ├── 10_Quarterly_Tariff_EnglandWales.csv
   ├── 11_Quarterly_Arrears_Debt.csv
   ├── 12_Financial_Stress_Index.csv
   └── 00_DATA_DICTIONARY.csv
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   * Automatically opens at `http://localhost:8501`

## 💬 Sample Questions

### Demand & Forecast
* "What is the average historical demand?"
* "What's the forecast for 2030?"
* "Compare historical vs forecast demand"
* "Is demand increasing or decreasing?"

### Seasonal & Temporal
* "What are the seasonal patterns?"
* "Which season has the highest demand?"
* "Compare weekday vs weekend demand"
* "Show me the hourly demand pattern"

### Weather Impact
* "How does temperature affect demand?"
* "What's the demand in cold weather?"
* "Does rainfall impact electricity usage?"

### Financial Metrics
* "What are the electricity tariffs?"
* "Show me customer arrears trends"
* "What's the financial stress index?"
* "When were the crisis periods?"

### Comprehensive Comparisons
* "Compare all metrics"
* "Show me peak demand analysis"
* "What drives electricity demand?"

## 📁 Project Structure

```
electricity-analytics-chatbot/
│
├── app.py                  # Main Streamlit application (685 lines)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── QUICKSTART.md          # 5-minute setup guide
├── DEMO.md               # Feature walkthrough
├── setup_data.py         # Data folder setup script
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
│
└── data/                 # Data folder (17MB total)
    ├── Core demand files (quarterly, monthly, yearly)
    ├── Detailed historical data (hourly, daily)
    ├── Pattern files (seasonal, weekday, hourly)
    ├── Weather impact files (temperature, rainfall)
    ├── Financial files (tariffs, arrears, FSI)
    └── Data dictionary
```

## 🔑 Optional: Enable AI Chatbot

For advanced AI-powered responses:

1. **Get an OpenAI API Key**
   * Sign up at [OpenAI Platform](https://platform.openai.com/)
   * Create an API key

2. **Configure the app**
   * In the sidebar, check "Use AI Chatbot"
   * Enter your API key
   
   *OR* set as environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   streamlit run app.py
   ```

## 📈 Available Visualizations

### 1. **Demand & Forecast Charts**
* Historical vs Forecast time series
* Yearly trend comparison

### 2. **Seasonal & Temporal Charts**
* Seasonal demand patterns (bar chart)
* Weekday patterns (7-day comparison)
* Hourly pattern (24-hour curve)

### 3. **Weather Impact Charts**
* Temperature impact on demand
* Demand across temperature bins

### 4. **Financial Charts**
* Tariff vs Arrears (dual-axis time series)
* Financial Stress Index over time

## 🎨 Features Overview

### **Topic-Based Navigation**
Switch between analysis categories:
* Overview (all metrics at a glance)
* Demand & Forecast
* Seasonal & Temporal
* Weather Impact
* Financial Metrics

### **Smart Context Switching**
The sidebar dynamically shows relevant metrics and chart options based on selected topic.

### **Dual Mode Operation**
* **Simple Mode**: Rule-based responses (instant, no API needed)
* **AI Mode**: OpenAI-powered (context-aware, conversational)

## 🛠️ Customization

### Adding More Questions

Edit `get_comprehensive_response()` in `app.py`:

```python
if 'your_keyword' in question_lower:
    return "Your custom response with stats"
```

### Adding New Visualizations

Create a new function following the pattern:

```python
def create_your_chart(data):
    df = data['your_data']
    fig = px.bar(...)  # or go.Figure()
    return fig
```

### Adding New Data Sources

1. Add CSV file to `data/` folder
2. Load in `load_all_data()` function
3. Update `get_comprehensive_stats()` to include new metrics
4. Add responses in `get_comprehensive_response()`

## 📤 Deployment Options

### **Deploy to Streamlit Cloud** (Free & Recommended)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `OPENAI_API_KEY` to Secrets (if using AI)
5. Deploy!

### **Deploy to Heroku**

```bash
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY="your-key"
```

### **Deploy to AWS/Azure/GCP**

Use Docker or standard Python deployment. App runs on port 8501.

## 🔒 Security Notes

* **Never commit API keys** to GitHub
* Use `.env` files or cloud secrets management
* The `.gitignore` file is pre-configured
* Ensure CSV files don't contain PII before public deployment

## 🐛 Troubleshooting

### "Data files not found"
* Ensure all 16 CSV files are in `data/` folder
* Run `python setup_data.py` to copy files
* Check file names match exactly

### Charts not displaying
* Clear browser cache
* Refresh page
* Check browser console for errors

### AI responses not working
* Verify OpenAI API key is correct
* Check API key has available credits
* Try Simple Mode (rule-based) as fallback

### App is slow
* Reduce hourly data file size if needed
* Use cached data (already implemented)
* Deploy to cloud for better performance

## 📊 Data Statistics

* **Total Data Points**: 146,568 hourly records
* **Time Coverage**: 2015-2035 (21 years)
* **Historical Period**: 2015-2025 (11 years)
* **Forecast Period**: 2026-2035 (10 years)
* **Data Size**: ~17 MB
* **Dimensions Covered**: 6 major categories

## 🎓 Use Cases

### **Energy Planners**
* Long-term capacity planning
* Infrastructure investment decisions
* Seasonal preparation strategies

### **Operations Managers**
* Maintenance scheduling (low-demand periods)
* Staffing optimization (weekday/weekend patterns)
* Real-time demand prediction

### **Financial Analysts**
* Tariff impact analysis
* Customer affordability monitoring
* Revenue forecasting

### **Policy Makers**
* Crisis period identification
* Social support program timing
* Energy poverty insights

### **Researchers**
* Weather-demand correlation studies
* Seasonal behavior analysis
* Long-term trend research

## 📝 License

MIT License - free to use and modify for your needs.

## 🤝 Contributing

Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For questions or issues:
* Open a GitHub issue
* Check [QUICKSTART.md](QUICKSTART.md) for setup help
* Review [DEMO.md](DEMO.md) for feature details

## 🎓 Academic Citation

If using this for research:

```bibtex
@software{electricity_analytics_chatbot,
  author = {Your Name},
  title = {Comprehensive Electricity Analytics Chatbot},
  year = {2026},
  url = {https://github.com/yourusername/electricity-analytics-chatbot}
}
```

## ⚡ Technology Stack

* **[Streamlit](https://streamlit.io/)** - Web framework
* **[Plotly](https://plotly.com/)** - Interactive visualizations
* **[Pandas](https://pandas.pydata.org/)** - Data manipulation
* **[Prophet](https://facebook.github.io/prophet/)** - Forecasting model
* **[OpenAI](https://openai.com/)** - AI-powered responses (optional)

## 🌟 Key Highlights

✅ **Comprehensive**: Covers 6 major data dimensions  
✅ **Interactive**: Natural language Q&A interface  
✅ **Visual**: 7 different chart types  
✅ **Intelligent**: AI-powered and rule-based modes  
✅ **Production-Ready**: Full documentation and deployment guides  
✅ **Business-Friendly**: Non-technical users can explore complex data  
✅ **Open Source**: MIT license, free to use and modify  

---

**Made with ❤️ for comprehensive electricity analytics and forecasting**

*Empowering data-driven decisions in the energy sector*
