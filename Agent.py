import pandas as pd
import numpy as np
import re
from geopy.distance import great_circle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
from fuzzywuzzy import fuzz, process

# Load necessary NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load NER model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class ToiletLocatorAgent:
    def __init__(self, data_path=None):
        """
        Initialize the agent with the dataset.
        Args:
            data_path (str): Path to the CSV file containing the toilet and bus stop data.
        """
        # If data_path is provided, load the data
        # For simulation purposes, we'll create a small sample dataset
        if data_path:
            self.df = pd.read_csv(data_path)
        else:
            # Create sample data for testing
            self.df = pd.DataFrame({
                'stop_id': ['BS001', 'BS002', 'BS003', 'BS004', 'BS005'],
                'stop_lat': [28.6129, 28.6229, 28.6329, 28.6429, 28.6529],
                'stop_lon': [77.2295, 77.2395, 77.2495, 77.2595, 77.2695],
                'stop_name': ['Arjun Nagar', 'Karol Bagh', 'Connaught Place', 'Lajpat Nagar', 'Hauz Khas'],
                'nearest_washroom_id': ['PTU-13_001', 'PTU-14_002', 'PTU-15_003', 'PTU-16_004', 'PTU-17_005'],
                'washroom_latitude': [28.6139, 28.6239, 28.6339, 28.6439, 28.6539],
                'washroom_longitude': [77.2305, 77.2405, 77.2505, 77.2605, 77.2705],
                'distance': [150, 200, 100, 180, 120],
                'washroom_address': ['Near Arjun Nagar Market', 'Karol Bagh Metro Station', 'Connaught Place Block A', 'Lajpat Nagar Central Market', 'Hauz Khas Village Entrance']
            })
        
        # Create a stop name index for fast matching
        self.stop_names = self.df['stop_name'].tolist()
        
    def extract_location(self, query):
        """
        Extract location names from user query using NER and fuzzy matching
        Args:
            query (str): User's natural language query
        Returns:
            str: Extracted location name or None
        """
        # Process with SpaCy NER
        doc = nlp(query)
        locations = [ent.text for ent in doc.ents if ent.label_ in ['LOC', 'GPE']]
        
        # If no locations found with NER, try fuzzy matching with stop names
        if not locations:
            # Tokenize the query
            tokens = word_tokenize(query.lower())
            stop_words = set(stopwords.words('english'))
            filtered_tokens = ' '.join([w for w in tokens if w.isalpha() and w not in stop_words])
            
            # Try fuzzy matching with stop names
            best_match = None
            highest_score = 0
            
            for stop_name in self.stop_names:
                score = fuzz.partial_ratio(filtered_tokens, stop_name.lower())
                if score > highest_score and score > 70:  # Threshold of 70%
                    highest_score = score
                    best_match = stop_name
            
            if best_match:
                locations = [best_match]
        
        return locations[0] if locations else None
    
    def find_nearest_toilet(self, location):
        """
        Find the nearest toilet to the given location
        Args:
            location (str): Name of the bus stop or location
        Returns:
            dict: Information about the nearest toilet
        """
        # Find the closest matching bus stop name
        if location not in self.stop_names:
            closest_stop, score = process.extractOne(location, self.stop_names)
            if score < 60:  # Threshold for confidence
                return None
            location = closest_stop
        
        # Get the row for the matching bus stop
        stop_info = self.df[self.df['stop_name'] == location].iloc[0]
        
        return {
            'stop_name': stop_info['stop_name'],
            'stop_lat': stop_info['stop_lat'],
            'stop_lon': stop_info['stop_lon'],
            'washroom_id': stop_info['nearest_washroom_id'],
            'washroom_lat': stop_info['washroom_latitude'],
            'washroom_lon': stop_info['washroom_longitude'],
            'washroom_address': stop_info['washroom_address'],
            'distance': stop_info['distance']
        }
    
    def get_google_maps_link(self, from_lat, from_lon, to_lat, to_lon):
        """
        Generate Google Maps directions link
        Args:
            from_lat, from_lon: Coordinates of starting point
            to_lat, to_lon: Coordinates of destination
        Returns:
            str: Google Maps URL
        """
        return f"https://www.google.com/maps/dir/?api=1&origin={from_lat},{from_lon}&destination={to_lat},{to_lon}&travelmode=walking"
    
    def process_query(self, query):
        """
        Process a natural language query to find the nearest washroom
        Args:
            query (str): User's natural language query
        Returns:
            dict: Response with toilet information and directions
        """
        # Extract location from query
        location = self.extract_location(query)
        
        if not location:
            return {
                'success': False,
                'message': "I couldn't identify a location in your query. Please mention a specific bus stand or area."
            }
        
        # Find nearest toilet
        toilet_info = self.find_nearest_toilet(location)
        
        if not toilet_info:
            return {
                'success': False,
                'message': f"I couldn't find a bus stand matching '{location}' in our database."
            }
        
        # Generate Google Maps link
        maps_link = self.get_google_maps_link(
            toilet_info['stop_lat'], 
            toilet_info['stop_lon'],
            toilet_info['washroom_lat'], 
            toilet_info['washroom_lon']
        )
        
        # Prepare response
        return {
            'success': True,
            'stop_name': toilet_info['stop_name'],
            'stop_lat': toilet_info['stop_lat'],    # Add this line
            'stop_lon': toilet_info['stop_lon'],    # Add this line
            'washroom_id': toilet_info['washroom_id'],
            'washroom_lat': toilet_info['washroom_lat'],
            'washroom_lon': toilet_info['washroom_lon'],
            'washroom_address': toilet_info['washroom_address'],
            'distance': toilet_info['distance'],
            'directions_link': maps_link,
            'message': f"I found a public toilet near {toilet_info['stop_name']} bus stand. It's located at {toilet_info['washroom_address']}, approximately {toilet_info['distance']} meters away. You can use the Google Maps link below for directions."
        }

# Example usage
if __name__ == "__main__":
    agent = ToiletLocatorAgent()
    
    # Test with a few queries
    queries = [
        "Where can I find a toilet near Arjun Nagar?",
        "I need a washroom near Connaught Place",
        "Public toilet close to Hauz Khas please",
        "Where is the nearest washroom from Karol Bagh bus stand?",
        "I'm at Lajpat Nagar, need a toilet urgently"
    ]
    
    for query in queries:
        result = agent.process_query(query)
        print(f"Query: {query}")
        print(f"Response: {result['message']}")
        if result['success']:
            print(f"Directions: {result['directions_link']}")
        print("---")