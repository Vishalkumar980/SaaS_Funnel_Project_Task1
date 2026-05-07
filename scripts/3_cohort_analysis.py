import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

print("=" * 60)
print("STEP 3: COHORT ANALYSIS")
print("=" * 60)

# Load cleaned data
if not os.path.exists('data/cleaned/cleaned_user_events.csv'):
    print("\n❌ ERROR: Cleaned data not found!")
    print("Please run 1_data_cleaning.py first")
    exit(1)

df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time', 'acquisition_month'])
print(f"\n📂 Loaded cleaned data: {len(df):,} rows, {df['user_id'].nunique():,} users")

# Define funnel steps (FIXED: Added this definition)
funnel_steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
step_labels = ['Landing', 'Sign-up', 'Onboarding', 'First Feature Use', 'Upgrade']

# Add cohort period
df['cohort'] = df['acquisition_month'].dt.to_period('M')

# Get unique cohorts
cohorts = sorted(df['cohort'].dropna().unique())
print(f"\n📊 Analyzing {len(cohorts)} cohorts from {cohorts[0]} to {cohorts[-1]}")

# Calculate cohort metrics
cohort_metrics = []

for cohort in cohorts:
    cohort_data = df[df['cohort'] == cohort]
    cohort_users = cohort_data['user_id'].nunique()
    
    # Count users at each funnel stage for this cohort
    signup_users = cohort_data[cohort_data['event_name'] == 'signup']['user_id'].nunique()
    onboard_users = cohort_data[cohort_data['event_name'] == 'onboarding']['user_id'].nunique()
    feature_users = cohort_data[cohort_data['event_name'] == 'first_feature_use']['user_id'].nunique()
    upgrade_users = cohort_data[cohort_data['event_name'] == 'upgrade']['user_id'].nunique()
    
    cohort_metrics.append({
        'Cohort': str(cohort),
        'Users': cohort_users,
        'Signup Rate': (signup_users / cohort_users * 100) if cohort_users > 0 else 0,
        'Onboarding Rate': (onboard_users / cohort_users * 100) if cohort_users > 0 else 0,
        'Feature Rate': (feature_users / cohort_users * 100) if cohort_users > 0 else 0,
        'Upgrade Rate': (upgrade_users / cohort_users * 100) if cohort_users > 0 else 0
    })

cohort_df = pd.DataFrame(cohort_metrics)

print("\n📈 COHORT PERFORMANCE TABLE:")
print("-" * 80)
print(cohort_df.to_string(index=False))
print("-" * 80)

# Identify trends
print("\n📊 COHORT TRENDS:")
first_cohort_rate = cohort_df.iloc[0]['Upgrade Rate']
last_cohort_rate = cohort_df.iloc[-1]['Upgrade Rate']
trend_change = last_cohort_rate - first_cohort_rate

if trend_change > 0:
    print(f"✅ POSITIVE TREND: Upgrade rates improved by {trend_change:.1f}%")
    print(f"   ({first_cohort_rate:.1f}% → {last_cohort_rate:.1f}%)")
else:
    print(f"⚠️ NEGATIVE TREND: Upgrade rates declined by {abs(trend_change):.1f}%")
    print(f"   ({first_cohort_rate:.1f}% → {last_cohort_rate:.1f}%)")

# Create visualizations
print("\n🎨 Creating cohort visualizations...")

# Create output directory if not exists
os.makedirs('outputs', exist_ok=True)

# Figure 1: Cohort performance over time
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Upgrade rate trend
ax1 = axes[0, 0]
ax1.plot(cohort_df['Cohort'], cohort_df['Upgrade Rate'], marker='o', linewidth=2, 
         color='#2ecc71', markersize=8)
ax1.set_xlabel('Acquisition Cohort', fontsize=11)
ax1.set_ylabel('Upgrade Rate (%)', fontsize=11)
ax1.set_title('Cohort Upgrade Rate Trend', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

# 2. All metrics comparison
ax2 = axes[0, 1]
x_pos = np.arange(len(cohort_df))
width = 0.2
ax2.bar(x_pos - width*1.5, cohort_df['Signup Rate'], width, label='Signup', color='#3498db')
ax2.bar(x_pos - width/2, cohort_df['Onboarding Rate'], width, label='Onboarding', color='#f39c12')
ax2.bar(x_pos + width/2, cohort_df['Feature Rate'], width, label='Feature Use', color='#e74c3c')
ax2.bar(x_pos + width*1.5, cohort_df['Upgrade Rate'], width, label='Upgrade', color='#2ecc71')
ax2.set_xlabel('Cohort', fontsize=11)
ax2.set_ylabel('Rate (%)', fontsize=11)
ax2.set_title('Cohort Performance - All Metrics', fontsize=13, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(cohort_df['Cohort'], rotation=45, ha='right')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Heatmap: Cohort progression
ax3 = axes[1, 0]
# Create matrix of cohort progression
progression_matrix = []
for idx, row in cohort_df.iterrows():
    progression_matrix.append([
        row['Signup Rate'],
        row['Onboarding Rate'],
        row['Feature Rate'],
        row['Upgrade Rate']
    ])

im = ax3.imshow(progression_matrix, cmap='YlOrRd', aspect='auto')
ax3.set_xticks(range(4))
ax3.set_xticklabels(['Signup', 'Onboard', 'Feature', 'Upgrade'])
ax3.set_yticks(range(len(cohort_df)))
ax3.set_yticklabels(cohort_df['Cohort'])
ax3.set_xlabel('Funnel Stage', fontsize=11)
ax3.set_ylabel('Cohort', fontsize=11)
ax3.set_title('Cohort Progression Heatmap', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax3, label='Conversion Rate (%)')

# 4. User count by cohort
ax4 = axes[1, 1]
bars = ax4.barh(cohort_df['Cohort'], cohort_df['Users'], color='#9b59b6', alpha=0.7)
ax4.set_xlabel('Number of Users', fontsize=11)
ax4.set_title('User Distribution by Cohort', fontsize=13, fontweight='bold')
for bar, users in zip(bars, cohort_df['Users']):
    ax4.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
             f'{int(users):,}', ha='left', va='center')

plt.tight_layout()
plt.savefig('outputs/cohort_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()
print("   ✅ Saved: outputs/cohort_heatmap.png")

# Summary
print("\n📊 COHORT ANALYSIS SUMMARY:")
print("=" * 50)
best_cohort = cohort_df.loc[cohort_df['Upgrade Rate'].idxmax(), 'Cohort']
best_rate = cohort_df['Upgrade Rate'].max()
worst_cohort = cohort_df.loc[cohort_df['Upgrade Rate'].idxmin(), 'Cohort']
worst_rate = cohort_df['Upgrade Rate'].min()

print(f"Best performing cohort: {best_cohort}")
print(f"  → Upgrade rate: {best_rate:.1f}%")
print(f"\nWorst performing cohort: {worst_cohort}")
print(f"  → Upgrade rate: {worst_rate:.1f}%")
print(f"\nAverage upgrade rate: {cohort_df['Upgrade Rate'].mean():.1f}%")
print("=" * 50)

print("\n✅ Step 3 completed! Run 4_segmentation_analysis.py next.")