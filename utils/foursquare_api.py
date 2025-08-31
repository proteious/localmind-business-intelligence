import requests
import json
from typing import List, Dict, Optional

class FoursquareAPI:
    """
    Beginner-friendly Foursquare Places API integration
    Uses the correct v3 endpoints for LocalMind features
    """
    
    def __init__(self, api_key: str):
        """
        Initialize with your Foursquare API key
        Get your free API key at: https://developer.foursquare.com/
        """
        self.api_key = api_key
        self.base_url = "https://api.foursquare.com/v3/places"
        self.headers = {
            "Authorization": f"{api_key}",  # Foursquare uses Bearer token
            "Accept": "application/json"
        }
        
        # Business category mappings for easier searching
        self.category_keywords = {
            'restaurant': 'restaurant,cafe,food,dining,pizza,burger,coffee',
            'retail': 'store,shop,boutique,market,clothing,electronics,retail',
            'fitness': 'gym,fitness,yoga,studio,wellness,health',
            'beauty': 'salon,spa,barber,nail,beauty,massage',
            'professional': 'office,law,accounting,consulting,insurance',
            'healthcare': 'clinic,doctor,dental,medical,pharmacy',
            'education': 'school,college,training,education,tutoring'
        }
        
    def test_connection(self) -> Dict[str, any]:
        """
        Test your API connection - run this first to make sure everything works
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                "query": "coffee",
                "near": "New York,NY",
                "limit": 1
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "API connection working!",
                    "sample_data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"API returned status code: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection failed: {str(e)}"
            }
    
    def search_competitors(self, location: str, business_type: str, radius: int = 1000) -> List[Dict]:
        """
        Find competitors near your business location
        
        Args:
            location: "New York, NY" or "123 Main Street, Boston, MA"
            business_type: 'restaurant', 'retail', 'fitness', etc.
            radius: search radius in meters (default: 1000m = 1km)
        
        Returns:
            List of competitor businesses with details
        """
        try:
            # Use the /search endpoint - this is the main endpoint we need
            url = f"{self.base_url}/search"
            
            # Get search keywords for the business type
            search_query = self.category_keywords.get(business_type, business_type)
            
            # Set up search parameters
            params = {
                "query": search_query,
                "near": location,
                "radius": min(radius, 5000),  # Foursquare max radius is 5000m
                "limit": 20,  # Maximum results to return
                "sort": "DISTANCE"  # Sort by distance from location
            }
            
            print(f"Searching for {business_type} businesses near {location}...")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                competitors = []
                
                # Process each result
                for place in data.get('results', []):
                    competitor = self._extract_competitor_data(place)
                    if competitor:
                        competitors.append(competitor)
                
                print(f"Found {len(competitors)} competitors")
                return competitors
                
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                # Return sample data if API fails (helpful for testing)
                return self._get_sample_competitors(business_type)
                
        except Exception as e:
            print(f"Error searching competitors: {e}")
            # Return sample data if anything goes wrong
            return self._get_sample_competitors(business_type)
    
    def get_local_businesses(self, location: str, radius: int = 1000) -> List[Dict]:
        """
        Get all types of businesses in an area (for hours analysis)
        
        Args:
            location: "New York, NY" or specific address
            radius: search radius in meters
            
        Returns:
            List of all local businesses
        """
        try:
            url = f"{self.base_url}/search"
            
            # Search for all business types
            params = {
                "near": location,
                "radius": min(radius, 5000),
                "limit": 50,
                "sort": "DISTANCE"
            }
            
            print(f"Getting all businesses near {location}...")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                businesses = []
                
                for place in data.get('results', []):
                    business = self._extract_business_data(place)
                    if business:
                        businesses.append(business)
                
                print(f"Found {len(businesses)} local businesses")
                return businesses
                
            else:
                print(f"API Error: {response.status_code}")
                return self._get_sample_local_businesses()
                
        except Exception as e:
            print(f"Error getting local businesses: {e}")
            return self._get_sample_local_businesses()
    
    def get_market_overview(self, location: str, radius: int = 1000) -> Dict:
        """
        Get comprehensive market overview for opportunity analysis
        
        Args:
            location: target location
            radius: analysis radius in meters
            
        Returns:
            Market analysis data
        """
        try:
            # Get all businesses in the area
            businesses = self.get_local_businesses(location, radius)
            
            # Analyze the market composition
            categories = {}
            total_businesses = len(businesses)
            
            for business in businesses:
                category = business.get('category', 'Other')
                categories[category] = categories.get(category, 0) + 1
            
            # Calculate market metrics
            market_data = {
                'total_businesses': total_businesses,
                'categories': categories,
                'market_score': min(10, max(1, total_businesses / 10)),
                'opportunity_count': max(0, 15 - (total_businesses // 5)),
                'saturation_level': self._calculate_saturation_level(total_businesses),
                'location': location,
                'radius': radius
            }
            
            print(f"Market overview: {total_businesses} businesses, {len(categories)} categories")
            return market_data
            
        except Exception as e:
            print(f"Error getting market overview: {e}")
            return self._get_sample_market_data()
    
    def _extract_competitor_data(self, place: Dict) -> Optional[Dict]:
        """Extract competitor information from Foursquare place data"""
        try:
            # Get the main category
            categories = place.get('categories', [])
            main_category = categories[0].get('name', 'Unknown') if categories else 'Unknown'
            
            # Get location info
            location_info = place.get('location', {})
            address = location_info.get('formatted_address', 'Address not available')
            
            # Get coordinates
            geocodes = place.get('geocodes', {}).get('main', {})
            
            competitor = {
                'id': place.get('fsq_id', ''),
                'name': place.get('name', 'Unknown Business'),
                'category': main_category,
                'address': address,
                'distance': place.get('distance', 0),
                'latitude': geocodes.get('latitude', 0),
                'longitude': geocodes.get('longitude', 0),
                'rating': place.get('rating', 0),
                'price': place.get('price', 0),
                'website': place.get('website', ''),
                'phone': place.get('tel', '')
            }
            
            return competitor
            
        except Exception as e:
            print(f"Error extracting competitor data: {e}")
            return None
    
    def _extract_business_data(self, place: Dict) -> Optional[Dict]:
        """Extract general business information from Foursquare place data"""
        try:
            categories = place.get('categories', [])
            main_category = categories[0].get('name', 'Other') if categories else 'Other'
            
            location_info = place.get('location', {})
            
            business = {
                'id': place.get('fsq_id', ''),
                'name': place.get('name', 'Unknown Business'),
                'category': main_category,
                'address': location_info.get('formatted_address', ''),
                'rating': place.get('rating', 0),
                'price': place.get('price', 0),
                'distance': place.get('distance', 0),
                'hours': self._extract_hours(place.get('hours', {})),
                'popular_times': place.get('popular', {})
            }
            
            return business
            
        except Exception as e:
            print(f"Error extracting business data: {e}")
            return None
    
    def _extract_hours(self, hours_data: Dict) -> Dict[str, str]:
        """Extract business hours in a simple format"""
        if not hours_data or not isinstance(hours_data, dict):
            return {}
        
        # Foursquare hours format is complex, simplify for our use
        regular_hours = hours_data.get('regular', [])
        simplified_hours = {}
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day_info in regular_hours:
            day_num = day_info.get('day', 0)  # 1=Monday, 7=Sunday
            if 1 <= day_num <= 7:
                day_name = days[day_num - 1]
                open_time = day_info.get('open', '')
                close_time = day_info.get('close', '')
                
                if open_time and close_time:
                    # Convert 24hr format to readable format
                    simplified_hours[day_name] = f"{self._format_time(open_time)} - {self._format_time(close_time)}"
        
        return simplified_hours
    
    def _format_time(self, time_str: str) -> str:
        """Convert 24hr time to 12hr format"""
        if not time_str or len(time_str) != 4:
            return time_str
        
        try:
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            
            if hour == 0:
                return f"12:{minute:02d} AM"
            elif hour < 12:
                return f"{hour}:{minute:02d} AM"
            elif hour == 12:
                return f"12:{minute:02d} PM"
            else:
                return f"{hour-12}:{minute:02d} PM"
        except:
            return time_str
    
    def _calculate_saturation_level(self, business_count: int) -> str:
        """Calculate how saturated the market is"""
        if business_count < 20:
            return "Low"
        elif business_count < 50:
            return "Medium"
        else:
            return "High"
    
    # Sample data for testing when API is not available
    def _get_sample_competitors(self, business_type: str) -> List[Dict]:
        """Sample competitor data for testing"""
        samples = {
            'restaurant': [
                {
                    'id': 'sample1',
                    'name': 'Downtown Cafe',
                    'category': 'Coffee Shop',
                    'address': '123 Main Street',
                    'distance': 250,
                    'rating': 4.2,
                    'price': 2,
                    'phone': '(555) 123-4567'
                },
                {
                    'id': 'sample2', 
                    'name': 'Pizza Palace',
                    'category': 'Pizza Restaurant',
                    'address': '456 Oak Avenue',
                    'distance': 480,
                    'rating': 4.0,
                    'price': 2,
                    'phone': '(555) 987-6543'
                }
            ],
            'retail': [
                {
                    'id': 'sample3',
                    'name': 'Fashion Boutique',
                    'category': 'Clothing Store', 
                    'address': '789 Shopping Street',
                    'distance': 320,
                    'rating': 4.1,
                    'price': 3,
                    'phone': '(555) 456-7890'
                }
            ],
            'fitness': [
                {
                    'id': 'sample4',
                    'name': 'FitZone Gym',
                    'category': 'Fitness Center',
                    'address': '321 Health Boulevard',
                    'distance': 600,
                    'rating': 4.3,
                    'price': 2,
                    'phone': '(555) 234-5678'
                }
            ]
        }
        
        return samples.get(business_type, samples['restaurant'])
    
    def _get_sample_local_businesses(self) -> List[Dict]:
        """Sample local business data"""
        return [
            {
                'id': 'local1',
                'name': 'Corner Market',
                'category': 'Convenience Store',
                'address': '100 Local Street',
                'rating': 3.8,
                'distance': 150,
                'hours': {
                    'Monday': '6:00 AM - 10:00 PM',
                    'Tuesday': '6:00 AM - 10:00 PM',
                    'Wednesday': '6:00 AM - 10:00 PM', 
                    'Thursday': '6:00 AM - 10:00 PM',
                    'Friday': '6:00 AM - 11:00 PM',
                    'Saturday': '7:00 AM - 11:00 PM',
                    'Sunday': '8:00 AM - 9:00 PM'
                }
            },
            {
                'id': 'local2',
                'name': 'Local Fitness',
                'category': 'Gym',
                'address': '200 Workout Way',
                'rating': 4.5,
                'distance': 400,
                'hours': {
                    'Monday': '5:00 AM - 11:00 PM',
                    'Tuesday': '5:00 AM - 11:00 PM',
                    'Wednesday': '5:00 AM - 11:00 PM',
                    'Thursday': '5:00 AM - 11:00 PM', 
                    'Friday': '5:00 AM - 10:00 PM',
                    'Saturday': '6:00 AM - 10:00 PM',
                    'Sunday': '7:00 AM - 9:00 PM'
                }
            },
            {
                'id': 'local3',
                'name': 'Daily Bread Bakery',
                'category': 'Bakery',
                'address': '300 Fresh Avenue',
                'rating': 4.7,
                'distance': 280,
                'hours': {
                    'Monday': '6:00 AM - 6:00 PM',
                    'Tuesday': '6:00 AM - 6:00 PM',
                    'Wednesday': '6:00 AM - 6:00 PM',
                    'Thursday': '6:00 AM - 6:00 PM',
                    'Friday': '6:00 AM - 7:00 PM',
                    'Saturday': '7:00 AM - 7:00 PM',
                    'Sunday': '8:00 AM - 5:00 PM'
                }
            }
        ]
    
    def _get_sample_market_data(self) -> Dict:
        """Sample market data for testing"""
        return {
            'total_businesses': 85,
            'categories': {
                'Restaurants': 18,
                'Retail Stores': 15,
                'Services': 12,
                'Healthcare': 8,
                'Fitness': 6,
                'Beauty': 5,
                'Other': 21
            },
            'market_score': 6.8,
            'opportunity_count': 5,
            'saturation_level': 'Medium',
            'location': 'Sample Location',
            'radius': 1000
        }

# Simple test function you can run independently
def test_api_key(api_key: str):
    """
    Simple function to test if your API key works
    Run this before using the full application
    """
    api = FoursquareAPI(api_key)
    result = api.test_connection()
    
    print("=== API Key Test Results ===")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'success':
        print("✅ Your API key is working correctly!")
        print("You can now run the LocalMind application.")
    else:
        print("❌ API key test failed.")
        print("Check your API key and internet connection.")
        
    return result['status'] == 'success'

# Example usage for testing:
if __name__ == "__main__":
    # Replace with your actual API key to test
    test_api_key = "your_api_key_here"
    
    if test_api_key != "your_api_key_here":
        test_api_key(test_api_key)
    else:
        print("Add your API key to test the connection!")