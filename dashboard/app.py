import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ============================================
# PAGE CONFIGURATION (MUST BE FIRST)
# ============================================
st.set_page_config(
    page_title="SaaS Funnel Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# BEAUTIFUL CSS STYLING
# ============================================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 600;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-size: 1rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .kpi-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Insight Boxes */
    .insight-critical {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .insight-success {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .insight-info {
        background: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-top: 2rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
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
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
<div class="main-header fade-in">
    <h1>📊 SaaS User Behaviour Funnel Analytics</h1>
    <p>Real-time User Journey Analysis & Conversion Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA FUNCTION
# ============================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/cleaned/cleaned_user_events.csv', parse_dates=['event_time'])
        
        # Convert acquisition_month to datetime - FIXED HERE
        if 'acquisition_month' in df.columns:
            df['acquisition_month'] = pd.to_datetime(df['acquisition_month'], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found! Creating sample data...")
        return create_sample_data()

def create_sample_data():
    import random
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    users = []
    
    for user_id in range(1, 1001):
        signup_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))
        channel = np.random.choice(['Organic', 'Paid', 'Referral'], p=[0.5, 0.3, 0.2])
        
        # Landing
        users.append({'user_id': user_id, 'event_name': 'landing', 
                     'event_time': signup_date - timedelta(days=1),
                     'acquisition_channel': channel, 
                     'acquisition_month': signup_date.strftime('%Y-%m')})
        
        # Signup (65% chance)
        if random.random() < 0.65:
            users.append({'user_id': user_id, 'event_name': 'signup',
                         'event_time': signup_date, 
                         'acquisition_channel': channel,
                         'acquisition_month': signup_date.strftime('%Y-%m')})
            
            # Onboarding (70% of signups)
            if random.random() < 0.7:
                users.append({'user_id': user_id, 'event_name': 'onboarding',
                             'event_time': signup_date + timedelta(days=1),
                             'acquisition_channel': channel,
                             'acquisition_month': signup_date.strftime('%Y-%m')})
                
                # Feature use (75% of onboarding)
                if random.random() < 0.75:
                    users.append({'user_id': user_id, 'event_name': 'first_feature_use',
                                 'event_time': signup_date + timedelta(days=3),
                                 'acquisition_channel': channel,
                                 'acquisition_month': signup_date.strftime('%Y-%m')})
                    
                    # Upgrade (30% of feature use)
                    if random.random() < 0.3:
                        users.append({'user_id': user_id, 'event_name': 'upgrade',
                                     'event_time': signup_date + timedelta(days=10),
                                     'acquisition_channel': channel,
                                     'acquisition_month': signup_date.strftime('%Y-%m')})
    
    df = pd.DataFrame(users)
    df['event_time'] = pd.to_datetime(df['event_time'])
    df['acquisition_month'] = pd.to_datetime(df['acquisition_month'], errors='coerce')
    
    return df

# Load data
df = load_data()

if df is None:
    st.warning("⚠️ Unable to load data. Please check your data files.")
    st.stop()

# ============================================
# SIDEBAR FILTERS
# ============================================
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")
    st.markdown("---")
    
    # Date filter
    st.markdown("### 📅 Date Range")
    min_date = df['event_time'].min().date()
    max_date = df['event_time'].max().date()
    date_range = st.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    st.markdown("---")
    
    # Channel filter
    st.markdown("### 📢 Acquisition Channel")
    channels = ['All'] + df['acquisition_channel'].unique().tolist()
    selected_channel = st.selectbox("Select Channel", channels)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This dashboard analyzes user behavior and identifies drop-off points in the conversion funnel.
    
    **Funnel Steps:**
    1. Landing Page
    2. Sign-up
    3. Onboarding
    4. First Feature Use
    5. Upgrade to Paid
    """)

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
steps = ['landing', 'signup', 'onboarding', 'first_feature_use', 'upgrade']
labels = ['Landing', 'Sign-up', 'Onboarding', 'Feature Use', 'Upgrade']

counts = {}
for step in steps:
    counts[step] = filtered_df[filtered_df['event_name'] == step]['user_id'].nunique()

total = counts['landing'] if counts['landing'] > 0 else 1

# ============================================
# KPI ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div class="kpi-label">👥 Total Visitors</div>
        <div class="kpi-value">{counts['landing']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    signup_rate = (counts['signup'] / total * 100)
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div class="kpi-label">📝 Signup Rate</div>
        <div class="kpi-value">{signup_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    upgrade_rate = (counts['upgrade'] / total * 100)
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div class="kpi-label">💎 Upgrade Rate</div>
        <div class="kpi-value">{upgrade_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    drop_off = 100 - upgrade_rate
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div class="kpi-label">⚠️ Total Drop-off</div>
        <div class="kpi-value">{drop_off:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FUNNEL VISUALIZATION
# ============================================
st.markdown('<div class="section-header fade-in">🎯 Conversion Funnel Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Create funnel data
    funnel_data = [{'Stage': labels[i], 'Users': counts[steps[i]]} for i in range(len(steps))]
    funnel_df_plot = pd.DataFrame(funnel_data)
    
    # Create funnel chart
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_df_plot['Stage'],
        x=funnel_df_plot['Users'],
        textinfo="value+percent previous",
        textposition="inside",
        marker={"color": ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#9b59b6"]},
        connector={"line": {"color": "#667eea", "dash": "solid", "width": 3}}
    ))
    
    fig_funnel.update_layout(
        title="User Journey Funnel",
        height=500,
        font=dict(size=12, family="Poppins"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)

with col2:
    # Calculate drop-off rates
    drop_off_data = []
    for i in range(1, len(steps)):
        prev_users = counts[steps[i-1]]
        curr_users = counts[steps[i]]
        if prev_users > 0:
            drop_rate = (prev_users - curr_users) / prev_users * 100
        else:
            drop_rate = 0
        drop_off_data.append({
            'Stage': labels[i],
            'Drop-off Rate': drop_rate
        })
    
    drop_df = pd.DataFrame(drop_off_data)
    
    fig_drop = px.bar(drop_df, x='Stage', y='Drop-off Rate', 
                      title='Drop-off Rate by Stage',
                      color='Drop-off Rate',
                      color_continuous_scale='Reds',
                      text='Drop-off Rate')
    
    fig_drop.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_drop.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_drop, use_container_width=True)

# ============================================
# CHANNEL PERFORMANCE
# ============================================
st.markdown('<div class="section-header fade-in">📊 Channel Performance Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Calculate channel metrics
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
    
    channel_df_plot = pd.DataFrame(channel_metrics)
    
    fig_channel = px.bar(channel_df_plot, x='Channel', y='Upgrade Rate (%)',
                         title='Upgrade Rate by Acquisition Channel',
                         color='Upgrade Rate (%)',
                         color_continuous_scale='Viridis',
                         text='Upgrade Rate (%)')
    
    fig_channel.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_channel.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_channel, use_container_width=True)

with col2:
    fig_pie = px.pie(channel_df_plot, values='Users', names='Channel',
                     title='User Distribution by Channel',
                     hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
    
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

# ============================================
# COHORT ANALYSIS - FIXED VERSION
# ============================================
st.markdown('<div class="section-header fade-in">📈 Cohort Analysis</div>', unsafe_allow_html=True)

# FIX: Check if acquisition_month exists and is datetime
if 'acquisition_month' in filtered_df.columns:
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(filtered_df['acquisition_month']):
        filtered_df['acquisition_month'] = pd.to_datetime(filtered_df['acquisition_month'], errors='coerce')
    
    # Drop rows with null acquisition_month
    cohort_df_clean = filtered_df.dropna(subset=['acquisition_month'])
    
    if len(cohort_df_clean) > 0:
        # Create cohort from year-month
        cohort_df_clean['cohort'] = cohort_df_clean['acquisition_month'].dt.strftime('%Y-%m')
        
        # Calculate cohort metrics
        cohort_metrics = []
        for cohort in cohort_df_clean['cohort'].unique():
            cohort_data = cohort_df_clean[cohort_df_clean['cohort'] == cohort]
            cohort_users = cohort_data['user_id'].nunique()
            upgrade_users = cohort_data[cohort_data['event_name'] == 'upgrade']['user_id'].nunique()
            upgrade_rate = (upgrade_users / cohort_users * 100) if cohort_users > 0 else 0
            
            cohort_metrics.append({
                'Cohort': cohort,
                'Users': cohort_users,
                'Upgrade Rate (%)': upgrade_rate
            })
        
        cohort_df_plot = pd.DataFrame(cohort_metrics)
        cohort_df_plot = cohort_df_plot.sort_values('Cohort')
        
        if len(cohort_df_plot) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_cohort_line = px.line(cohort_df_plot, x='Cohort', y='Upgrade Rate (%)',
                                          title='Cohort Upgrade Rate Trend',
                                          markers=True,
                                          line_shape='linear')
                
                fig_cohort_line.update_traces(line=dict(color="#667eea", width=3),
                                              marker=dict(size=8, color="#764ba2"))
                
                fig_cohort_line.update_layout(
                    xaxis_tickangle=-45,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_cohort_line, use_container_width=True)
            
            with col2:
                fig_cohort_bar = px.bar(cohort_df_plot.sort_values('Upgrade Rate (%)', ascending=False),
                                        x='Cohort', y='Upgrade Rate (%)',
                                        title='Cohort Performance Ranking',
                                        color='Upgrade Rate (%)',
                                        color_continuous_scale='Viridis')
                
                fig_cohort_bar.update_layout(
                    xaxis_tickangle=-45,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_cohort_bar, use_container_width=True)
        else:
            st.info("No cohort data available for the selected filters.")
    else:
        st.info("No valid acquisition month data available for cohort analysis.")
else:
    st.info("Cohort analysis requires 'acquisition_month' column in the data.")

# ============================================
# ACTIONABLE INSIGHTS
# ============================================
st.markdown('<div class="section-header fade-in">💡 Actionable Insights</div>', unsafe_allow_html=True)

# Calculate drop-off rates for insights
drop_rates = []
for i in range(1, len(steps)):
    prev_users = counts[steps[i-1]]
    curr_users = counts[steps[i]]
    drop = ((prev_users - curr_users) / prev_users * 100) if prev_users > 0 else 0
    drop_rates.append(drop)

# Find biggest drop-off
if len(drop_rates) > 0:
    max_drop_idx = drop_rates.index(max(drop_rates))
    max_drop_stage = labels[max_drop_idx + 1]
    max_drop_rate = max(drop_rates)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-critical fade-in">
            <h3>⚠️ Biggest Drop-off Point</h3>
            <p><strong>{max_drop_stage}</strong> stage has the highest drop-off rate at <strong>{max_drop_rate:.1f}%</strong></p>
            <hr>
            <p><strong>🎯 Recommended Action:</strong></p>
            <ul>
                <li>Implement A/B testing at this stage</li>
                <li>Add user guidance and tooltips</li>
                <li>Simplify the process flow</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if len(channel_df_plot) > 0:
            best_channel = channel_df_plot.loc[channel_df_plot['Upgrade Rate (%)'].idxmax(), 'Channel']
            best_rate = channel_df_plot['Upgrade Rate (%)'].max()
            
            st.markdown(f"""
            <div class="insight-success fade-in">
                <h3>🏆 Best Performing Channel</h3>
                <p><strong>{best_channel}</strong> channel achieves <strong>{best_rate:.1f}%</strong> upgrade rate</p>
                <hr>
                <p><strong>🎯 Recommended Action:</strong></p>
                <ul>
                    <li>Increase marketing budget for {best_channel} by 40%</li>
                    <li>Analyze what makes {best_channel} successful</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Overall insight
    st.markdown(f"""
    <div class="insight-info fade-in">
        <h3>📊 Overall Performance Summary</h3>
        <p><strong>Total Visitors:</strong> {counts['landing']:,} | <strong>Total Upgrades:</strong> {counts['upgrade']:,}</p>
        <p><strong>Overall Conversion:</strong> {upgrade_rate:.1f}% | <strong>Industry Benchmark:</strong> 25-30%</p>
        <hr>
        <p><strong>🎯 Strategic Recommendations:</strong></p>
        <ul>
            <li>Focus on reducing {max_drop_stage} drop-off to increase conversion by 15-20%</li>
            <li>Scale {best_channel if len(channel_df_plot) > 0 else 'Referral'} channel for better ROI</li>
            <li>Implement personalized onboarding for high-value segments</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown(f"""
<div class="footer fade-in">
    <p>📊 Dashboard last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>🎯 Built with Streamlit | Data-Driven Decision Making | SaaS Analytics</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# DATA DOWNLOAD SECTION
# ============================================
with st.expander("📄 View & Download Raw Data"):
    st.dataframe(filtered_df.head(100))
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_user_events.csv",
        mime="text/csv"
    )