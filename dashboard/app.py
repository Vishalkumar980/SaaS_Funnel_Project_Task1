import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="SaaS Funnel Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 2rem;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
    }
    .insight-critical {
        background: #fee2e2;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .insight-success {
        background: #a7f3d0;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .insight-info {
        background: #dbeafe;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 SaaS User Behaviour Funnel Analytics</h1>
    <p>User Journey Analysis & Conversion Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Load or create data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/cleaned/cleaned_user_events.csv')
        df['event_time'] = pd.to_datetime(df['event_time'])
        return df
    except:
        # Create sample data
        data = []
        for user_id in range(1, 1001):
            signup_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))
            channel = random.choice(['Organic', 'Paid', 'Referral'])
            
            data.append({'user_id': user_id, 'event_name': 'landing', 
                        'event_time': signup_date - timedelta(days=1),
                        'acquisition_channel': channel})
            
            if random.random() < 0.65:
                data.append({'user_id': user_id, 'event_name': 'signup',
                            'event_time': signup_date, 'acquisition_channel': channel})
                
                if random.random() < 0.7:
                    data.append({'user_id': user_id, 'event_name': 'onboarding',
                                'event_time': signup_date + timedelta(days=1),
                                'acquisition_channel': channel})
                    
                    if random.random() < 0.75:
                        data.append({'user_id': user_id, 'event_name': 'first_feature_use',
                                    'event_time': signup_date + timedelta(days=3),
                                    'acquisition_channel': channel})
                        
                        if random.random() < 0.3:
                            data.append({'user_id': user_id, 'event_name': 'upgrade',
                                        'event_time': signup_date + timedelta(days=10),
                                        'acquisition_channel': channel})
        
        df = pd.DataFrame(data)
        df['event_time'] = pd.to_datetime(df['event_time'])
        return df

df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    min_date = df['event_time'].min().date()
    max_date = df['event_time'].max().date()
    date_range = st.date_input("Date Range", [min_date, max_date])
    
    channels = ['All'] + df['acquisition_channel'].unique().tolist()
    selected_channel = st.selectbox("Channel", channels)

# Apply filters
filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['event_time'].dt.date >= date_range[0]) &
        (filtered_df['event_time'].dt.date <= date_range[1])
    ]
if selected_channel != 'All':
    filtered_df = filtered_df[filtered_df['acquisition_channel'] == selected_channel]

# Calculate funnel
steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
labels = ['Landing', 'Sign-up', 'Onboarding', 'Feature Use', 'Upgrade']

counts = {}
for step in steps:
    counts[step] = filtered_df[filtered_df['event_name'] == step]['user_id'].nunique()

total = counts['landing'] if counts['landing'] > 0 else 1

# KPI Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div>👥 Visitors</div>
        <div class="kpi-value">{counts['landing']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    rate = (counts['signup'] / total * 100)
    st.markdown(f"""
    <div class="kpi-card">
        <div>📝 Signup Rate</div>
        <div class="kpi-value">{rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    rate = (counts['upgrade'] / total * 100)
    st.markdown(f"""
    <div class="kpi-card">
        <div>💎 Upgrade Rate</div>
        <div class="kpi-value">{rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    drop = 100 - rate
    st.markdown(f"""
    <div class="kpi-card">
        <div>⚠️ Drop-off</div>
        <div class="kpi-value">{drop:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Funnel Chart
st.markdown('<div class="section-header">🎯 Conversion Funnel</div>', unsafe_allow_html=True)

funnel_data = [{'Stage': labels[i], 'Users': counts[steps[i]]} for i in range(len(steps))]
funnel_df_plot = pd.DataFrame(funnel_data)

fig = go.Figure(go.Funnel(
    y=funnel_df_plot['Stage'],
    x=funnel_df_plot['Users'],
    textinfo="value+percent previous",
    marker={"color": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6"]}
))
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Drop-off Analysis
st.markdown('<div class="section-header">📉 Drop-off Analysis</div>', unsafe_allow_html=True)

drop_data = []
for i in range(1, len(steps)):
    prev_users = counts[steps[i-1]]
    curr_users = counts[steps[i]]
    drop_rate = ((prev_users - curr_users) / prev_users * 100) if prev_users > 0 else 0
    drop_data.append({'Stage': labels[i], 'Drop-off Rate': drop_rate})

drop_df = pd.DataFrame(drop_data)
fig_drop = px.bar(drop_df, x='Stage', y='Drop-off Rate', 
                  title='Drop-off Rate by Stage',
                  color='Drop-off Rate',
                  color_continuous_scale='Reds',
                  text='Drop-off Rate')
fig_drop.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
st.plotly_chart(fig_drop, use_container_width=True)

# Channel Analysis
st.markdown('<div class="section-header">📊 Channel Performance</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    channel_metrics = []
    for channel in filtered_df['acquisition_channel'].unique():
        channel_data = filtered_df[filtered_df['acquisition_channel'] == channel]
        channel_users = channel_data['user_id'].nunique()
        upgrade_users = channel_data[channel_data['event_name'] == 'upgrade']['user_id'].nunique()
        upgrade_rate = (upgrade_users / channel_users * 100) if channel_users > 0 else 0
        channel_metrics.append({'Channel': channel, 'Upgrade Rate': upgrade_rate})
    
    ch_df = pd.DataFrame(channel_metrics)
    fig_bar = px.bar(ch_df, x='Channel', y='Upgrade Rate', 
                     title='Upgrade Rate by Channel',
                     text='Upgrade Rate')
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_pie = px.pie(ch_df, values='Upgrade Rate', names='Channel', 
                     title='Channel Distribution', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# ============================================
# COHORT ANALYSIS - FIXED (NO .dt accessor error)
# ============================================
st.markdown('<div class="section-header">📈 Cohort Analysis</div>', unsafe_allow_html=True)

# Create cohort from signup dates - DIFFERENT APPROACH
# Get first event date for each user as acquisition date
first_events = filtered_df.groupby('user_id')['event_time'].min().reset_index()
first_events.columns = ['user_id', 'acquisition_date']
first_events['cohort'] = first_events['acquisition_date'].dt.strftime('%Y-%m')

# Get upgrade events
upgrades = filtered_df[filtered_df['event_name'] == 'upgrade'][['user_id', 'event_time']]
upgrades.columns = ['user_id', 'upgrade_date']

# Merge
cohort_data = first_events.merge(upgrades, on='user_id', how='left')
cohort_data['upgraded'] = cohort_data['upgrade_date'].notna()

# Calculate cohort metrics
cohort_metrics = []
for cohort in cohort_data['cohort'].unique():
    cohort_users = cohort_data[cohort_data['cohort'] == cohort]
    total_users = len(cohort_users)
    upgraded_users = cohort_users['upgraded'].sum()
    upgrade_rate = (upgraded_users / total_users * 100) if total_users > 0 else 0
    
    cohort_metrics.append({
        'Cohort': cohort,
        'Users': total_users,
        'Upgrade Rate (%)': upgrade_rate
    })

cohort_df_plot = pd.DataFrame(cohort_metrics)
cohort_df_plot = cohort_df_plot.sort_values('Cohort')

if len(cohort_df_plot) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cohort = px.line(cohort_df_plot, x='Cohort', y='Upgrade Rate (%)',
                             title='Cohort Upgrade Rate Trend',
                             markers=True)
        fig_cohort.update_traces(line=dict(color="#667eea", width=3))
        fig_cohort.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cohort, use_container_width=True)
    
    with col2:
        fig_cohort_bar = px.bar(cohort_df_plot.sort_values('Upgrade Rate (%)', ascending=False),
                                x='Cohort', y='Upgrade Rate (%)',
                                title='Cohort Performance',
                                color='Upgrade Rate (%)',
                                color_continuous_scale='Viridis')
        fig_cohort_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cohort_bar, use_container_width=True)
else:
    st.info("No cohort data available")

# Insights
st.markdown('<div class="section-header">💡 Actionable Insights</div>', unsafe_allow_html=True)

# Find biggest drop-off
max_drop_idx = drop_df['Drop-off Rate'].idxmax()
max_stage = drop_df.loc[max_drop_idx, 'Stage']
max_rate = drop_df.loc[max_drop_idx, 'Drop-off Rate']

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="insight-critical">
        <h3>⚠️ Biggest Drop-off Point</h3>
        <p><strong>{max_stage}</strong> stage loses <strong>{max_rate:.1f}%</strong> of users</p>
        <p><strong>Action:</strong> Focus optimization efforts on {max_stage.lower()} experience</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if len(ch_df) > 0:
        best = ch_df.loc[ch_df['Upgrade Rate'].idxmax()]
        st.markdown(f"""
        <div class="insight-success">
            <h3>🏆 Best Channel</h3>
            <p><strong>{best['Channel']}</strong> channel: {best['Upgrade Rate']:.1f}% upgrade rate</p>
            <p><strong>Action:</strong> Increase marketing budget for {best['Channel']}</p>
        </div>
        """, unsafe_allow_html=True)

# Overall
st.markdown(f"""
<div class="insight-info">
    <h3>📊 Summary</h3>
    <p>Overall conversion rate: <strong>{upgrade_rate:.1f}%</strong> | Industry benchmark: 25-30%</p>
    <p>Focus on reducing {max_stage.lower()} drop-off to improve conversion by 15-20%</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="footer">
    <p>📊 Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>🎯 Built with Streamlit | SaaS Funnel Analytics</p>
</div>
""", unsafe_allow_html=True)

# Data download
with st.expander("📄 View Data"):
    st.dataframe(filtered_df.head(100))
    csv = filtered_df.to_csv(index=False)
    st.download_button("Download CSV", csv, "data.csv", "text/csv")