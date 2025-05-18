import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Agent import ToiletLocatorAgent

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Usable Public Toilet Locator",
    page_icon="🚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E88E5 !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #424242 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
    .blue-text {
        color: #1976D2;
    }
    .result-area {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
    }
    .success-area {
        background-color: #E8F5E9;
        border: 1px solid #C8E6C9;
    }
    .error-area {
        background-color: #FFEBEE;
        border: 1px solid #FFCDD2;
    }
    .info-text {
        font-size: 0.9rem;
        color: #616161;
    }
    .demo-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .map-container {
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>Usable Public Toilet Locator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'>Find hygienic public toilets near bus stands using natural language queries</p>", 
            unsafe_allow_html=True)

# Initialize agent
@st.cache_resource
def load_agent():
    data_path = os.getenv("DATA_PATH", None)
    return ToiletLocatorAgent(data_path=data_path)

agent = load_agent()

# Sidebar
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2016/03/31/14/37/bathroom-1292857_960_720.png", width=100)
    st.markdown("## About UPTL")
    st.info(
        "The Usable Public Toilet Locator (UPTL) helps citizens locate clean "
        "and accessible public toilets. This AI-powered tool understands natural "
        "language queries to find the most convenient facilities."
    )
    
    st.markdown("## How to use")
    st.markdown(
        "1. Type a query like 'Find toilet near Connaught Place'\n"
        "2. Get information about the nearest toilet\n"
        "3. View the location on the map\n"
        "4. Follow Google Maps directions to get there"
    )
    
    st.markdown("## Features")
    st.markdown(
        "- Natural language understanding\n"
        "- Precise toilet location mapping\n"
        "- Walking directions via Google Maps\n"
        "- Information about toilet facilities"
    )

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<h2 class='sub-header'>Find a Public Toilet</h2>", unsafe_allow_html=True)
    
    query = st.text_input(
        "Enter your query in natural language:",
        placeholder="Example: I need a washroom near Connaught Place",
        help="Try mentioning a specific location or bus stand in your query"
    )
    
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        search_button = st.button("Search", type="primary", use_container_width=True)
    with col_btn2:
        st.markdown("<p class='info-text'>Our AI will understand your query and find the nearest toilet</p>", 
                    unsafe_allow_html=True)
    
    # Example queries
    st.markdown("<p class='info-text'>Try these example queries:</p>", unsafe_allow_html=True)
    example_queries = [
        "Where can I find a toilet near Arjun Nagar?",
        "I need a washroom near Connaught Place",
        "Public toilet close to Hauz Khas please",
        "Washroom near Lajpat Nagar"
    ]
    
    col1, col2 = st.columns(2)
    if col1.button(example_queries[0], use_container_width=True):
        query = example_queries[0]
        search_button = True
    if col2.button(example_queries[1], use_container_width=True):
        query = example_queries[1]
        search_button = True
    
    col1, col2 = st.columns(2)
    if col1.button(example_queries[2], use_container_width=True):
        query = example_queries[2]
        search_button = True
    if col2.button(example_queries[3], use_container_width=True):
        query = example_queries[3]
        search_button = True

with col2:
    st.markdown("<h2 class='sub-header'>How It Works</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Natural Language Processing")
    st.markdown(
        "Our AI-powered agent extracts location information from your query "
        "using Named Entity Recognition and fuzzy matching algorithms."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Location Matching")
    st.markdown(
        "We find the bus stand closest to your mentioned location "
        "and identify the nearest public toilet facility."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📍 Precise Directions")
    st.markdown(
        "Get walking directions via Google Maps from the bus stand "
        "to the public toilet with our integrated navigation system."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Process query when button is clicked
if search_button and query:
    st.markdown("<h2 class='sub-header'>Results</h2>", unsafe_allow_html=True)
    
    with st.spinner("Searching for the nearest toilet..."):
        result = agent.process_query(query)
    
    # Display results
    if result['success']:
        st.markdown(f"<div class='result-area success-area'>", unsafe_allow_html=True)
        st.markdown(f"### 🚽 Found a Public Toilet!")
        st.markdown(result['message'])
        
        # Create two columns for details and map
        col_details, col_map = st.columns([1, 1])
        
        with col_details:
            st.markdown("#### Toilet Details")
            st.markdown(f"**Bus Stand:** {result['stop_name']}")
            st.markdown(f"**Toilet ID:** {result['washroom_id']}")
            st.markdown(f"**Location:** {result['washroom_address']}")
            st.markdown(f"**Distance:** {result['distance']} meters")
            
            # Google Maps direction button
            st.markdown(f"[Get Directions on Google Maps]({result['directions_link']})")
        
        with col_map:
            # Create a folium map centered at the bus stop
            m = folium.Map(
                location=[result['stop_lat'], result['stop_lon']], 
                zoom_start=16
            )
            
            # Add marker for the bus stop
            folium.Marker(
                [result['stop_lat'], result['stop_lon']],
                popup=f"Bus Stand: {result['stop_name']}",
                tooltip=result['stop_name'],
                icon=folium.Icon(color='blue', icon='bus', prefix='fa')
            ).add_to(m)
            
            # Add marker for the toilet
            folium.Marker(
                [result['washroom_lat'], result['washroom_lon']],
                popup=f"Toilet: {result['washroom_address']}",
                tooltip="Public Toilet",
                icon=folium.Icon(color='green', icon='toilet', prefix='fa')
            ).add_to(m)
            
            # Add a line connecting them
            folium.PolyLine(
                locations=[
                    [result['stop_lat'], result['stop_lon']],
                    [result['washroom_lat'], result['washroom_lon']]
                ],
                color='blue',
                weight=2,
                opacity=0.7,
                dash_array='5'
            ).add_to(m)
            
            # Display the map
            st.markdown("<div class='map-container'>", unsafe_allow_html=True)
            folium_static(m)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='result-area error-area'>", unsafe_allow_html=True)
        st.markdown("### 😕 No Results Found")
        st.markdown(result['message'])
        st.markdown(
            "Try refining your query by mentioning a specific bus stand or area. "
            "You can also try one of the example queries provided."
        )
        st.markdown("</div>", unsafe_allow_html=True)

# Bottom information section
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>About the Project</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Goal")
    st.markdown(
        "Our goal is to make public sanitation facilities more accessible to everyone, "
        "helping to improve public health and comfort in urban areas."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 AI-Powered")
    st.markdown(
        "The agent uses advanced natural language processing and location matching "
        "algorithms to understand complex queries and provide accurate results."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📱 Mobile Friendly")
    st.markdown(
        "Access the toilet locator on your mobile device while traveling "
        "to quickly find the nearest clean public toilet facilities."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<p style='text-align: center; margin-top: 3rem;'>© 2025 Top Notch Navaacharan - Usable Public Toilet Locator Project</p>", unsafe_allow_html=True)