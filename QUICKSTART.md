# ⚡ Quick Start Guide - 5 Minutes to Launch

## For Business Users (No Coding Experience)

### Step 1: Download the Application

1. Go to the GitHub repository
2. Click the green **"Code"** button
3. Select **"Download ZIP"**
4. Extract the ZIP file to your computer (e.g., `C:\Users\YourName\electricity-chatbot`)

### Step 2: Install Python (One-Time Setup)

If you don't have Python installed:

1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 (or latest version)
3. During installation, **CHECK** the box: "Add Python to PATH"
4. Click "Install Now"

### Step 3: Setup (One-Time)

Open Command Prompt (Windows) or Terminal (Mac/Linux):

```bash
# Navigate to the application folder
cd path/to/electricity-chatbot

# Install required packages
pip install -r requirements.txt

# Setup data files (if not already in data folder)
python setup_data.py
```

### Step 4: Run the Application

```bash
streamlit run app.py
```

That's it! The app will open in your web browser automatically.

## For Developers

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/electricity-demand-chatbot.git
cd electricity-demand-chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy data files
python setup_data.py

# Run
streamlit run app.py
```

### With OpenAI Integration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Then run:
streamlit run app.py
```

## Testing the App

### Try These Sample Questions:

1. **Basic Stats**:
   * "What is the average historical demand?"
   * "What's the forecast for 2030?"

2. **Comparisons**:
   * "Compare 2020 vs 2030"
   * "Is demand increasing or decreasing?"

3. **Trends**:
   * "Show me the trend over 20 years"
   * "What's the peak demand?"

### Generate Visualizations:

1. Look at the **left sidebar**
2. Select a chart type (Quarterly, Monthly, Yearly)
3. Click **"Generate Chart"**
4. Chart appears on the right side

## Troubleshooting

### "streamlit: command not found"
```bash
pip install --upgrade streamlit
```

### "Data files not found"
1. Ensure you have the `data` folder
2. Run `python setup_data.py`
3. Or manually copy CSV files to `data/` folder

### "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

## Stopping the Application

Press `Ctrl+C` in the terminal/command prompt.

## Next Steps

* 📚 Read the full [README.md](README.md) for detailed documentation
* 🎓 Explore advanced features and customization
* 🚀 Deploy to cloud (see README for deployment options)

---

**Need Help?** Open an issue on GitHub or contact support.
