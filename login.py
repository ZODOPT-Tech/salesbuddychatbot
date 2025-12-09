import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration (Crucial for full width) ---
# Set the layout to 'wide' to use the maximum horizontal space.
st.set_page_config(
    page_title="No-Scroll Dashboard",
    layout="wide"
)

# --- Define Content Height (Estimate for No-Scroll) ---
# We use this value to set the height of the main scrollable element (the dataframe).
# This is often determined by trial and error based on the height of your header/footer/widgets.
# A value of 500-600px is a common starting point for a data table on a standard laptop screen.
DATA_HEIGHT = 550

st.title("Screen-Fitting Dashboard (No Vertical Scroll)")
st.caption(f"The main data table is limited to {DATA_HEIGHT}px to prevent vertical screen scrolling.")

# --- Generate Sample Data ---
@st.cache_data
def get_data():
    return pd.DataFrame(
        np.random.randn(100, 4),
        columns=['A', 'B', 'C', 'D']
    )

df = get_data()

# --- Create two columns with a ratio of 3:1 ---
col1, col2 = st.columns([3, 1])

# --- Wider Left Container (3/4 of screen) ---
with col1:
    st.header("📈 Primary Content Area")
    st.subheader("Data View (Height-Limited)")

    # The key to no-scroll is limiting the height of large elements.
    # The dataframe will scroll internally, but the app itself won't.
    st.dataframe(
        df,
        use_container_width=True,
        height=DATA_HEIGHT # Set the height to control vertical space
    )

# --- Narrower Right Container (1/4 of screen) ---
with col2:
    st.header("⚙️ Controls & Metrics")
    st.markdown("---")
    
    # Use a container here if you want to apply specific styling or a sidebar feel
    with st.container(border=True):
        st.metric(
            label="Total Rows",
            value=len(df),
            delta="Optimized"
        )
        st.slider("Data Filter Threshold", 0.0, 1.0, 0.5, step=0.01)
        st.selectbox("Select Column", options=df.columns)
        
    st.markdown("---")
    st.info("Space for small chart or brief summary.")

# Note: The main layout is designed to contain all elements above the viewport fold.
# Avoid adding any elements *after* the columns that would push the content down.
