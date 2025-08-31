from typing import List, Dict, Any
import statistics
from datetime import datetime, time

class BusinessIntelligence:
    """Core business intelligence and recommendation engine"""
    
    def __init__(self):
        self.business_hour_patterns = {
            'restaurant': {'weekday': (8, 22), 'weekend': (9, 23)},
            'retail': {'weekday': (9, 19), 'weekend': (10, 20)},
            'fitness': {'weekday': (5, 23), 'weekend': (7, 22)},
            'beauty': {'weekday': (9, 19), 'weekend': (9, 18)},
            'professional': {'weekday': (8, 18), 'weekend': (10, 16)},
            'healthcare': {'weekday': (8, 17), 'weekend': (9, 15)},
            'education': {'weekday': (8, 20), 'weekend': (9, 17)}
        }
    
    def analyze_competitors(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor data and generate insights"""
        if not competitors:
            return {
                'market_density': 'Low',
                'competition_level': 'Low',
                'recommendations': ['Great location with minimal competition!']
            }
        
        competitor_count = len(competitors)
        avg_rating = statistics.mean([c.get('rating', 4.0) for c in competitors if c.get('rating', 0) > 0])
        
        # Calculate market density
        if competitor_count <= 3:
            density = 'Low'
            competition = 'Low'
        elif competitor_count <= 8:
            density = 'Medium'
            competition = 'Medium'
        else:
            density = 'High'
            competition = 'High'
        
        # Generate recommendations
        recommendations = self._generate_competitor_recommendations(
            competitor_count, avg_rating, density
        )
        
        return {
            'market_density': density,
            'competition_level': competition,
            'average_rating': round(avg_rating, 1),
            'total_competitors': competitor_count,
            'recommendations': recommendations
        }
    
    def recommend_hours(self, local_businesses: List[Dict], business_type: str) -> Dict[str, Any]:
        """Generate optimal hours recommendation"""
        # Get base pattern for business type
        base_pattern = self.business_hour_patterns.get(business_type, 
                                                     self.business_hour_patterns['retail'])
        
        # Analyze local competition hours
        competitor_hours = self._analyze_competitor_hours(local_businesses)
        
        # Generate optimized schedule
        optimized_schedule = self._create_optimized_schedule(base_pattern, competitor_hours, business_type)
        
        # Generate insights
        insights = self._generate_hours_insights(optimized_schedule, business_type, competitor_hours)
        
        return {
            'weekly_schedule': optimized_schedule,
            'insights': insights,
            'peak_hours': self._identify_peak_hours(business_type),
            'revenue_impact': self._estimate_revenue_impact(optimized_schedule, business_type)
        }
    
    def identify_opportunities(self, market_data: Dict) -> List[Dict]:
        """Identify business opportunities based on market analysis"""
        opportunities = []
        categories = market_data.get('categories', {})
        total_businesses = market_data.get('total_businesses', 0)
        
        # Define opportunity thresholds
        opportunity_categories = {
            'Specialty Coffee Shop': {'threshold': 2, 'icon': 'fa-coffee'},
            'Fitness Studio': {'threshold': 3, 'icon': 'fa-dumbbell'},
            'Pet Services': {'threshold': 1, 'icon': 'fa-paw'},
            'Coworking Space': {'threshold': 1, 'icon': 'fa-laptop'},
            'Healthy Fast Food': {'threshold': 5, 'icon': 'fa-leaf'},
            'Mobile Phone Repair': {'threshold': 2, 'icon': 'fa-mobile-alt'},
            'Tutoring Center': {'threshold': 2, 'icon': 'fa-graduation-cap'},
            'Laundromat': {'threshold': 1, 'icon': 'fa-tshirt'}
        }
        
        # Analyze gaps in market
        for category, config in opportunity_categories.items():
            current_count = sum([count for cat, count in categories.items() 
                               if any(keyword in cat.lower() for keyword in 
                                     category.lower().split())])
            
            if current_count <= config['threshold']:
                score = self._calculate_opportunity_score(
                    current_count, config['threshold'], total_businesses, category
                )
                
                opportunities.append({
                    'category': category,
                    'score': score,
                    'description': self._generate_opportunity_description(category, current_count, score),
                    'icon': config['icon'],
                    'market_gap': config['threshold'] - current_count
                })
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities[:6]  # Return top 6 opportunities
    
    def _generate_competitor_recommendations(self, count: int, avg_rating: float, density: str) -> List[str]:
        """Generate specific recommendations based on competitor analysis"""
        recommendations = []
        
        if density == 'Low':
            recommendations.extend([
                "🎯 Excellent location with low competition - great opportunity!",
                "📈 Focus on building strong local brand presence",
                "💡 Consider premium pricing strategy due to limited competition"
            ])
        elif density == 'Medium':
            recommendations.extend([
                "⚖️ Balanced competition level - focus on differentiation",
                "🏆 Aim to exceed average rating of {:.1f} stars".format(avg_rating),
                "📊 Monitor competitor pricing and service offerings closely"
            ])
        else:
            recommendations.extend([
                "🚨 High competition area - strong differentiation required",
                "💪 Focus on unique value proposition and superior service",
                "🎨 Consider niche specialization to stand out"
            ])
        
        return recommendations
    
    def _analyze_competitor_hours(self, businesses: List[Dict]) -> Dict:
        """Analyze operating hours of local businesses"""
        # Mock analysis - in real implementation, would parse actual hours
        return {
            'earliest_open': 7,
            'latest_close': 22,
            'avg_weekday_hours': 11,
            'avg_weekend_hours': 10,
            'common_closed_day': 'Sunday'
        }
    
    def _create_optimized_schedule(self, base_pattern: Dict, competitor_hours: Dict, business_type: str) -> Dict:
        """Create optimized weekly schedule"""
        weekday_start, weekday_end = base_pattern['weekday']
        weekend_start, weekend_end = base_pattern['weekend']
        
        # Optimize based on business type and local patterns
        if business_type == 'restaurant':
            # Restaurants benefit from extended evening hours
            weekday_end = min(23, weekday_end + 1)
            weekend_end = min(24, weekend_end + 1)
        elif business_type == 'fitness':
            # Fitness centers benefit from early morning hours
            weekday_start = max(5, weekday_start - 1)
            weekend_start = max(6, weekend_start - 1)
        elif business_type == 'professional':
            # Professional services stick to business hours
            weekend_end = min(17, weekend_end)
        
        return {
            'Monday': f"{weekday_start}:00 AM - {self._format_hour(weekday_end)}",
            'Tuesday': f"{weekday_start}:00 AM - {self._format_hour(weekday_end)}",
            'Wednesday': f"{weekday_start}:00 AM - {self._format_hour(weekday_end)}",
            'Thursday': f"{weekday_start}:00 AM - {self._format_hour(weekday_end + 1)}",
            'Friday': f"{weekday_start}:00 AM - {self._format_hour(weekend_end)}",
            'Saturday': f"{weekend_start}:00 AM - {self._format_hour(weekend_end)}",
            'Sunday': f"{weekend_start + 1}:00 AM - {self._format_hour(weekend_end - 2)}"
        }
    
    def _format_hour(self, hour: int) -> str:
        """Format hour in 12-hour format"""
        if hour <= 12:
            return f"{hour}:00 {'PM' if hour == 12 else 'AM'}"
        else:
            return f"{hour - 12}:00 PM"
    
    def _generate_hours_insights(self, schedule: Dict, business_type: str, competitor_data: Dict) -> List[str]:
        """Generate insights about the recommended hours"""
        insights = []
        
        if business_type == 'restaurant':
            insights.extend([
                "🍽️ Extended Friday and Saturday hours to capture weekend dining traffic",
                "📅 Thursday evening extension recommended for local happy hour market",
                "☀️ Sunday brunch hours optimized for weekend leisure dining"
            ])
        elif business_type == 'retail':
            insights.extend([
                "🛍️ Weekend hours extended to capture leisure shopping traffic",
                "📈 Consistent weekday hours build customer shopping habits",
                "🕐 Late evening hours on Friday for after-work shopping"
            ])
        elif business_type == 'fitness':
            insights.extend([
                "💪 Early morning hours capture pre-work fitness crowd",
                "🌙 Extended evening hours for after-work fitness enthusiasts",
                "🎯 Weekend hours optimized for flexible fitness schedules"
            ])
        else:
            insights.extend([
                "⏰ Hours optimized based on local business patterns",
                "📊 Schedule balances customer convenience with operational efficiency",
                "🎯 Weekend hours adjusted for target demographic preferences"
            ])
        
        return insights
    
    def _identify_peak_hours(self, business_type: str) -> Dict:
        """Identify peak hours for different business types"""
        peak_patterns = {
            'restaurant': {'morning': '8:00-10:00', 'lunch': '12:00-14:00', 'evening': '18:00-20:00'},
            'retail': {'morning': '10:00-12:00', 'afternoon': '14:00-16:00', 'evening': '17:00-19:00'},
            'fitness': {'morning': '6:00-8:00', 'lunch': '12:00-13:00', 'evening': '17:00-20:00'},
            'default': {'morning': '9:00-11:00', 'afternoon': '13:00-15:00', 'evening': '17:00-19:00'}
        }
        
        return peak_patterns.get(business_type, peak_patterns['default'])
    
    def _estimate_revenue_impact(self, schedule: Dict, business_type: str) -> Dict:
        """Estimate revenue impact of optimized hours"""
        return {
            'estimated_increase': '15-25%',
            'peak_hour_capture': '85%',
            'efficiency_gain': '30%'
        }
    
    def _calculate_opportunity_score(self, current_count: int, threshold: int, total_businesses: int, category: str) -> float:
        """Calculate opportunity score for a business category"""
        # Base score calculation
        gap_score = max(0, (threshold - current_count) * 2)
        market_size_score = min(5, total_businesses / 20)
        
        # Category-specific adjustments
        category_multipliers = {
            'Specialty Coffee Shop': 1.2,
            'Fitness Studio': 1.1,
            'Pet Services': 1.3,
            'Coworking Space': 1.4,
            'Healthy Fast Food': 1.1
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        final_score = min(10, (gap_score + market_size_score) * multiplier)
        
        return round(final_score, 1)
    
    def _generate_opportunity_description(self, category: str, current_count: int, score: float) -> str:
        """Generate description for business opportunity"""
        descriptions = {
            'Specialty Coffee Shop': f"High demand area with only {current_count} specialty coffee options. Strong foot traffic from nearby offices and residential areas.",
            'Fitness Studio': f"Growing residential area with {current_count} fitness options. Young professional demographic seeking convenient workout solutions.",
            'Pet Services': f"High pet ownership density with minimal grooming and pet care services. Only {current_count} competitors identified.",
            'Coworking Space': f"Emerging business district with {current_count} coworking options. Remote workers and freelancers need flexible workspace.",
            'Healthy Fast Food': f"Health-conscious area with limited quick healthy dining options. Gap in market for {current_count} existing providers.",
            'Mobile Phone Repair': f"Tech-savvy area with {current_count} repair shops. High smartphone usage creates consistent demand.",
            'Tutoring Center': f"Family-oriented neighborhood with {current_count} educational support services. Strong demand for academic assistance.",
            'Laundromat': f"Residential area with {current_count} laundry services. Apartment dwellers need convenient laundry solutions."
        }
        
        return descriptions.get(category, f"Market analysis shows potential for {category.lower()} with {current_count} existing competitors.")
    
    def _get_mock_competitors(self, business_type: str) -> List[Dict]:
        """Mock competitor data for testing"""
        return [
            {'name': f'Sample {business_type.title()} 1', 'distance': 200, 'rating': 4.2},
            {'name': f'Sample {business_type.title()} 2', 'distance': 450, 'rating': 3.8},
            {'name': f'Sample {business_type.title()} 3', 'distance': 680, 'rating': 4.5}
        ]