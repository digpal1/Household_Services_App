import os
from flask import Flask, send_from_directory, jsonify, make_response
from flask_restful import Api, Resource
from sqlalchemy import inspect
from flask_cors import CORS
from flask_security import Security
from flask_jwt_extended import JWTManager
import redis
from household.config import DevelopmentConfig, ProductionConfig
from household.sec import user_datastore
from household.model import db
from household.resources.cache_config import cache

# Path to the directory where PDFs are stored
ATTACH_FOLDER = 'pdf_files'
CSV_FOLDER = 'csv'

def create_app(environment='development'):
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Redis and Caching
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Load configuration based on environment
    if environment == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize the cache with the app
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEBUG'] = True
    cache.init_app(app)

    # Initialize Extensions
    JWTManager(app)
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Security(app, user_datastore)
    api = Api(app)

    # Register Blueprints
    from household.resources.greetings import greeting_bp
    from household.resources.auth import auth_bp
    from household.resources.usersmgmt import user_bp
    from household.resources.services import services_bp
    from household.resources.addpackages import packages_bp
    from household.resources.booking import booking_bp
    from household.resources.booking_approval import bookingapproval_bp
    from household.resources.professional_dash import professional_dash_bp
    from household.resources.submit_feedback import submit_feedback_bp
    from household.resources.all_bookings import all_bookings_bp
    from household.resources.profdetails import prof_details_bp

    blueprints = [
        (greeting_bp, '/api'),
        (auth_bp, '/api'),
        (user_bp, '/api'),
        (services_bp, '/api'),
        (packages_bp, '/api'),
        (booking_bp, '/api'),
        (bookingapproval_bp, '/api'),
        (professional_dash_bp, '/api'),
        (submit_feedback_bp, '/api'),
        (all_bookings_bp, '/api'),
        (prof_details_bp, '/api'),
    ]
    for blueprint, prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)

    # Route to Serve PDF Files
    @app.route('/pdf_files/<path:filename>')
    def serve_pdf(filename):
        return send_from_directory(ATTACH_FOLDER, filename)
    
    @app.route('/csv/<path:filename>')
    def serve_csv(filename):
        return send_from_directory(CSV_FOLDER, filename, as_attachment=True)

        # Example of a cached route
    @app.route('/some_route')
    @cache.cached(timeout=60, key_prefix='some_cache_key')
    def some_route():
        # Simulate fetching data or performing operations
        data = {"message": "This is cached!"}
        return jsonify(data)
    
    return app

class ExportCSVResource(Resource):
    """API Resource to export service data as CSV."""

    def post(self, user_id):
        from tasks import export_closed_service_as_csv
        try:
            csv_data = export_closed_service_as_csv(user_id)
            response = make_response(csv_data)
            response.headers['Content-Disposition'] = 'attachment; filename=closed_service_requests.csv'
            response.headers['Content-Type'] = 'text/csv'
            return response
        except Exception as e:
            return jsonify({'message': f"Error exporting CSV: {str(e)}"}), 500
        
        
def create_initial_data(app):
    """Create initial data and tables if not already present."""
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")
        
        expected_tables = ['packages', 'professional_details', 'role', 'roles_user', 'services', 'user', 'bookings', 'submit_feedback']
        missing_tables = [table for table in expected_tables if table not in tables]
        print(f"Missing tables: {missing_tables}")

        if missing_tables:
            try:
                db.create_all()
                print("Missing Tables created successfully.")
            except Exception as e:
                print(f"Error creating tables: {e}")
        else:
            print("All tables already exist.")


if __name__ == "__main__":
    environment = os.getenv('FLASK_ENV', 'development')
    app = create_app(environment)
    create_initial_data(app)
    app.run(debug=True)
