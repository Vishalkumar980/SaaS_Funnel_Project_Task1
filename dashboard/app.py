import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="SaaS Funnel Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* KPI Card Styling */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .kpi-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ecdc4;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# ========== HEADER WITH CSS ==========
st.markdown("""
<div class="main-header fade-in">
    <h1>📊 SaaS User Behaviour Funnel Analytics</h1>
    <p>Real-time User Journey Analysis & Conversion Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time'])
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found! Please run the analysis scripts first.")
        st.info("Run: python scripts/0_create_sample_data.py")
        return None

df = load_data()

if df is not None:
    # Sidebar with custom styling
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h3>🎛️ Dashboard Controls</h3>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.sidebar.subheader("📢 Acquisition Channel")
    channels = ['All'] + df['acquisition_channel'].unique().tolist()
    selected_channel = st.sidebar.selectbox("Select Channel", channels)
    
    # Apply filters
    filtered_df = df.copy()
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['event_time'].dt.date >= date_range[0]) &
            (filtered_df['event_time'].dt.date <= date_range[1])
        ]
    if selected_channel != 'All':
        filtered_df = filtered_df[filtered_df['acquisition_channel'] == selected_channel]
    
    # Calculate funnel metrics
    funnel_steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
    step_labels = ['Landing', 'Sign-up', 'Onboarding', 'First Feature', 'Upgrade']
    
    funnel_counts = {}
    for step in funnel_steps:
        funnel_counts[step] = filtered_df[filtered_df['event_name'] == step]['user_id'].nunique()
    
    total_users = funnel_counts['landing'] if funnel_counts['landing'] > 0 else 1
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card fade-in">
            <div class="kpi-label">👥 Total Visitors</div>
            <div class="kpi-value">{:,}</div>
        </div>
        """.format(funnel_counts['landing']), unsafe_allow_html=True)
    
    with col2:
        signup_rate = (funnel_counts['signup'] / total_users * 100)
        st.markdown("""
        <div class="kpi-card fade-in">
            <div class="kpi-label">📝 Signup Rate</div>
            <div class="kpi-value">{:.1f}%</div>
        </div>
        """.format(signup_rate), unsafe_allow_html=True)
    
    with col3:
        upgrade_rate = (funnel_counts['upgrade'] / total_users * 100)
        st.markdown("""
        <div class="kpi-card fade-in">
            <div class="kpi-label">💎 Upgrade Rate</div>
            <div class="kpi-value">{:.1f}%</div>
        </div>
        """.format(upgrade_rate), unsafe_allow_html=True)
    
    with col4:
        drop_off = 100 - upgrade_rate
        st.markdown("""
        <div class="kpi-card fade-in">
            <div class="kpi-label">⚠️ Total Drop-off</div>
            <div class="kpi-value">{:.1f}%</div>
        </div>
        """.format(drop_off), unsafe_allow_html=True)
    
    # Funnel Visualization Section
    st.markdown('<div class="section-header fade-in">🎯 Conversion Funnel Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create interactive funnel chart
        funnel_data = []
        for i, step in enumerate(funnel_steps):
            funnel_data.append({
                'stage': step_labels[i],
                'users': funnel_counts[step]
            })
        
        funnel_df_plot = pd.DataFrame(funnel_data)
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df_plot['stage'],
            x=funnel_df_plot['users'],
            textinfo="value+percent previous",
            textposition="inside",
            marker={"color": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6"]},
        ))
        
        fig_funnel.update_layout(
            title="User Conversion Funnel",
            height=500,
            font=dict(size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        # Drop-off analysis
        drop_off_data = []
        for i in range(1, len(funnel_steps)):
            prev_users = funnel_counts[funnel_steps[i-1]]
            curr_users = funnel_counts[funnel_steps[i]]
            if prev_users > 0:
                drop_rate = (prev_users - curr_users) / prev_users * 100
            else:
                drop_rate = 0
            drop_off_data.append({
                'step': step_labels[i],
                'drop_rate': drop_rate
            })
        
        drop_df = pd.DataFrame(drop_off_data)
        
        fig_drop = px.bar(drop_df, x='step', y='drop_rate', 
                          title='Drop-off Rate by Stage',
                          color='drop_rate',
                          color_continuous_scale='Reds')
        fig_drop.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_drop, use_container_width=True)
    
    # Channel Analysis Section
    st.markdown('<div class="section-header fade-in">📊 Channel Performance Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        channel_metrics = []
        for channel in filtered_df['acquisition_channel'].unique():
            channel_data = filtered_df[filtered_df['acquisition_channel'] == channel]
            channel_users = channel_data['user_id'].nunique()
            upgrade_users = channel_data[channel_data['event_name'] == 'upgrade']['user_id'].nunique()
            upgrade_rate = (upgrade_users / channel_users * 100) if channel_users > 0 else 0
            
            channel_metrics.append({
                'Channel': channel,
                'Users': channel_users,
                'Upgrade Rate (%)': upgrade_rate
            })
        
        channel_df = pd.DataFrame(channel_metrics)
        
        fig_channel = px.bar(channel_df, x='Channel', y='Upgrade Rate (%)',
                             title='Upgrade Rate by Channel',
                             color='Channel',
                             text='Upgrade Rate (%)')
        fig_channel.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_channel.update_layout(showlegend=False)
        st.plotly_chart(fig_channel, use_container_width=True)
    
    with col2:
        fig_pie = px.pie(channel_df, values='Users', names='Channel',
                         title='User Distribution by Channel',
                         hole=0.3,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Key Insights Section
    st.markdown('<div class="section-header fade-in">💡 Actionable Insights</div>', unsafe_allow_html=True)
    
    # Calculate insights
    max_drop_idx = drop_df['drop_rate'].idxmax()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-box fade-in">
            <h3>⚠️ Critical Finding</h3>
            <p><strong>{drop_df.loc[max_drop_idx, 'step']}</strong> stage has the highest drop-off rate at <strong>{drop_df.loc[max_drop_idx, 'drop_rate']:.1f}%</strong></p>
            <p><strong>🎯 Action:</strong> Implement targeted interventions at this stage to improve retention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if len(channel_df) > 0:
            best_channel = channel_df.loc[channel_df['Upgrade Rate (%)'].idxmax(), 'Channel']
            best_rate = channel_df['Upgrade Rate (%)'].max()
            st.markdown(f"""
            <div class="success-box fade-in">
                <h3>🏆 Best Performing Channel</h3>
                <p><strong>{best_channel}</strong> channel achieves <strong>{best_rate:.1f}%</strong> upgrade rate</p>
                <p><strong>🎯 Action:</strong> Allocate 40% more budget to {best_channel} marketing</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div class="footer fade-in">
        <p>📊 Dashboard last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🎯 Built with Streamlit | SaaS Funnel Analytics | Data-Driven Decision Making</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data download option
    with st.expander("📄 View Raw Data"):
        st.dataframe(filtered_df.head(100))
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_user_events.csv",
            mime="text/csv"
        )
else:
    st.warning("⚠️ Please run the analysis scripts first to generate the data.")
    st.code("""
    # Run these commands in order:
    python scripts/0_create_sample_data.py
    python scripts/1_data_cleaning.py
    python scripts/2_funnel_analysis.py
    python scripts/3_cohort_analysis.py
    python scripts/4_segmentation_analysis.py
    
    # Then run the dashboard:
    streamlit run dashboard/app.py
    """)