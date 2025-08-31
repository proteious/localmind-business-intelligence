import json
import math
import statistics
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class DataProcessor:
    """Data processing utilities for LocalMind Business Intelligence"""
    
    def __init__(self):
        self.business_categories = {
            'restaurant': ['restaurant', 'cafe', 'bar', 'food', 'dining', 'pizza', 'burger', 'coffee'],
            'retail': ['store', 'shop', 'boutique', 'market', 'mall', 'clothing', 'electronics'],
            'fitness': ['gym', 'fitness', 'yoga', 'studio', 'wellness', 'health club', 'crossfit'],
            'beauty': ['salon', 'spa', 'barber', 'nail', 'beauty', 'cosmetics', 'massage'],
            'professional': ['office', 'law', 'accounting', 'consulting', 'real estate', 'insurance'],
            'healthcare': ['clinic', 'doctor', 'dental', 'medical', 'pharmacy', 'hospital'],
            'education': ['school', 'college', 'university', 'training', 'education', 'tutoring']
        }
        
        self.peak_hour_patterns = {
            'restaurant': {
                'breakfast': (7, 10),
                'lunch': (11, 14),
                'dinner': (17, 21),
                'late_night': (21, 24)
            },
            'retail': {
                'morning': (10, 12),
                'afternoon': (14, 17),
                'evening': (18, 20)
            },
            'fitness': {
                'early_morning': (5, 8),
                'lunch': (11, 14),
                'evening': (17, 21)
            }
        }
    
    def clean_location_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Clean and standardize location data from API responses"""
        cleaned_data = []
        
        for item in raw_data:
            if not item or not isinstance(item, dict):
                continue
                
            cleaned_item = {
                'id': item.get('id', ''),
                'name': self._clean_text(item.get('name', 'Unknown Business')),
                'category': self._standardize_category(item.get('category', 'Other')),
                'address': self._clean_address(item.get('address', '')),
                'distance': self._validate_distance(item.get('distance', 0)),
                'rating': self._validate_rating(item.get('rating', 0)),
                'latitude': self._validate_coordinate(item.get('latitude', 0)),
                'longitude': self._validate_coordinate(item.get('longitude', 0)),
                'price_level': item.get('price_level', 0),
                'phone': self._clean_phone(item.get('phone', '')),
                'website': self._clean_url(item.get('website', '')),
                'hours': self._parse_hours(item.get('hours', {}))
            }
            
            # Only add if we have minimum required data
            if cleaned_item['name'] and cleaned_item['name'] != 'Unknown Business':
                cleaned_data.append(cleaned_item)
        
        return cleaned_data
    
    def calculate_market_density(self, businesses: List[Dict], radius: int = 1000) -> Dict[str, Any]:
        """Calculate market density metrics"""
        if not businesses:
            return {
                'density_score': 0,
                'businesses_per_km2': 0,
                'category_distribution': {},
                'saturation_level': 'Low'
            }
        
        # Calculate area in km²
        area_km2 = math.pi * (radius / 1000) ** 2
        businesses_per_km2 = len(businesses) / area_km2
        
        # Calculate category distribution
        categories = [b.get('category', 'Other') for b in businesses]
        category_counts = Counter(categories)
        total_businesses = len(businesses)
        
        category_distribution = {
            cat: {
                'count': count,
                'percentage': round((count / total_businesses) * 100, 1)
            }
            for cat, count in category_counts.items()
        }
        
        # Calculate density score (0-10 scale)
        density_score = min(10, businesses_per_km2 / 10)
        
        # Determine saturation level
        if density_score < 3:
            saturation = 'Low'
        elif density_score < 7:
            saturation = 'Medium'
        else:
            saturation = 'High'
        
        return {
            'density_score': round(density_score, 1),
            'businesses_per_km2': round(businesses_per_km2, 1),
            'category_distribution': category_distribution,
            'saturation_level': saturation,
            'total_businesses': total_businesses
        }
    
    def analyze_competition_strength(self, competitors: List[Dict], target_business_type: str) -> Dict[str, Any]:
        """Analyze the strength and positioning of competitors"""
        if not competitors:
            return {
                'competition_strength': 'Low',
                'average_rating': 0,
                'price_analysis': {},
                'market_leaders': [],
                'weak_competitors': []
            }
        
        # Filter relevant competitors
        relevant_competitors = self._filter_relevant_competitors(competitors, target_business_type)
        
        # Calculate metrics
        ratings = [c.get('rating', 0) for c in relevant_competitors if c.get('rating', 0) > 0]
        avg_rating = statistics.mean(ratings) if ratings else 0
        
        # Analyze price levels
        price_levels = [c.get('price_level', 0) for c in relevant_competitors if c.get('price_level', 0) > 0]
        price_analysis = self._analyze_price_distribution(price_levels)
        
        # Identify market leaders and weak competitors
        market_leaders = self._identify_market_leaders(relevant_competitors)
        weak_competitors = self._identify_weak_competitors(relevant_competitors)
        
        # Determine overall competition strength
        competition_strength = self._calculate_competition_strength(
            len(relevant_competitors), avg_rating, price_analysis
        )
        
        return {
            'competition_strength': competition_strength,
            'average_rating': round(avg_rating, 1),
            'price_analysis': price_analysis,
            'market_leaders': market_leaders,
            'weak_competitors': weak_competitors,
            'competitor_count': len(relevant_competitors)
        }
    
    def process_hours_data(self, businesses: List[Dict]) -> Dict[str, Any]:
        """Process and analyze business hours data"""
        hours_data = []
        
        for business in businesses:
            hours = business.get('hours', {})
            if hours:
                parsed_hours = self._parse_business_hours(hours)
                if parsed_hours:
                    hours_data.append({
                        'name': business.get('name', ''),
                        'category': business.get('category', ''),
                        'hours': parsed_hours
                    })
        
        # Analyze patterns
        patterns = self._analyze_hours_patterns(hours_data)
        peak_times = self._identify_peak_times(hours_data)
        recommendations = self._generate_hours_recommendations(patterns, peak_times)
        
        return {
            'patterns': patterns,
            'peak_times': peak_times,
            'recommendations': recommendations,
            'sample_size': len(hours_data)
        }
    
    def identify_market_gaps(self, businesses: List[Dict], location_data: Dict = None) -> List[Dict]:
        """Identify gaps in the local market"""
        # Analyze current business composition
        categories = [b.get('category', 'Other') for b in businesses]
        category_counts = Counter(categories)
        
        # Define expected business types for a balanced market
        expected_businesses = {
            'Coffee Shop': 3,
            'Restaurant': 8,
            'Convenience Store': 2,
            'Fitness Center': 2,
            'Beauty Salon': 2,
            'Pharmacy': 1,
            'Bank/ATM': 1,
            'Gas Station': 1,
            'Grocery Store': 2,
            'Auto Services': 2
        }
        
        gaps = []
        for business_type, expected_count in expected_businesses.items():
            current_count = sum(count for cat, count in category_counts.items() 
                              if self._category_matches(cat, business_type))
            
            if current_count < expected_count:
                gap_severity = self._calculate_gap_severity(current_count, expected_count)
                gaps.append({
                    'business_type': business_type,
                    'current_count': current_count,
                    'expected_count': expected_count,
                    'gap_size': expected_count - current_count,
                    'severity': gap_severity,
                    'opportunity_score': self._calculate_gap_opportunity_score(
                        current_count, expected_count, len(businesses)
                    )
                })
        
        # Sort by opportunity score
        gaps.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return gaps
    
    def calculate_optimal_location_score(self, businesses: List[Dict], target_coordinates: Tuple[float, float] = None) -> Dict[str, Any]:
        """Calculate location score based on various factors"""
        if not businesses:
            return {'score': 5.0, 'factors': {}}
        
        factors = {}
        
        # Business density factor (optimal is medium density)
        density = len(businesses)
        if density < 20:
            density_score = density / 20 * 7  # Low density gets moderate score
        elif density < 50:
            density_score = 10  # Medium density is optimal
        else:
            density_score = max(3, 10 - (density - 50) / 10)  # High density reduces score
        
        factors['business_density'] = round(density_score, 1)
        
        # Diversity factor (more diverse = better)
        categories = [b.get('category', 'Other') for b in businesses]
        unique_categories = len(set(categories))
        diversity_score = min(10, unique_categories / 3)
        factors['business_diversity'] = round(diversity_score, 1)
        
        # Quality factor (based on average ratings)
        ratings = [b.get('rating', 0) for b in businesses if b.get('rating', 0) > 0]
        avg_rating = statistics.mean(ratings) if ratings else 3.5
        quality_score = (avg_rating / 5) * 10
        factors['area_quality'] = round(quality_score, 1)
        
        # Calculate overall score
        overall_score = (
            factors['business_density'] * 0.4 +
            factors['business_diversity'] * 0.3 +
            factors['area_quality'] * 0.3
        )
        
        return {
            'score': round(overall_score, 1),
            'factors': factors,
            'recommendation': self._get_location_recommendation(overall_score)
        }
    
    def aggregate_market_insights(self, competitors: List[Dict], market_data: Dict, opportunities: List[Dict]) -> Dict[str, Any]:
        """Aggregate all market data into comprehensive insights"""
        insights = {
            'summary': {},
            'key_findings': [],
            'action_items': [],
            'risk_factors': [],
            'success_factors': []
        }
        
        # Generate summary
        total_competitors = len(competitors)
        market_score = market_data.get('density_score', 5.0)
        top_opportunity = opportunities[0] if opportunities else None
        
        insights['summary'] = {
            'total_competitors': total_competitors,
            'market_score': market_score,
            'top_opportunity': top_opportunity.get('business_type') if top_opportunity else 'No clear opportunities',
            'competition_level': self._determine_competition_level(total_competitors, market_score)
        }
        
        # Generate key findings
        insights['key_findings'] = self._generate_key_findings(competitors, market_data, opportunities)
        
        # Generate action items
        insights['action_items'] = self._generate_action_items(market_score, opportunities)
        
        # Identify risk factors
        insights['risk_factors'] = self._identify_risk_factors(competitors, market_data)
        
        # Identify success factors
        insights['success_factors'] = self._identify_success_factors(market_data, opportunities)
        
        return insights
    
    def validate_and_enhance_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Validate input data and enhance with calculated fields"""
        enhanced_data = {}
        
        # Validate location data
        if 'location' in raw_data:
            enhanced_data['location'] = {
                'original': raw_data['location'],
                'cleaned': self._clean_text(raw_data['location']),
                'coordinates': self._extract_coordinates(raw_data.get('coordinates')),
                'address_components': self._parse_address(raw_data['location'])
            }
        
        # Validate business type
        if 'business_type' in raw_data:
            enhanced_data['business_type'] = {
                'original': raw_data['business_type'],
                'standardized': self._standardize_business_type(raw_data['business_type']),
                'category_keywords': self.business_categories.get(raw_data['business_type'], [])
            }
        
        # Validate radius
        if 'radius' in raw_data:
            enhanced_data['radius'] = max(100, min(10000, int(raw_data.get('radius', 1000))))
        
        # Add timestamp
        enhanced_data['processed_at'] = datetime.now().isoformat()
        
        return enhanced_data
    
    def format_response_data(self, analysis_result: Dict, response_type: str = 'json') -> Any:
        """Format analysis results for API responses"""
        if response_type == 'json':
            return self._format_json_response(analysis_result)
        elif response_type == 'summary':
            return self._format_summary_response(analysis_result)
        else:
            return analysis_result
    
    # Private helper methods
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text or not isinstance(text, str):
            return ''
        
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', text.strip())
        cleaned = re.sub(r'[^\w\s\-\.,]', '', cleaned)
        return cleaned
    
    def _clean_address(self, address: str) -> str:
        """Clean and format address data"""
        if not address:
            return ''
        
        # Basic address cleaning
        cleaned = self._clean_text(address)
        
        # Standardize common abbreviations
        replacements = {
            ' st ': ' Street ',
            ' ave ': ' Avenue ',
            ' blvd ': ' Boulevard ',
            ' rd ': ' Road ',
            ' dr ': ' Drive '
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old.lower(), new)
        
        return cleaned.title()
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone numbers"""
        if not phone:
            return ''
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format US phone numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't format
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URLs"""
        if not url:
            return ''
        
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def _standardize_category(self, category: str) -> str:
        """Standardize business category names"""
        if not category:
            return 'Other'
        
        category_lower = category.lower()
        
        # Map common variations to standard categories
        category_mappings = {
            'coffee': 'Coffee Shop',
            'cafe': 'Coffee Shop',
            'restaurant': 'Restaurant',
            'fast food': 'Fast Food',
            'pizza': 'Pizza Restaurant',
            'gym': 'Fitness Center',
            'fitness': 'Fitness Center',
            'salon': 'Beauty Salon',
            'spa': 'Beauty Salon',
            'store': 'Retail Store',
            'shop': 'Retail Store',
            'clinic': 'Healthcare',
            'doctor': 'Healthcare'
        }
        
        for key, standard_name in category_mappings.items():
            if key in category_lower:
                return standard_name
        
        return category.title()
    
    def _validate_distance(self, distance: Any) -> int:
        """Validate and convert distance to meters"""
        try:
            return max(0, int(float(distance)))
        except (ValueError, TypeError):
            return 0
    
    def _validate_rating(self, rating: Any) -> float:
        """Validate and normalize rating values"""
        try:
            rating_float = float(rating)
            return max(0, min(5, rating_float))
        except (ValueError, TypeError):
            return 0
    
    def _validate_coordinate(self, coord: Any) -> float:
        """Validate geographic coordinates"""
        try:
            coord_float = float(coord)
            if -180 <= coord_float <= 180:
                return coord_float
        except (ValueError, TypeError):
            pass
        return 0
    
    def _parse_hours(self, hours_data: Any) -> Dict[str, str]:
        """Parse and standardize business hours"""
        if not hours_data or not isinstance(hours_data, dict):
            return {}
        
        standardized_hours = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            day_hours = hours_data.get(day, hours_data.get(day.capitalize(), ''))
            if day_hours:
                standardized_hours[day.capitalize()] = str(day_hours)
        
        return standardized_hours
    
    def _filter_relevant_competitors(self, competitors: List[Dict], business_type: str) -> List[Dict]:
        """Filter competitors relevant to the target business type"""
        if business_type not in self.business_categories:
            return competitors
        
        keywords = self.business_categories[business_type]
        relevant_competitors = []
        
        for competitor in competitors:
            category = competitor.get('category', '').lower()
            name = competitor.get('name', '').lower()
            
            if any(keyword in category or keyword in name for keyword in keywords):
                relevant_competitors.append(competitor)
        
        return relevant_competitors
    
    def _analyze_price_distribution(self, price_levels: List[int]) -> Dict[str, Any]:
        """Analyze price level distribution"""
        if not price_levels:
            return {'average': 0, 'distribution': {}, 'recommendation': 'Medium pricing'}
        
        price_counter = Counter(price_levels)
        total = len(price_levels)
        
        distribution = {
            'budget': price_counter.get(1, 0) / total * 100,
            'moderate': price_counter.get(2, 0) / total * 100,
            'expensive': price_counter.get(3, 0) / total * 100,
            'very_expensive': price_counter.get(4, 0) / total * 100
        }
        
        avg_price = statistics.mean(price_levels)
        
        # Generate pricing recommendation
        if avg_price < 2:
            recommendation = 'Consider moderate pricing for differentiation'
        elif avg_price > 3:
            recommendation = 'Budget-friendly pricing could capture underserved market'
        else:
            recommendation = 'Competitive pricing environment - focus on value'
        
        return {
            'average': round(avg_price, 1),
            'distribution': {k: round(v, 1) for k, v in distribution.items()},
            'recommendation': recommendation
        }
    
    def _identify_market_leaders(self, competitors: List[Dict]) -> List[Dict]:
        """Identify top-performing competitors"""
        if not competitors:
            return []
        
        # Score competitors based on rating and other factors
        scored_competitors = []
        for comp in competitors:
            score = (
                comp.get('rating', 0) * 0.6 +
                (1 / max(1, comp.get('distance', 1000) / 100)) * 0.4
            )
            scored_competitors.append({
                'name': comp.get('name', ''),
                'rating': comp.get('rating', 0),
                'distance': comp.get('distance', 0),
                'score': round(score, 2)
            })
        
        # Return top 3 market leaders
        scored_competitors.sort(key=lambda x: x['score'], reverse=True)
        return scored_competitors[:3]
    
    def _identify_weak_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """Identify underperforming competitors"""
        if not competitors:
            return []
        
        weak_competitors = [
            comp for comp in competitors 
            if comp.get('rating', 5) < 3.5
        ]
        
        return weak_competitors[:3]  # Return up to 3 weak competitors
    
    def _calculate_competition_strength(self, competitor_count: int, avg_rating: float, price_analysis: Dict) -> str:
        """Calculate overall competition strength"""
        # Normalize factors
        count_factor = min(1, competitor_count / 10)
        rating_factor = avg_rating / 5
        
        combined_score = (count_factor * 0.6) + (rating_factor * 0.4)
        
        if combined_score < 0.3:
            return 'Low'
        elif combined_score < 0.7:
            return 'Medium'
        else:
            return 'High'
    
    def _analyze_hours_patterns(self, hours_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in business hours"""
        if not hours_data:
            return {}
        
        # Extract opening and closing times
        opening_times = defaultdict(list)
        closing_times = defaultdict(list)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for business in hours_data:
            for day in days:
                if day in business.get('hours', {}):
                    hours = business['hours'][day]
                    open_time, close_time = self._extract_open_close_times(hours)
                    if open_time and close_time:
                        opening_times[day].append(open_time)
                        closing_times[day].append(close_time)
        
        # Calculate averages
        patterns = {}
        for day in days:
            if opening_times[day] and closing_times[day]:
                patterns[day] = {
                    'avg_open': self._time_to_string(statistics.mean(opening_times[day])),
                    'avg_close': self._time_to_string(statistics.mean(closing_times[day])),
                    'earliest_open': self._time_to_string(min(opening_times[day])),
                    'latest_close': self._time_to_string(max(closing_times[day]))
                }
        
        return patterns
    
    def _extract_open_close_times(self, hours_string: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract opening and closing times from hours string"""
        if not hours_string or 'closed' in hours_string.lower():
            return None, None
        
        # Simple regex pattern for times like "9:00 AM - 5:00 PM"
        time_pattern = r'(\d{1,2}):?(\d{0,2})\s*(AM|PM)?'
        matches = re.findall(time_pattern, hours_string.upper())
        
        if len(matches) >= 2:
            # Parse opening time
            open_hour = int(matches[0][0])
            open_min = int(matches[0][1]) if matches[0][1] else 0
            open_period = matches[0][2] if matches[0][2] else ('AM' if open_hour < 12 else 'PM')
            
            # Parse closing time
            close_hour = int(matches[1][0])
            close_min = int(matches[1][1]) if matches[1][1] else 0
            close_period = matches[1][2] if matches[1][2] else 'PM'
            
            # Convert to 24-hour format
            open_24 = self._to_24_hour(open_hour, open_min, open_period)
            close_24 = self._to_24_hour(close_hour, close_min, close_period)
            
            return open_24, close_24
        
        return None, None
    
    def _to_24_hour(self, hour: int, minute: int, period: str) -> float:
        """Convert 12-hour time to 24-hour decimal format"""
        if period == 'PM' and hour != 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0
        
        return hour + (minute / 60)
    
    def _time_to_string(self, decimal_time: float) -> str:
        """Convert decimal time back to readable format"""
        hour = int(decimal_time)
        minute = int((decimal_time - hour) * 60)
        
        if hour == 0:
            return f"12:{minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{minute:02d} AM"
        elif hour == 12:
            return f"12:{minute:02d} PM"
        else:
            return f"{hour - 12}:{minute:02d} PM"
    
    def _identify_peak_times(self, hours_data: List[Dict]) -> Dict[str, List[str]]:
        """Identify peak business hours"""
        # Mock implementation - would analyze actual traffic data
        return {
            'weekday_peaks': ['8:00-10:00 AM', '12:00-2:00 PM', '5:00-7:00 PM'],
            'weekend_peaks': ['10:00 AM-12:00 PM', '2:00-5:00 PM', '7:00-9:00 PM'],
            'seasonal_patterns': ['Higher activity in Q4', 'Summer outdoor business boost']
        }
    
    def _generate_hours_recommendations(self, patterns: Dict, peak_times: Dict) -> List[str]:
        """Generate hours optimization recommendations"""
        recommendations = [
            "Align opening hours with local business patterns",
            "Extend hours during identified peak periods",
            "Consider early morning hours for professional service areas",
            "Weekend hours should reflect leisure activity patterns"
        ]
        
        return recommendations
    
    def _category_matches(self, actual_category: str, expected_business: str) -> bool:
        """Check if actual category matches expected business type"""
        actual_lower = actual_category.lower()
        expected_lower = expected_business.lower()
        
        # Define matching patterns
        matches = {
            'coffee shop': ['coffee', 'cafe'],
            'restaurant': ['restaurant', 'dining', 'food'],
            'convenience store': ['convenience', 'market', 'corner'],
            'fitness center': ['fitness', 'gym', 'health'],
            'beauty salon': ['salon', 'beauty', 'spa'],
            'pharmacy': ['pharmacy', 'drug', 'cvs', 'walgreens'],
            'grocery store': ['grocery', 'supermarket', 'food store']
        }
        
        keywords = matches.get(expected_lower, [expected_lower.split()[0]])
        return any(keyword in actual_lower for keyword in keywords)
    
    def _calculate_gap_severity(self, current: int, expected: int) -> str:
        """Calculate severity of market gap"""
        gap_ratio = (expected - current) / expected
        
        if gap_ratio >= 0.8:
            return 'Critical'
        elif gap_ratio >= 0.5:
            return 'High'
        elif gap_ratio >= 0.3:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_gap_opportunity_score(self, current: int, expected: int, total_businesses: int) -> float:
        """Calculate opportunity score for market gaps"""
        gap_size = expected - current
        market_size_factor = min(2, total_businesses / 50)
        
        base_score = gap_size * 2
        adjusted_score = base_score * market_size_factor
        
        return round(min(10, adjusted_score), 1)
    
    def _get_location_recommendation(self, score: float) -> str:
        """Get location recommendation based on score"""
        if score >= 8:
            return "Excellent location with strong market potential"
        elif score >= 6:
            return "Good location with moderate opportunities"
        elif score >= 4:
            return "Average location - consider market positioning carefully"
        else:
            return "Challenging location - strong differentiation required"
    
    def _determine_competition_level(self, competitor_count: int, market_score: float) -> str:
        """Determine overall competition level"""
        if competitor_count < 5 and market_score < 5:
            return 'Low'
        elif competitor_count < 15 and market_score < 7:
            return 'Medium'
        else:
            return 'High'
    
    def _generate_key_findings(self, competitors: List[Dict], market_data: Dict, opportunities: List[Dict]) -> List[str]:
        """Generate key market findings"""
        findings = []
        
        competitor_count = len(competitors)
        market_score = market_data.get('density_score', 5.0)
        
        if competitor_count < 5:
            findings.append("Low competition environment presents first-mover advantages")
        elif competitor_count > 15:
            findings.append("Highly competitive market requires strong differentiation strategy")
        
        if market_score > 7:
            findings.append("High market activity indicates strong consumer demand")
        elif market_score < 3:
            findings.append("Emerging market with potential for growth")
        
        if opportunities:
            top_opp = opportunities[0]
            findings.append(f"Top opportunity identified: {top_opp.get('business_type', 'Unknown')} with {top_opp.get('opportunity_score', 0)} score")
        
        return findings
    
    def _generate_action_items(self, market_score: float, opportunities: List[Dict]) -> List[str]:
        """Generate actionable items based on analysis"""
        actions = []
        
        if market_score < 4:
            actions.append("Conduct additional market validation through local surveys")
            actions.append("Consider phased market entry approach")
        elif market_score > 7:
            actions.append("Move quickly to establish market presence")
            actions.append("Prepare for competitive response strategies")
        
        if opportunities:
            top_opportunity = opportunities[0]
            actions.append(f"Research {top_opportunity.get('business_type', 'top opportunity')} market requirements")
            actions.append("Validate opportunity through local community engagement")
        
        actions.append("Monitor competitor activities and market changes")
        actions.append("Develop unique value proposition for market differentiation")
        
        return actions
    
    def _identify_risk_factors(self, competitors: List[Dict], market_data: Dict) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        competitor_count = len(competitors)
        market_score = market_data.get('density_score', 5.0)
        
        if competitor_count > 10:
            risks.append("High competition may impact market share and pricing power")
        
        if market_score > 8:
            risks.append("Market saturation risk - new entrants may struggle")
        
        # Check for dominant competitors
        strong_competitors = [c for c in competitors if c.get('rating', 0) > 4.3]
        if len(strong_competitors) > 3:
            risks.append("Multiple strong competitors present - differentiation critical")
        
        if market_score < 3:
            risks.append("Low market activity may indicate limited consumer demand")
        
        return risks
    
    def _identify_success_factors(self, market_data: Dict, opportunities: List[Dict]) -> List[str]:
        """Identify factors that contribute to success"""
        success_factors = []
        
        market_score = market_data.get('density_score', 5.0)
        
        if 4 <= market_score <= 7:
            success_factors.append("Balanced market conditions favor new entrants")
        
        if opportunities:
            high_score_opps = [o for o in opportunities if o.get('opportunity_score', 0) > 7]
            if high_score_opps:
                success_factors.append("High-scoring opportunities identified in market gaps")
        
        diversity_score = len(market_data.get('category_distribution', {}))
        if diversity_score > 8:
            success_factors.append("Diverse business ecosystem supports cross-customer traffic")
        
        success_factors.extend([
            "Local market shows consistent business activity",
            "Multiple entry strategies available based on opportunity analysis",
            "Market intelligence provides competitive advantage over uninformed competitors"
        ])
        
        return success_factors
    
    def _format_json_response(self, analysis_result: Dict) -> Dict[str, Any]:
        """Format analysis results for JSON API response"""
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': analysis_result,
            'metadata': {
                'processing_time': 'real-time',
                'data_sources': ['foursquare_api', 'business_intelligence'],
                'version': '1.0'
            }
        }
    
    def _format_summary_response(self, analysis_result: Dict) -> str:
        """Format analysis results as text summary"""
        summary_parts = []
        
        if 'summary' in analysis_result:
            summary = analysis_result['summary']
            summary_parts.append(f"Market Analysis Summary:")
            summary_parts.append(f"- Total Competitors: {summary.get('total_competitors', 0)}")
            summary_parts.append(f"- Market Score: {summary.get('market_score', 0)}/10")
            summary_parts.append(f"- Competition Level: {summary.get('competition_level', 'Unknown')}")
        
        if 'key_findings' in analysis_result:
            summary_parts.append("\nKey Findings:")
            for finding in analysis_result['key_findings'][:3]:  # Top 3 findings
                summary_parts.append(f"- {finding}")
        
        return "\n".join(summary_parts)
    
    def _extract_coordinates(self, coordinates: Any) -> Optional[Tuple[float, float]]:
        """Extract and validate coordinates"""
        if not coordinates:
            return None
        
        try:
            if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
                lat, lng = float(coordinates[0]), float(coordinates[1])
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return (lat, lng)
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_address(self, address: str) -> Dict[str, str]:
        """Parse address into components"""
        if not address:
            return {}
        
        # Simple address parsing - in production, use proper geocoding service
        components = {}
        address_parts = address.split(',')
        
        if len(address_parts) >= 1:
            components['street'] = address_parts[0].strip()
        if len(address_parts) >= 2:
            components['city'] = address_parts[-2].strip()
        if len(address_parts) >= 3:
            components['state'] = address_parts[-1].strip()
        
        return components
    
    def _standardize_business_type(self, business_type: str) -> str:
        """Standardize business type input"""
        if not business_type:
            return 'general'
        
        business_type_lower = business_type.lower().strip()
        
        # Map variations to standard types
        type_mappings = {
            'food': 'restaurant',
            'dining': 'restaurant',
            'cafe': 'restaurant',
            'coffee': 'restaurant',
            'shop': 'retail',
            'store': 'retail',
            'boutique': 'retail',
            'gym': 'fitness',
            'health': 'fitness',
            'wellness': 'fitness',
            'salon': 'beauty',
            'spa': 'beauty',
            'barber': 'beauty',
            'office': 'professional',
            'service': 'professional',
            'clinic': 'healthcare',
            'medical': 'healthcare',
            'school': 'education',
            'training': 'education'
        }
        
        for keyword, standard_type in type_mappings.items():
            if keyword in business_type_lower:
                return standard_type
        
        return business_type_lower
    
    def _parse_business_hours(self, hours_data: Any) -> Optional[Dict[str, str]]:
        """Parse various formats of business hours data"""
        if not hours_data:
            return None
        
        parsed_hours = {}
        
        if isinstance(hours_data, dict):
            # Handle dict format
            for day, hours in hours_data.items():
                if isinstance(hours, str) and hours.strip():
                    parsed_hours[day.capitalize()] = hours.strip()
        elif isinstance(hours_data, str):
            # Handle string format like "Mon-Fri: 9AM-5PM"
            parsed_hours = self._parse_hours_string(hours_data)
        
        return parsed_hours if parsed_hours else None
    
    def _parse_hours_string(self, hours_string: str) -> Dict[str, str]:
        """Parse hours from string format"""
        parsed = {}
        
        # Simple parsing for common formats
        if 'mon-fri' in hours_string.lower():
            # Extract weekday hours
            weekday_pattern = r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM)?)'
            match = re.search(weekday_pattern, hours_string, re.IGNORECASE)
            if match:
                hours = f"{match.group(1)} - {match.group(2)}"
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    parsed[day] = hours
        
        return parsed
    
    def export_analysis_data(self, analysis_results: Dict, export_format: str = 'json') -> str:
        """Export analysis results in specified format"""
        if export_format == 'json':
            return json.dumps(analysis_results, indent=2, default=str)
        elif export_format == 'csv':
            return self._convert_to_csv(analysis_results)
        else:
            return str(analysis_results)
    
    def _convert_to_csv(self, data: Dict) -> str:
        """Convert analysis data to CSV format"""
        # Simple CSV conversion for competitor data
        if 'competitors' in data:
            csv_lines = ['Name,Category,Address,Distance,Rating']
            for comp in data['competitors']:
                line = f"{comp.get('name', '')},{comp.get('category', '')},{comp.get('address', '')},{comp.get('distance', 0)},{comp.get('rating', 0)}"
                csv_lines.append(line)
            return '\n'.join(csv_lines)
        
        return "No convertible data found"
    
    def calculate_market_health_score(self, businesses: List[Dict]) -> Dict[str, Any]:
        """Calculate overall market health score"""
        if not businesses:
            return {'health_score': 0, 'indicators': {}}
        
        indicators = {}
        
        # Business diversity indicator
        categories = [b.get('category', 'Other') for b in businesses]
        unique_categories = len(set(categories))
        diversity_score = min(10, unique_categories / 2)
        indicators['business_diversity'] = round(diversity_score, 1)
        
        # Quality indicator (average ratings)
        ratings = [b.get('rating', 0) for b in businesses if b.get('rating', 0) > 0]
        avg_rating = statistics.mean(ratings) if ratings else 3.5
        quality_score = (avg_rating / 5) * 10
        indicators['service_quality'] = round(quality_score, 1)
        
        # Activity indicator (business density)
        activity_score = min(10, len(businesses) / 5)
        indicators['market_activity'] = round(activity_score, 1)
        
        # Calculate overall health score
        health_score = (
            indicators['business_diversity'] * 0.3 +
            indicators['service_quality'] * 0.4 +
            indicators['market_activity'] * 0.3
        )
        
        return {
            'health_score': round(health_score, 1),
            'indicators': indicators,
            'assessment': self._get_health_assessment(health_score)
        }
    
    def _get_health_assessment(self, score: float) -> str:
        """Get market health assessment based on score"""
        if score >= 8:
            return "Thriving market with strong fundamentals"
        elif score >= 6:
            return "Healthy market with good potential"
        elif score >= 4:
            return "Developing market with mixed indicators"
        else:
            return "Challenging market conditions - careful analysis required"
    
    def generate_comprehensive_report(self, all_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        report = {
            'executive_summary': {},
            'market_analysis': {},
            'competitive_landscape': {},
            'opportunities': {},
            'recommendations': {},
            'risk_assessment': {}
        }
        
        # Executive Summary
        competitor_count = len(all_data.get('competitors', []))
        market_score = all_data.get('market_data', {}).get('density_score', 5.0)
        top_opportunity = all_data.get('opportunities', [{}])[0] if all_data.get('opportunities') else {}
        
        report['executive_summary'] = {
            'market_attractiveness': self._score_to_rating(market_score),
            'competition_intensity': self._competitor_count_to_intensity(competitor_count),
            'primary_opportunity': top_opportunity.get('business_type', 'None identified'),
            'overall_recommendation': self._generate_overall_recommendation(market_score, competitor_count)
        }
        
        # Market Analysis
        report['market_analysis'] = {
            'total_businesses': len(all_data.get('all_businesses', [])),
            'market_health': all_data.get('market_health', {}),
            'growth_indicators': self._analyze_growth_indicators(all_data),
            'market_gaps': all_data.get('market_gaps', [])
        }
        
        # Competitive Landscape
        report['competitive_landscape'] = {
            'direct_competitors': competitor_count,
            'market_leaders': all_data.get('market_leaders', []),
            'competitive_advantages': self._identify_competitive_advantages(all_data),
            'barriers_to_entry': self._assess_barriers_to_entry(all_data)
        }
        
        return report
    
    def _score_to_rating(self, score: float) -> str:
        """Convert numeric score to descriptive rating"""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Fair"
        else:
            return "Poor"
    
    def _competitor_count_to_intensity(self, count: int) -> str:
        """Convert competitor count to intensity level"""
        if count <= 3:
            return "Low"
        elif count <= 8:
            return "Moderate"
        elif count <= 15:
            return "High"
        else:
            return "Very High"
    
    def _generate_overall_recommendation(self, market_score: float, competitor_count: int) -> str:
        """Generate overall business recommendation"""
        if market_score >= 6 and competitor_count <= 8:
            return "Recommended - Favorable market conditions"
        elif market_score >= 4 and competitor_count <= 12:
            return "Proceed with caution - Moderate market conditions"
        else:
            return "Not recommended - Challenging market conditions"
    
    def _analyze_growth_indicators(self, data: Dict) -> List[str]:
        """Analyze indicators of market growth"""
        indicators = []
        
        market_score = data.get('market_data', {}).get('density_score', 5.0)
        businesses = data.get('all_businesses', [])
        
        if market_score > 6:
            indicators.append("High business activity indicates growing market")
        
        # Analyze business types for growth signs
        categories = [b.get('category', '') for b in businesses]
        modern_businesses = sum(1 for cat in categories if any(keyword in cat.lower() 
                                                             for keyword in ['tech', 'fitness', 'organic', 'specialty']))
        
        if modern_businesses > len(businesses) * 0.2:
            indicators.append("Presence of modern business types suggests market evolution")
        
        return indicators
    
    def _identify_competitive_advantages(self, data: Dict) -> List[str]:
        """Identify potential competitive advantages"""
        advantages = []
        
        competitors = data.get('competitors', [])
        weak_competitors = [c for c in competitors if c.get('rating', 5) < 3.5]
        
        if weak_competitors:
            advantages.append("Opportunity to outperform underperforming competitors")
        
        market_gaps = data.get('market_gaps', [])
        high_opportunity_gaps = [g for g in market_gaps if g.get('opportunity_score', 0) > 7]
        
        if high_opportunity_gaps:
            advantages.append("Clear market gaps present first-mover opportunities")
        
        return advantages
    
    def _assess_barriers_to_entry(self, data: Dict) -> List[str]:
        """Assess barriers to market entry"""
        barriers = []
        
        competitors = data.get('competitors', [])
        strong_competitors = [c for c in competitors if c.get('rating', 0) > 4.2]
        
        if len(strong_competitors) > 5:
            barriers.append("Multiple established high-quality competitors")
        
        market_score = data.get('market_data', {}).get('density_score', 5.0)
        if market_score > 8:
            barriers.append("High market saturation may limit customer acquisition")
        
        return barriers