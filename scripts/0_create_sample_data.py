import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Create directories if they don't exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/cleaned', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

print("=" * 50)
print("CREATING SAMPLE DATA")
print("=" * 50)

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

print("\n📊 Generating user behavior data...")

# Define parameters
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 4, 30)

# Total users
n_users = 10000

# Acquisition channels and their probabilities
channels = ['Organic', 'Paid', 'Referral']
channel_probs = [0.5, 0.3, 0.2]

# Generate user data
users = []
events = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
conversion_rates = {
    'landing': 1.0,
    'signup': 0.65,
    'onboarding': 0.70,
    'first_feature_use': 0.75,
    'upgrade': 0.30
}

# Channel-specific conversion modifiers
channel_modifiers = {
    'Organic': {'signup': 1.0, 'onboarding': 1.0, 'first_feature_use': 1.0, 'upgrade': 1.0},
    'Paid': {'signup': 1.2, 'onboarding': 0.9, 'first_feature_use': 0.85, 'upgrade': 0.7},
    'Referral': {'signup': 1.3, 'onboarding': 1.1, 'first_feature_use': 1.15, 'upgrade': 1.25}
}

user_events = []

for user_id in range(1, n_users + 1):
    # User signup date (random within date range)
    signup_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    acquisition_month = signup_date.strftime('%Y-%m')
    
    # Assign channel
    channel = np.random.choice(channels, p=channel_probs)
    
    # Track events with time delays
    current_time = signup_date
    user_completed = []
    
    # Landing (all users have landing)
    user_completed.append('landing')
    landing_time = current_time - timedelta(hours=random.randint(1, 48))
    user_events.append({
        'user_id': user_id,
        'event_name': 'landing',
        'event_time': landing_time,
        'acquisition_channel': channel,
        'acquisition_month': acquisition_month
    })
    
    # Signup (starts at signup date)
    signup_rate = conversion_rates['signup'] * channel_modifiers[channel]['signup']
    if np.random.random() < signup_rate:
        user_completed.append('signup')
        user_events.append({
            'user_id': user_id,
            'event_name': 'signup',
            'event_time': current_time,
            'acquisition_channel': channel,
            'acquisition_month': acquisition_month
        })
        
        # Onboarding (within 2 days of signup)
        onboarding_rate = conversion_rates['onboarding'] * channel_modifiers[channel]['onboarding']
        if np.random.random() < onboarding_rate:
            onboarding_time = current_time + timedelta(hours=random.randint(1, 48))
            user_completed.append('onboarding')
            user_events.append({
                'user_id': user_id,
                'event_name': 'onboarding',
                'event_time': onboarding_time,
                'acquisition_channel': channel,
                'acquisition_month': acquisition_month
            })
            
            # First Feature Use (within 3 days of onboarding)
            feature_rate = conversion_rates['first_feature_use'] * channel_modifiers[channel]['first_feature_use']
            if np.random.random() < feature_rate:
                feature_time = onboarding_time + timedelta(hours=random.randint(1, 72))
                user_completed.append('first_feature_use')
                user_events.append({
                    'user_id': user_id,
                    'event_name': 'first_feature_use',
                    'event_time': feature_time,
                    'acquisition_channel': channel,
                    'acquisition_month': acquisition_month
                })
                
                # Upgrade (within 14 days of feature use)
                upgrade_rate = conversion_rates['upgrade'] * channel_modifiers[channel]['upgrade']
                if np.random.random() < upgrade_rate:
                    upgrade_time = feature_time + timedelta(days=random.randint(1, 14))
                    user_completed.append('upgrade')
                    user_events.append({
                        'user_id': user_id,
                        'event_name': 'upgrade',
                        'event_time': upgrade_time,
                        'acquisition_channel': channel,
                        'acquisition_month': acquisition_month
                    })

# Create DataFrame
df = pd.DataFrame(user_events)
df = df.sort_values(['user_id', 'event_time'])

# Add some missing values and duplicates (real-world issues)
print("Adding data quality issues...")
# Add 2% missing event times
missing_mask = np.random.random(len(df)) < 0.02
df.loc[missing_mask, 'event_time'] = pd.NaT

# Add 3% duplicate rows
duplicate_count = int(len(df) * 0.03)
duplicates = df.sample(n=duplicate_count, replace=True)
df = pd.concat([df, duplicates], ignore_index=True)

# Save raw data
df.to_csv('data/raw/user_events.csv', index=False)
print(f"\n✅ Raw data saved to: data/raw/user_events.csv")
print(f"   Total rows: {len(df):,}")
print(f"   Unique users: {df['user_id'].nunique():,}")
print(f"\n📊 Event distribution:")
print(df['event_name'].value_counts())

print("\n✅ Data creation completed successfully!")