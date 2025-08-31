from flask import Flask, render_template, request, jsonify
import os
import config
from utils.foursquare_api import FoursquareAPI
from utils.business_logic import BusinessIntelligence
from utils.data_processor import DataProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Initialize components
foursquare_api = FoursquareAPI(config.FOURSQUARE_API_KEY)
business_intelligence = BusinessIntelligence()
data_processor = DataProcessor()

@app.route('/')
def index():
    """Homepage/Dashboard"""
    return render_template('index.html')

@app.route('/competitor-analysis')
def competitor_analysis():
    """Competitor analysis page"""
    return render_template('competitor_analysis.html')

@app.route('/hours-optimizer')
def hours_optimizer():
    """Hours optimization page"""
    return render_template('hours_optimizer.html')

@app.route('/market-scanner')
def market_scanner():
    """Market scanner page"""
    return render_template('market_scanner.html')

@app.route('/api/analyze-competitors', methods=['POST'])
def api_analyze_competitors():
    """API endpoint for competitor analysis"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate and enhance input data
        enhanced_data = data_processor.validate_and_enhance_data(data)
        
        location = enhanced_data.get('location', {}).get('cleaned', '')
        business_type = enhanced_data.get('business_type', {}).get('standardized', '')
        radius = enhanced_data.get('radius', 1000)
        
        if not location or not business_type:
            return jsonify({'success': False, 'error': 'Location and business type are required'}), 400
        
        # Search for competitors using Foursquare API
        raw_competitors = foursquare_api.search_competitors(location, business_type, radius)
        
        # Clean and process competitor data
        cleaned_competitors = data_processor.clean_location_data(raw_competitors)
        
        # Analyze competitors using business intelligence
        analysis = business_intelligence.analyze_competitors(cleaned_competitors)
        
        # Calculate market density
        market_density = data_processor.calculate_market_density(cleaned_competitors, radius)
        
        # Analyze competition strength
        competition_analysis = data_processor.analyze_competition_strength(cleaned_competitors, business_type)
        
        # Format response
        response_data = {
            'competitors': cleaned_competitors,
            'analysis': {
                **analysis,
                **market_density,
                **competition_analysis
            },
            'location_info': enhanced_data['location'],
            'processed_at': enhanced_data['processed_at']
        }
        
        return jsonify(data_processor.format_response_data(response_data))
        
    except Exception as e:
        app.logger.error(f"Error in competitor analysis: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Analysis failed. Please try again or contact support.'
        }), 500

@app.route('/api/optimize-hours', methods=['POST'])
def api_optimize_hours():
    """API endpoint for hours optimization"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate and enhance input data
        enhanced_data = data_processor.validate_and_enhance_data(data)
        
        location = enhanced_data.get('location', {}).get('cleaned', '')
        business_type = enhanced_data.get('business_type', {}).get('standardized', '')
        radius = enhanced_data.get('radius', 1000)
        current_hours = data.get('current_hours', '')
        
        if not location or not business_type:
            return jsonify({'success': False, 'error': 'Location and business type are required'}), 400
        
        # Get local businesses for hours analysis
        local_businesses = foursquare_api.get_local_businesses(location, radius)
        
        # Clean the data
        cleaned_businesses = data_processor.clean_location_data(local_businesses)
        
        # Process hours data
        hours_analysis = data_processor.process_hours_data(cleaned_businesses)
        
        # Generate hours recommendation
        recommendation = business_intelligence.recommend_hours(cleaned_businesses, business_type)
        
        # Combine all data
        response_data = {
            'recommendation': recommendation,
            'hours_analysis': hours_analysis,
            'current_hours': current_hours,
            'location_info': enhanced_data['location'],
            'business_count': len(cleaned_businesses)
        }
        
        return jsonify(data_processor.format_response_data(response_data))
        
    except Exception as e:
        app.logger.error(f"Error in hours optimization: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Hours optimization failed. Please try again.'
        }), 500

@app.route('/api/scan-market', methods=['POST'])
def api_scan_market():
    """API endpoint for market opportunity scanning"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate and enhance input data
        enhanced_data = data_processor.validate_and_enhance_data(data)
        
        location = enhanced_data.get('location', {}).get('cleaned', '')
        radius = enhanced_data.get('radius', 1000)
        focus_industry = data.get('focus_industry', '')
        
        if not location:
            return jsonify({'success': False, 'error': 'Location is required'}), 400
        
        # Get comprehensive market overview
        market_overview = foursquare_api.get_market_overview(location, radius)
        
        # Get all local businesses
        all_businesses = foursquare_api.get_local_businesses(location, radius)
        cleaned_businesses = data_processor.clean_location_data(all_businesses)
        
        # Calculate market health
        market_health = data_processor.calculate_market_health_score(cleaned_businesses)
        
        # Identify market gaps
        market_gaps = data_processor.identify_market_gaps(cleaned_businesses)
        
        # Identify opportunities using business intelligence
        opportunities = business_intelligence.identify_opportunities(market_overview)
        
        # Filter by focus industry if specified
        if focus_industry:
            opportunities = [opp for opp in opportunities 
                           if focus_industry.lower() in opp.get('category', '').lower()]
        
        # Calculate location score
        location_score = data_processor.calculate_optimal_location_score(cleaned_businesses)
        
        # Generate comprehensive insights
        all_analysis_data = {
            'all_businesses': cleaned_businesses,
            'market_data': market_overview,
            'opportunities': opportunities,
            'market_gaps': market_gaps,
            'market_health': market_health
        }
        
        comprehensive_insights = data_processor.aggregate_market_insights(
            [], market_overview, opportunities
        )
        
        # Format response
        response_data = {
            'market_data': {
                **market_overview,
                **market_health,
                **location_score
            },
            'opportunities': opportunities,
            'market_gaps': market_gaps,
            'insights': comprehensive_insights,
            'location_info': enhanced_data['location'],
            'scan_parameters': {
                'radius': radius,
                'focus_industry': focus_industry,
                'total_businesses_analyzed': len(cleaned_businesses)
            }
        }
        
        return jsonify(data_processor.format_response_data(response_data))
        
    except Exception as e:
        app.logger.error(f"Error in market scanning: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Market scan failed. Please try again.'
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def api_generate_report():
    """Generate comprehensive business intelligence report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        enhanced_data = data_processor.validate_and_enhance_data(data)
        location = enhanced_data.get('location', {}).get('cleaned', '')
        business_type = enhanced_data.get('business_type', {}).get('standardized', '')
        
        if not location or not business_type:
            return jsonify({'success': False, 'error': 'Location and business type are required'}), 400
        
        # Gather all necessary data
        competitors = foursquare_api.search_competitors(location, business_type)
        market_overview = foursquare_api.get_market_overview(location)
        local_businesses = foursquare_api.get_local_businesses(location)
        
        # Process all data
        cleaned_competitors = data_processor.clean_location_data(competitors)
        cleaned_businesses = data_processor.clean_location_data(local_businesses)
        
        # Generate comprehensive analysis
        all_data = {
            'competitors': cleaned_competitors,
            'all_businesses': cleaned_businesses,
            'market_data': market_overview,
            'opportunities': business_intelligence.identify_opportunities(market_overview),
            'market_gaps': data_processor.identify_market_gaps(cleaned_businesses),
            'market_health': data_processor.calculate_market_health_score(cleaned_businesses)
        }
        
        # Generate comprehensive report
        comprehensive_report = data_processor.generate_comprehensive_report(all_data)
        
        return jsonify(data_processor.format_response_data(comprehensive_report))
        
    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Report generation failed. Please try again.'
        }), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': data_processor.validate_and_enhance_data({})['processed_at']
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again later.'
    }), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler('logs/localmind.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LocalMind application startup')
    
    app.run(debug=True, host='0.0.0.0', port=5000)