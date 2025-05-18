# Toilet Locator Agent - Installation and Usage Guide

## System Requirements

- Python 3.9+ 
- Sufficient disk space for language models (~100MB for spaCy models)
- Internet connection (for initial setup and Google Maps integration)

## Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/your-repo/toilet-locator-agent.git
   cd toilet-locator-agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download required language models**:
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords
   ```

5. **Prepare your dataset**:
   - Ensure your dataset has the following columns:
     - `stop_id`: Unique identifier for bus stops
     - `stop_lat`: Latitude of bus stop
     - `stop_lon`: Longitude of bus stop
     - `stop_name`: Name of the bus stop
     - `nearest_washroom_id`: ID of nearest washroom
     - `washroom_latitude`: Latitude of washroom
     - `washroom_longitude`: Longitude of washroom
     - `distance`: Distance from bus stop to washroom in meters
     - `washroom_address`: Address of the washroom

## Usage as a Standalone Agent

```python
from toilet_locator_agent import ToiletLocatorAgent

# Initialize with your data
agent = ToiletLocatorAgent(data_path='path/to/your/data.csv')

# Process a query
result = agent.process_query("Where can I find a toilet near Connaught Place?")

# Access the result
if result['success']:
    print(f"Found washroom: {result['washroom_address']}")
    print(f"Distance: {result['distance']} meters")
    print(f"Directions: {result['directions_link']}")
else:
    print(f"Error: {result['message']}")
```

## Deploying as an API Service

1. **Create a FastAPI server**:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from toilet_locator_agent import ToiletLocatorAgent

app = FastAPI(title="Toilet Locator API")
agent = ToiletLocatorAgent(data_path='path/to/your/data.csv')

class QueryRequest(BaseModel):
    query: str

@app.post("/locate")
async def locate_toilet(request: QueryRequest):
    result = agent.process_query(request.query)
    return result

# Run with: uvicorn app:app --reload
```

2. **Start the server**:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Integration with Web/Mobile Applications

### REST API

Make HTTP requests to your deployed API:

```javascript
// Example JavaScript fetch
async function findToilet(query) {
  const response = await fetch('http://your-api-url/locate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  
  return await response.json();
}

// Usage
findToilet("I need a washroom near Hauz Khas")
  .then(result => {
    if (result.success) {
      console.log(`Found: ${result.washroom_address}`);
      window.open(result.directions_link);
    } else {
      console.error(result.message);
    }
  });
```

### Streamlit Demo App

You can also run a quick demo with Streamlit:

```python
# Save as streamlit_app.py
import streamlit as st
from toilet_locator_agent import ToiletLocatorAgent

st.title("Usable Public Toilet Locator")

agent = ToiletLocatorAgent(data_path='path/to/your/data.csv')

query = st.text_input("Where do you need to find a toilet?", 
                      "Find toilet near Connaught Place")

if st.button("Search"):
    result = agent.process_query(query)
    
    if result['success']:
        st.success(result['message'])
        
        st.subheader("Details:")
        st.write(f"**Bus Stand:** {result['stop_name']}")
        st.write(f"**Toilet ID:** {result['washroom_id']}")
        st.write(f"**Address:** {result['washroom_address']}")
        st.write(f"**Distance:** {result['distance']} meters")
        
        st.markdown(f"[Get Directions on Google Maps]({result['directions_link']})")
    else:
        st.error(result['message'])
```

Run with:
```bash
streamlit run streamlit_app.py
```

## Configuration Options

You can customize the agent behavior by modifying parameters during initialization:

```python
agent = ToiletLocatorAgent(
    data_path='path/to/your/data.csv',
    fuzzy_match_threshold=70,  # Minimum score (0-100) for fuzzy matching
    max_distance=2000,         # Maximum distance in meters to consider
    consider_reviews=True      # Whether to factor in reviews (if you have review data)
)
```

## Troubleshooting

1. **NER model issues**: If you encounter errors with the spaCy model, try:
   ```bash
   python -m spacy validate
   # If needed, reinstall: 
   python -m spacy download en_core_web_sm --force
   ```

2. **Location not recognized**: The agent uses both NER and fuzzy matching. Try using more specific location names in queries.

3. **Performance issues**: For large datasets, consider:
   - Adding spatial indexing
   - Implementing caching for frequent queries
   - Pre-filtering data by geographic region before processing

## Extending the Agent

To add custom functionality:

1. **Enhanced location extraction**:
   - Extend the `extract_location` method to handle more complex queries
   - Add custom location aliases or landmarks

2. **Additional data sources**:
   - Modify the agent to pull real-time cleanliness ratings
   - Integrate with occupancy sensors if available

3. **Feedback mechanism**:
   - Add methods to collect and incorporate user feedback
