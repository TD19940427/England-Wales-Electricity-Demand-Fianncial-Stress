#!/usr/bin/env python3
"""Setup script to prepare data folder and copy CSV files"""

import os
import shutil

def setup_data_folder():
    """
    Create data folder and copy required CSV files from Power BI export directory.
    
    This script assumes you have already exported the data files from the notebook.
    Adjust the source_dir path if your files are located elsewhere.
    """
    
    # Create data folder if it doesn't exist
    data_folder = 'data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"✅ Created '{data_folder}' folder")
    else:
        print(f"✓ '{data_folder}' folder already exists")
    
    # Source directory (adjust this path to match your export location)
    source_dir = '/Workspace/Users/dutta.tania2050@gmail.com/Dissertation - Utility/PowerBI_Export'
    
    # Required files
    required_files = [
        '26_PowerBI_Complete_2015_2035.csv',
        '27_Monthly_Complete_2015_2035.csv',
        '23_Yearly_Historical_and_Forecast_Combined.csv'
    ]
    
    print("\n📋 Copying required files...")
    
    copied = 0
    for filename in required_files:
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(data_folder, filename)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"  ✅ Copied: {filename}")
            copied += 1
        else:
            print(f"  ❌ Not found: {filename}")
            print(f"     Expected at: {source_path}")
    
    print(f"\n📊 Summary: {copied}/{len(required_files)} files copied successfully")
    
    if copied == len(required_files):
        print("\n🎉 Setup complete! You can now run the app with: streamlit run app.py")
    else:
        print("\n⚠️  Some files are missing. Please:")
        print("   1. Run the full notebook pipeline to generate export files")
        print("   2. Check that the export directory path is correct")
        print("   3. Re-run this setup script")

if __name__ == "__main__":
    print("="*60)
    print("⚡ Electricity Demand Chatbot - Data Setup")
    print("="*60)
    print()
    
    setup_data_folder()
