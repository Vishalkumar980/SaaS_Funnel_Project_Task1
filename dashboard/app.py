import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="SaaS Funnel Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 SaaS User Behaviour Funnel Analytics Dashboard")
st.markdown("*Real-time User Journey Analysis & Conversion Optimization*")

# Sidebar
st.sidebar.header("🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time'])
    return df

df = load_data()

# Date range filter
st.sidebar.subheader("📅 Date Range")
min_date = df['event_time'].min().date()
max_date = df['event_time'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Channel filter
st.sidebar.subheader("📢 Channel")
channels = ['All'] + df['acquisition_channel'].unique().tolist()
selected_channel = st.sidebar.selectbox("Select Channel", channels)

# Cohort filter
st.sidebar.subheader("📆 Cohort")
cohorts = ['All'] + sorted(df['cohort'].dropna().unique().astype(str).tolist())
selected_cohort = st.sidebar.selectbox("Select Cohort", cohorts)

# Apply filters
filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['event_time'].dt.date >= date_range[0]) &
        (filtered_df['event_time'].dt.date <= date_range[1])
    ]
if selected_channel != 'All':
    filtered_df = filtered_df[filtered_df['acquisition_channel'] == selected_channel]
if selected_cohort != 'All':
    filtered_df = filtered_df[filtered_df['cohort'].astype(str) == selected_cohort]

# Main dashboard
st.markdown("---")

# KPI Row
col1, col2, col3, col4 = st.columns(4)

# Calculate funnel
funnel_steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
funnel_counts = {}
for step in funnel_steps:
    users = filtered_df[filtered_df['event_name'] == step]['user_id'].nunique()
    funnel_counts[step] = users

total_users = funnel_counts['landing'] if funnel_counts['landing'] > 0 else 1

with col1:
    st.metric(
        "👥 Total Users",
        f"{funnel_counts['landing']:,}",
        delta=None
    )

with col2:
    signup_rate = (funnel_counts['signup'] / total_users * 100)
    st.metric(
        "📝 Signup Rate",
        f"{signup_rate:.1f}%",
        delta=f"{signup_rate - 65:.1f}%" if signup_rate != 65 else None
    )

with col3:
    upgrade_rate = (funnel_counts['upgrade'] / total_users * 100)
    st.metric(
        "💎 Upgrade Rate",
        f"{upgrade_rate:.1f}%",
        delta=f"{upgrade_rate - 20:.1f}%" if upgrade_rate != 20 else None
    )

with col4:
    drop_off = 100 - upgrade_rate
    st.metric(
        "⚠️ Total Drop-off",
        f"{drop_off:.1f}%",
        delta=None
    )

st.markdown("---")

# Funnel Visualization
st.header("🎯 Conversion Funnel Analysis")

# Create funnel chart using plotly
fig_funnel = go.Figure()

# Prepare funnel data
funnel_data = []
for step in funnel_steps:
    funnel_data.append({
        'stage': step.replace('_', ' ').title(),
        'users': funnel_counts[step]
    })

funnel_df_plot = pd.DataFrame(funnel_data)

fig_funnel.add_trace(go.Funnel(
    name='User Journey',
    y=funnel_df_plot['stage'],
    x=funnel_df_plot['users'],
    textinfo="value+percent previous",
    textposition="inside",
    marker={"color": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6"]},
    connector={"line": {"color": "royalblue", "dash": "solid", "width": 3}},
))

fig_funnel.update_layout(
    title="User Conversion Funnel",
    width=800,
    height=500,
    font=dict(size=12)
)

col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig_funnel, use_container_width=True)

with col2:
    # Drop-off analysis
    st.subheader("📉 Drop-off Analysis")
    drop_off_data = []
    for i in range(1, len(funnel_steps)):
        prev_users = funnel_counts[funnel_steps[i-1]]
        curr_users = funnel_counts[funnel_steps[i]]
        if prev_users > 0:
            drop_rate = (prev_users - curr_users) / prev_users * 100
        else:
            drop_rate = 0
        drop_off_data.append({
            'step': funnel_steps[i].replace('_', ' ').title(),
            'drop_rate': drop_rate
        })
    
    drop_df = pd.DataFrame(drop_off_data)
    
    fig_drop = px.bar(drop_df, x='step', y='drop_rate', 
                      title='Drop-off Rate by Stage',
                      color='drop_rate',
                      color_continuous_scale='Reds')
    fig_drop.update_layout(showlegend=False)
    st.plotly_chart(fig_drop, use_container_width=True)

st.markdown("---")

# Cohort Analysis Section
st.header("📈 Cohort Analysis")

# Calculate cohort metrics
def get_cohort_data(data):
    cohort_metrics = []
    for cohort in data['cohort'].dropna().unique():
        cohort_data = data[data['cohort'] == cohort]
        cohort_users = cohort_data['user_id'].nunique()
        
        upgrade_users = cohort_data[cohort_data['event_name'] == 'upgrade']['user_id'].nunique()
        
        if cohort_users > 0:
            upgrade_rate = upgrade_users / cohort_users * 100
        else:
            upgrade_rate = 0
            
        cohort_metrics.append({
            'Cohort': str(cohort),
            'Users': cohort_users,
            'Upgrade Rate': upgrade_rate
        })
    
    return pd.DataFrame(cohort_metrics)

cohort_df = get_cohort_data(filtered_df)

col1, col2 = st.columns(2)

with col1:
    # Cohort trend line
    fig_cohort_line = px.line(cohort_df, x='Cohort', y='Upgrade Rate',
                              title='Cohort Upgrade Rate Trend',
                              markers=True)
    fig_cohort_line.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_cohort_line, use_container_width=True)

with col2:
    # Cohort bar chart
    fig_cohort_bar = px.bar(cohort_df.sort_values('Upgrade Rate', ascending=False),
                            x='Cohort', y='Upgrade Rate',
                            title='Cohort Performance Ranking',
                            color='Upgrade Rate',
                            color_continuous_scale='Viridis')
    fig_cohort_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_cohort_bar, use_container_width=True)

st.markdown("---")

# Channel Segmentation
st.header("🎯 Channel Performance Analysis")

channel_metrics = []
for channel in filtered_df['acquisition_channel'].unique():
    channel_data = filtered_df[filtered_df['acquisition_channel'] == channel]
    channel_users = channel_data['user_id'].nunique()
    upgrade_users = channel_data[channel_data['event_name'] == 'upgrade']['user_id'].nunique()
    
    if channel_users > 0:
        upgrade_rate = upgrade_users / channel_users * 100
    else:
        upgrade_rate = 0
    
    channel_metrics.append({
        'Channel': channel,
        'Users': channel_users,
        'Upgrade Rate (%)': upgrade_rate
    })

channel_df = pd.DataFrame(channel_metrics)

col1, col2 = st.columns(2)

with col1:
    fig_channel_bar = px.bar(channel_df, x='Channel', y='Upgrade Rate (%)',
                             title='Upgrade Rate by Channel',
                             color='Channel',
                             text='Upgrade Rate (%)')
    fig_channel_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_channel_bar, use_container_width=True)

with col2:
    fig_channel_pie = px.pie(channel_df, values='Users', names='Channel',
                             title='User Distribution by Channel',
                             hole=0.3)
    st.plotly_chart(fig_channel_pie, use_container_width=True)

st.markdown("---")

# Detailed Insights Section
st.header("💡 Actionable Insights")

# Calculate key insights
insights = []

# Find biggest drop-off
max_drop_idx = drop_df['drop_rate'].idxmax()
insights.append({
    'type': 'critical',
    'title': 'Biggest Drop-off Point',
    'description': f"**{drop_df.loc[max_drop_idx, 'step']}** stage has the highest drop-off rate at **{drop_df.loc[max_drop_idx, 'drop_rate']:.1f}%**",
    'action': "Implement targeted interventions at this stage to improve retention"
})

# Channel insights
if len(channel_df) > 0:
    best_channel = channel_df.loc[channel_df['Upgrade Rate (%)'].idxmax(), 'Channel']
    best_rate = channel_df['Upgrade Rate (%)'].max()
    insights.append({
        'type': 'success',
        'title': 'Best Performing Channel',
        'description': f"**{best_channel}** channel achieves **{best_rate:.1f}%** upgrade rate",
        'action': f"Allocate 40% more budget to {best_channel} marketing"
    })

# Cohort trend
if len(cohort_df) > 1:
    if cohort_df.iloc[-1]['Upgrade Rate'] > cohort_df.iloc[0]['Upgrade Rate']:
        insights.append({
            'type': 'positive',
            'title': 'Improving Trend',
            'description': f"Latest cohort shows **{cohort_df.iloc[-1]['Upgrade Rate'] - cohort_df.iloc[0]['Upgrade Rate']:.1f}%** improvement vs earliest cohort",
            'action': "Continue current product improvements and onboarding flow"
        })
    else:
        insights.append({
            'type': 'warning',
            'title': 'Declining Trend',
            'description': f"Conversion rates dropping by **{cohort_df.iloc[0]['Upgrade Rate'] - cohort_df.iloc[-1]['Upgrade Rate']:.1f}%** over time",
            'action': "Urgently investigate recent changes to product/onboarding"
        })

# Display insights in columns
for i, insight in enumerate(insights):
    if insight['type'] == 'critical':
        st.error(f"⚠️ **{insight['title']}**\n\n{insight['description']}\n\n**Action:** {insight['action']}")
    elif insight['type'] == 'warning':
        st.warning(f"📉 **{insight['title']}**\n\n{insight['description']}\n\n**Action:** {insight['action']}")
    elif insight['type'] == 'positive':
        st.info(f"📈 **{insight['title']}**\n\n{insight['description']}\n\n**Action:** {insight['action']}")
    else:
        st.success(f"✅ **{insight['title']}**\n\n{insight['description']}\n\n**Action:** {insight['action']}")

st.markdown("---")

# Raw Data Viewer
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_user_events.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Dashboard last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))