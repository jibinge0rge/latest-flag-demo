import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="Latest Flag Logic Demo",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode styling
st.markdown("""
<style>
    .main {
        background-color: #0D1117;
        color: #E0E6ED;
    }
    .stApp {
        background-color: #0D1117;
    }
    .stDataFrame {
        background-color: #161B22;
    }
    .metric-card {
        background-color: #161B22;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #30363D;
    }
    .header-section {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .step-section {
        background-color: #161B22;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #30363D;
        margin: 1rem 0;
    }
    .success-animation {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def highlight_duplicates(val):
    """Highlight duplicate hostnames"""
    if val in st.session_state.get('duplicate_hostnames', []):
        return 'background-color: #FF6B6B; color: white'
    return ''

def highlight_flag(val):
    """Highlight latest flag values"""
    if val == 1:
        return 'background-color: #2D5A2D; color: #E0E6ED; font-weight: bold'
    elif val == 0:
        return 'background-color: #3C4043; color: #E0E6ED'
    return ''

def load_data():
    """Load and process the CSV data"""
    try:
        # Try different encodings to handle the file properly
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('sample.csv', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            st.error("❌ Could not load data with any supported encoding")
            return None
        
        # Clean the data
        df['Last_Active (UTC)'] = pd.to_datetime(df['Last_Active (UTC)'], dayfirst=True, errors='coerce')
        
        # Find duplicate hostnames for highlighting
        hostname_counts = df['Hostname'].value_counts()
        duplicate_hostnames = hostname_counts[hostname_counts > 1].index.tolist()
        st.session_state['duplicate_hostnames'] = duplicate_hostnames
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def apply_latest_flag_logic(df):
    """Apply the latest flag logic to the dataframe"""
    # Create a copy to avoid modifying the original
    df_flagged = df.copy()
    
    # Apply latest flag logic
    df_flagged['latest_flag'] = df_flagged.groupby(['Hostname', 'FQDN'])['Last_Active (UTC)'].transform(
        lambda x: (x == x.max()).astype(int)
    )
    
    return df_flagged

def main():
    # Header Section
    st.markdown("""
    <div class="header-section">
        <h1>🏁 Latest Flag Logic – Host Deduplication in CrowdStrike Data</h1>
        <p style="font-size: 1.2rem; color: #8B949E; margin-top: 1rem;">
            Interactive demo of how timestamp-based flagging removes duplicates and retains the latest host record.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'df_flagged' not in st.session_state:
        st.session_state.df_flagged = None
    if 'df_clean' not in st.session_state:
        st.session_state.df_clean = None
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Show Raw Dataset
    st.markdown("## 📊 Step 1: Raw Dataset with Duplicates")
    
    with st.expander("🔍 See Raw Data", expanded=True):
        st.markdown("**Raw host data showing duplicate entries:**")
        
        # Display raw data with duplicate highlighting
        st.dataframe(
            df.style.applymap(highlight_duplicates, subset=['Hostname']),
            use_container_width=True,
            hide_index=False
        )
        
        # Show duplicate summary
        duplicate_count = len(st.session_state.get('duplicate_hostnames', []))
        st.info(f"🔍 Found {duplicate_count} hostnames with duplicates")
    
    # Step 2: Explain Logic
    st.markdown("## 🧠 Step 2: Latest Flag Logic Explanation")
    
    st.markdown("""
    <div class="step-section">
        <h4>📋 Pseudo-Algorithm:</h4>
        <ol>
            <li><strong>For each Hostname + FQDN combination:</strong></li>
            <ul>
                <li>Compare all "Last Active" timestamps</li>
                <li>Mark the latest record as <code>latest_flag = 1</code></li>
                <li>Mark all others as <code>latest_flag = 0</code></li>
                <li>If timestamps are missing or identical → mark all as <code>1</code></li>
            </ul>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Apply logic button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Apply Latest Flag Logic", type="primary", use_container_width=True):
            with st.spinner("Applying latest flag logic..."):
                time.sleep(1)  # Simulate processing time
                st.session_state.df_flagged = apply_latest_flag_logic(df)
                st.session_state.step = 1
    
    # Step 3: Show Flagged Data
    if st.session_state.df_flagged is not None:
        st.markdown("## 🎯 Step 3: Flagged Data with Color Coding")
        
        st.markdown("""
        <div style="background-color: #161B22; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
            <p><strong>Color Legend:</strong></p>
            <p>🟢 <strong>Green:</strong> Latest record (flag = 1)</p>
            <p>⚪ <strong>Gray:</strong> Older record (flag = 0)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display flagged data with color coding
        st.dataframe(
            st.session_state.df_flagged.style.applymap(highlight_flag, subset=['latest_flag']),
            use_container_width=True,
            hide_index=False
        )
        
        # Step 4: Filter Clean Dataset
        st.markdown("## 🧹 Step 4: Clean Dataset (Latest Records Only)")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Show Clean Dataset", type="secondary", use_container_width=True):
                st.session_state.df_clean = st.session_state.df_flagged[st.session_state.df_flagged['latest_flag'] == 1].reset_index(drop=True)
                st.session_state.step = 2
        
        if st.session_state.df_clean is not None:
            # Display clean data without scroll
            st.dataframe(
                st.session_state.df_clean, 
                use_container_width=True, 
                hide_index=False
            )
            
            # Metrics - properly aligned
            st.markdown("### 📊 Summary Statistics")
            
            # Use equal spacing with proper alignment
            col1, col2, col3 = st.columns(3, gap="large")
            
            with col1:
                st.metric(
                    label="📊 Total Raw Entries",
                    value=len(df),
                    delta=None
                )
            with col2:
                st.metric(
                    label="✅ Cleaned Hosts", 
                    value=len(st.session_state.df_clean),
                    delta=f"-{len(df) - len(st.session_state.df_clean)} duplicates"
                )
            with col3:
                st.metric(
                    label="📈 Deduplication Rate",
                    value=f"{((len(df) - len(st.session_state.df_clean)) / len(df) * 100):.1f}%",
                    delta="duplicates removed"
                )
            
    
    # Update progress
    if st.session_state.step == 0:
        progress_bar.progress(0.2)
        status_text.text("📊 Showing raw data...")
    elif st.session_state.step == 1:
        progress_bar.progress(0.6)
        status_text.text("🎯 Flagging latest records...")
    elif st.session_state.step == 2:
        progress_bar.progress(1.0)
        status_text.text("✅ Demo complete!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8B949E; padding: 2rem 0;">
        <p><strong>Latest Flag Logic</strong> — Turning CrowdStrike chaos into clarity.</p>
        <p>By analyzing timestamp recency, we keep only the most accurate host record.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
