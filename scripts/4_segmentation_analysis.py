import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 50)
print("STEP 4: SEGMENTATION ANALYSIS")
print("=" * 50)

# Load cleaned data
df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time'])

# Define funnel steps
funnel_steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']

# Analyze by acquisition channel
channels = df['acquisition_channel'].unique()

print("\n📊 CHANNEL PERFORMANCE COMPARISON")
print("=" * 60)

channel_results = {}

for channel in channels:
    channel_data = df[df['acquisition_channel'] == channel]
    
    # Calculate funnel for this channel
    funnel_counts = {}
    for step in funnel_steps:
        users_at_step = channel_data[channel_data['event_name'] == step]['user_id'].nunique()
        funnel_counts[step] = users_at_step
    
    total_users = funnel_counts['landing']
    
    if total_users > 0:
        conversion_rates = {
            'Channel': channel,
            'Total Users': total_users,
            'Signup Rate %': round(funnel_counts['signup'] / total_users * 100, 1),
            'Onboarding Rate %': round(funnel_counts['onboarding'] / total_users * 100, 1),
            'Feature Rate %': round(funnel_counts['first_feature_use'] / total_users * 100, 1),
            'Upgrade Rate %': round(funnel_counts['upgrade'] / total_users * 100, 1)
        }
        channel_results[channel] = conversion_rates

channel_df = pd.DataFrame(channel_results).T
print(channel_df.to_string())

# Identify best performing channel
best_channel = channel_df.loc[channel_df['Upgrade Rate %'].idxmax(), 'Channel']
best_rate = channel_df.loc[channel_df['Upgrade Rate %'].idxmax(), 'Upgrade Rate %']
worst_channel = channel_df.loc[channel_df['Upgrade Rate %'].idxmin(), 'Channel']
worst_rate = channel_df.loc[channel_df['Upgrade Rate %'].idxmin(), 'Upgrade Rate %']

print(f"\n🏆 Best channel: {best_channel} ({best_rate}% upgrade rate)")
print(f"📉 Worst channel: {worst_channel} ({worst_rate}% upgrade rate)")

# Visualization - Channel Comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Bar chart - Upgrade rates by channel
ax1 = axes[0, 0]
channels_list = channel_df.index.tolist()
upgrade_rates = channel_df['Upgrade Rate %'].tolist()
bars1 = ax1.bar(channels_list, upgrade_rates, color=['#2ecc71', '#3498db', '#e74c3c'])
ax1.set_title('Upgrade Rate by Acquisition Channel', fontsize=12, fontweight='bold')
ax1.set_ylabel('Upgrade Rate (%)')
ax1.set_ylim(0, max(upgrade_rates) + 10)
for bar, rate in zip(bars1, upgrade_rates):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{rate}%', ha='center', va='bottom', fontweight='bold')

# 2. Funnel comparison for top 2 channels
ax2 = axes[0, 1]
best_data = df[df['acquisition_channel'] == best_channel]
worst_data = df[df['acquisition_channel'] == worst_channel]

def get_funnel_rates(data):
    rates = []
    for i, step in enumerate(funnel_steps):
        if i == 0:
            rates.append(100)
        else:
            prev_users = data[data['event_name'] == funnel_steps[i-1]]['user_id'].nunique()
            curr_users = data[data['event_name'] == step]['user_id'].nunique()
            rate = (curr_users / prev_users * 100) if prev_users > 0 else 0
            rates.append(rate)
    return rates

best_rates = get_funnel_rates(best_data)
worst_rates = get_funnel_rates(worst_data)

x_pos = range(len(funnel_steps))
ax2.plot(x_pos, best_rates, marker='o', linewidth=2, label=best_channel, color='green')
ax2.plot(x_pos, worst_rates, marker='s', linewidth=2, label=worst_channel, color='red')
ax2.set_xticks(x_pos)
ax2.set_xticklabels([step.replace('_', ' ').title() for step in funnel_steps], rotation=45, ha='right')
ax2.set_ylabel('Conversion Rate (%)')
ax2.set_title(f'Funnel Comparison: {best_channel} vs {worst_channel}', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. User distribution by channel
ax3 = axes[1, 0]
user_counts = channel_df['Total Users']
explode = [0.05 if i == user_counts.idxmax() else 0 for i in range(len(channels_list))]
colors_pie = ['#2ecc71', '#3498db', '#e74c3c']
ax3.pie(user_counts, labels=channels_list, autopct='%1.1f%%', startangle=90, 
        explode=explode, colors=colors_pie)
ax3.set_title('User Distribution by Channel', fontsize=12, fontweight='bold')

# 4. Funnel drop-off comparison
ax4 = axes[1, 1]
# Calculate drop-off rates for each step by channel
drop_off_data = {}
for channel in channels:
    channel_data = df[df['acquisition_channel'] == channel]
    drop_off_rates = []
    for i in range(1, len(funnel_steps)):
        prev_users = channel_data[channel_data['event_name'] == funnel_steps[i-1]]['user_id'].nunique()
        curr_users = channel_data[channel_data['event_name'] == funnel_steps[i]]['user_id'].nunique()
        drop_rate = ((prev_users - curr_users) / prev_users * 100) if prev_users > 0 else 0
        drop_off_rates.append(drop_rate)
    drop_off_data[channel] = drop_off_rates

x_pos = range(len(funnel_steps) - 1)
width = 0.25
for i, channel in enumerate(channels):
    offset = (i - 1) * width
    bars = ax4.bar([x + offset for x in x_pos], drop_off_data[channel], 
                   width, label=channel, alpha=0.7)
    # Add percentage labels
    for bar, rate in zip(bars, drop_off_data[channel]):
        if rate > 0:
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{rate:.0f}%', ha='center', va='bottom', fontsize=8)

ax4.set_xticks(x_pos)
ax4.set_xticklabels([f'{funnel_steps[i+1].replace("_", " ").title()}' for i in range(len(funnel_steps)-1)], 
                    rotation=45, ha='right')
ax4.set_ylabel('Drop-off Rate (%)')
ax4.set_title('Drop-off Rates by Funnel Step & Channel', fontsize=12, fontweight='bold')
ax4.legend()
ax4.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('outputs/channel_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ Channel analysis saved to 'outputs/channel_analysis.png'")

# Channel-specific recommendations
print("\n💡 CHANNEL-SPECIFIC INSIGHTS:")
print("-" * 50)

for channel in channels:
    channel_upgrade = channel_df.loc[channel, 'Upgrade Rate %']
    channel_signup = channel_df.loc[channel, 'Signup Rate %']
    
    print(f"\n{channel.upper()}:")
    print(f"  - Upgrade rate: {channel_upgrade}%")
    print(f"  - Signup rate: {channel_signup}%")
    
    if channel == 'Referral':
        if channel_upgrade > 30:
            print("  ✅ Excellent! Referral users have high upgrade rates")
            print("  💡 Action: Invest in referral program expansion")
    elif channel == 'Paid':
        if channel_signup > 70:
            print("  ✅ Good at acquiring users, but check post-signup drop-off")
        if channel_upgrade < 20:
            print("  ⚠️ Low upgrade rate - need retention strategies")
            print("  💡 Action: Implement targeted onboarding for paid channel")
    elif channel == 'Organic':
        if 20 <= channel_upgrade <= 35:
            print("  ✅ Solid performance - stable user base")
            print("  💡 Action: Optimize SEO and content marketing")