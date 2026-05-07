import pandas as pd
import numpy as np
from datetime import datetime
import os

print("=" * 50)
print("STEP 1: DATA CLEANING")
print("=" * 50)

# Check if raw data exists
if not os.path.exists('data/raw/user_events.csv'):
    print("❌ Error: raw data not found!")
    print("Please run 0_create_sample_data.py first")
    exit(1)

# Load raw data
df = pd.read_csv('data/raw/user_events.csv', parse_dates=['event_time'])
print(f"\n📂 Loaded raw data: {len(df):,} rows, {df['user_id'].nunique():,} users")

# 1. Handle missing events
print("\n--- 1. Handling Missing Values ---")
initial_rows = len(df)
df = df.dropna(subset=['user_id', 'event_name'])
print(f"   Dropped rows with missing IDs/names: {initial_rows - len(df)}")

# For missing event_time, fill with a default
missing_time_mask = df['event_time'].isna()
if missing_time_mask.any():
    print(f"   Filling {missing_time_mask.sum()} missing event_time values")
    default_date = pd.Timestamp('2025-06-01')
    df.loc[missing_time_mask, 'event_time'] = default_date

# 2. Remove duplicates
print("\n--- 2. Removing Duplicates ---")
before_dedup = len(df)
df['event_date'] = df['event_time'].dt.date
duplicate_cols = ['user_id', 'event_name', 'event_date']
df = df.drop_duplicates(subset=duplicate_cols, keep='first')
print(f"   Removed {before_dedup - len(df)} duplicate rows")

# 3. Validate data types
print("\n--- 3. Validating Data Types ---")
df['event_time'] = pd.to_datetime(df['event_time'])
df['acquisition_month'] = pd.to_datetime(df['acquisition_month'])

# 4. Filter valid date range
print("\n--- 4. Filtering Date Range ---")
before_filter = len(df)
df = df[df['event_time'] >= '2025-01-01']
df = df[df['event_time'] <= '2026-04-30']
print(f"   Filtered out {before_filter - len(df)} rows outside date range")

# 5. Create additional columns for analysis
print("\n--- 5. Creating Analysis Columns ---")
df['hour'] = df['event_time'].dt.hour
df['day_of_week'] = df['event_time'].dt.day_name()
df['week'] = df['event_time'].dt.isocalendar().week
df['cohort'] = df['acquisition_month'].dt.to_period('M')
print(f"   Added columns: hour, day_of_week, week, cohort")

# Save cleaned data
df.to_csv('data/cleaned/cleaned_user_events.csv', index=False)
print(f"\n✅ Cleaned data saved to: data/cleaned/cleaned_user_events.csv")
print(f"   Final rows: {len(df):,}")
print(f"   Unique users: {df['user_id'].nunique():,}")
print(f"\n📊 Cleaned event distribution:")
print(df['event_name'].value_counts())

print("\n✅ Data cleaning completed successfully!")