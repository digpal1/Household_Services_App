from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with, marshal
from ..model import db, Bookings, ProfessionalDetails, User
from household.resources.cache_config import cache

booking_bp = Blueprint('booking_bp', __name__)

api = Api(booking_bp)
src_parser = reqparse.RequestParser()
src_parser.add_argument('service_id', type=int, required=True, help='Service is required')
src_parser.add_argument('user_id', type=int, required=True, help='User ID is required')
src_parser.add_argument('package_id', type=int, required=True, help='Package ID is required')


booking_fields = {
    'id': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
    'package_id': fields.Integer,
    'status': fields.Boolean,
    'action': fields.Boolean,
    'request_date': fields.String,
    'complete_date': fields.String
}

class BookingApi(Resource):
    def post(self):
        args = src_parser.parse_args()

        service_id = args['service_id']
        user_id = args['user_id']
        package_id = args['package_id']

        check_bookings = Bookings.query.filter_by(user_id=user_id, package_id=package_id).first()
        # print(check_bookings.status)
        if check_bookings is None or check_bookings.status == True:
            professional_id = ProfessionalDetails.query.filter_by(id=service_id).first().user_id
            professional_name = User.query.filter_by(id=professional_id).first().full_name

            booking = Bookings(
                service_id=service_id,
                user_id=user_id,
                package_id=package_id,
                professional_name=professional_name,
                request_date=datetime.now()
            )
            db.session.add(booking)
            db.session.commit()

            return jsonify({'message': 'Booking created successfully!', 'booking_id': booking.id})

        else:
            return jsonify({'message': 'Booking already exists or open!'})

    @marshal_with(booking_fields)
    @cache.cached(timeout=10)
    def get(self, user_id):
        try:
            bookings = Bookings.query.filter_by(user_id=user_id).all()
            if not bookings:
                return jsonify([]), 200
            return bookings, 200
        except Exception as e:
            print(f"Error fetching bookings:{e}")
            return jsonify({"error":"Failed to fetch bookings"}), 500

        
 
    @marshal_with(booking_fields)
    def delete(self, user_id):
        booking_id = request.args.get('booking_id')
        # print(booking_id)
        
        if booking_id is None:
            return jsonify({'message': 'Booking ID is required'}), 400

        booking = Bookings.query.filter_by(user_id=user_id, id=booking_id).first()
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        if booking:            
            db.session.delete(booking)
            db.session.commit()
            return jsonify({'message': 'Booking canceled successfully'}), 200
        else:
            return jsonify({"error": "Booking not found"}), 404

    

api.add_resource(BookingApi, '/bookings', '/bookings/<int:user_id>')
