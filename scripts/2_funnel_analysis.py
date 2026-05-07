import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 50)
print("STEP 2: FUNNEL ANALYSIS")
print("=" * 50)

# Load cleaned data
df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time'])

# Define funnel steps in order
funnel_steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']

# Function to calculate funnel for a subset of users
def calculate_funnel(data, funnel_steps):
    """Calculate conversion and drop-off rates for funnel"""
    
    # Get users who performed each step
    funnel_counts = {}
    for step in funnel_steps:
        users_at_step = data[data['event_name'] == step]['user_id'].unique()
        funnel_counts[step] = len(users_at_step)
    
    # Calculate conversion rates
    funnel_df = pd.DataFrame({
        'step': funnel_steps,
        'users': [funnel_counts[step] for step in funnel_steps]
    })
    
    # Total users (landing page visitors)
    total_users = funnel_counts['landing']
    
    # Conversion rate (from start)
    funnel_df['conversion_rate_from_start'] = (funnel_df['users'] / total_users * 100).round(2)
    
    # Step conversion rate (from previous step)
    step_conversions = []
    for i in range(len(funnel_steps)):
        if i == 0:
            step_conversions.append(100.0)
        else:
            prev_users = funnel_counts[funnel_steps[i-1]]
            curr_users = funnel_counts[funnel_steps[i]]
            rate = (curr_users / prev_users * 100) if prev_users > 0 else 0
            step_conversions.append(round(rate, 2))
    
    funnel_df['step_conversion_rate'] = step_conversions
    funnel_df['drop_off_rate'] = (100 - funnel_df['step_conversion_rate']).round(2)
    funnel_df['cumulative_drop_off'] = (100 - funnel_df['conversion_rate_from_start']).round(2)
    
    return funnel_df, funnel_counts

# Calculate overall funnel
funnel_df, funnel_counts = calculate_funnel(df, funnel_steps)

print("\n📊 OVERALL FUNNEL ANALYSIS")
print("-" * 60)
print(funnel_df.to_string(index=False))
print("-" * 60)

# Identify key drop-off points
print("\n🔍 KEY DROP-OFF POINTS:")
print("-" * 40)
max_drop_idx = funnel_df['drop_off_rate'].iloc[1:].idxmax()
max_drop_step = funnel_df.loc[max_drop_idx, 'step']
max_drop_rate = funnel_df.loc[max_drop_idx, 'drop_off_rate']
print(f"1. Biggest drop-off: {max_drop_step} → {max_drop_rate}% users lost")

second_drop_idx = funnel_df['drop_off_rate'].iloc[1:].nlargest(2).index[-1]
second_drop_step = funnel_df.loc[second_drop_idx, 'step']
second_drop_rate = funnel_df.loc[second_drop_idx, 'drop_off_rate']
print(f"2. Second biggest: {second_drop_step} → {second_drop_rate}% users lost")

# Visualization - Funnel Chart
plt.figure(figsize=(12, 8))

# Create funnel chart
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
y_pos = range(len(funnel_steps))

# Horizontal bar chart for funnel
plt.subplot(1, 2, 1)
bars = plt.barh(y_pos, funnel_df['users'], color=colors)
plt.yticks(y_pos, [step.upper().replace('_', ' ') for step in funnel_steps])
plt.xlabel('Number of Users')
plt.title('Conversion Funnel - User Count', fontsize=14, fontweight='bold')

# Add value labels on bars
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + (max(funnel_df['users'])*0.02), bar.get_y() + bar.get_height()/2, 
             f'{int(width):,}', ha='left', va='center', fontweight='bold')

# Drop-off analysis subplot
plt.subplot(1, 2, 2)
drop_off_steps = funnel_steps[1:]  # Exclude first step
drop_off_rates = funnel_df['drop_off_rate'].iloc[1:]

bars2 = plt.bar(range(len(drop_off_steps)), drop_off_rates, color='#e74c3c', alpha=0.7)
plt.xticks(range(len(drop_off_steps)), [step.replace('_', ' ').title() for step in drop_off_steps], 
           rotation=45, ha='right')
plt.ylabel('Drop-off Rate (%)')
plt.title('Drop-off Rate by Funnel Step', fontsize=14, fontweight='bold')
plt.ylim(0, 100)

# Add percentage labels
for bar, rate in zip(bars2, drop_off_rates):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{rate}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/funnel_chart.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ Funnel chart saved to 'outputs/funnel_chart.png'")

# Calculate funnel metrics summary
print("\n📈 FUNNEL METRICS SUMMARY:")
print(f"Total Landing Visitors: {funnel_counts['landing']:,}")
print(f"Total Signups: {funnel_counts['signup']:,} ({funnel_df.loc[0, 'step_conversion_rate']}%)")
print(f"Completed Onboarding: {funnel_counts['onboarding']:,} ({funnel_df.loc[1, 'step_conversion_rate']}%)")
print(f"Used First Feature: {funnel_counts['first_feature_use']:,} ({funnel_df.loc[2, 'step_conversion_rate']}%)")
print(f"Upgraded to Paid: {funnel_counts['upgrade']:,} ({funnel_df.loc[3, 'step_conversion_rate']}%)")
print(f"\nOverall Conversion (Landing → Upgrade): {funnel_df.loc[4, 'conversion_rate_from_start']}%")