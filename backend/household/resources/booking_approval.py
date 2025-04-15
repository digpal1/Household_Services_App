from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from ..model import db, Bookings, Packages, Services, ProfessionalDetails
from household.resources.cache_config import cache

bookingapproval_bp = Blueprint('bookingapproval_bp', __name__)
api = Api(bookingapproval_bp)

# Request parser setup
src_parser = reqparse.RequestParser()
src_parser.add_argument('service_id', type=int, required=True, help='Service is required')
src_parser.add_argument('user_id', type=int, required=True, help='User ID is required')
src_parser.add_argument('package_id', type=int, required=True, help='Package ID is required')

# Field definitions
service_fields = {
    'id': fields.Integer,
    'service_name': fields.String,
    'description': fields.String,
    'base_price': fields.Integer
}

professional_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "experience": fields.Integer 
}

package_fields = {
    'id': fields.Integer,
    'package_name': fields.String,
    'description': fields.String,
    'price': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
}

booking_fields = {
    'id': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
    'professional_name': fields.String,
    'package_id': fields.Integer,
    'status': fields.Boolean,
    'request_date': fields.String,
    'complete_date': fields.String,
    'reject_date': fields.String,
    'action': fields.Boolean
}

# Composite fields
composite_fields = {
    "booking": fields.Nested(booking_fields),
    "service": fields.Nested(service_fields),
    "package": fields.Nested(package_fields),
    "professional": fields.Nested(professional_fields)
}

class BookingApprovalApi(Resource):

    @marshal_with(composite_fields)
    @cache.cached(timeout=10)
    def get(self, user_id):
        try:
            bookings = Bookings.query.filter_by(user_id=user_id).all()
            # print(f"Bookings for user {user_id}: {bookings}")

            if not bookings:
                return [], 200

            result = []
            for booking in bookings:
                service = Services.query.filter_by(id=booking.service_id).first()
                package = Packages.query.filter_by(id=booking.package_id).first()

                professionals = ProfessionalDetails.query.filter_by(service_name=service.service_name).first()
                # print(professionals)


                result.append({
                    "booking": booking,
                    "service": service,
                    "package": package,
                    "request_date": booking.request_date.strftime, 
                    "reject_date": booking.request_date.strftime,
                    "professional": professionals
                })

            return result, 200

        except Exception as e:
            print(f"Error fetching bookings for user {user_id}: {str(e)}")
            return {"error": "Failed to fetch bookings"}, 500

api.add_resource(BookingApprovalApi, '/bookingapproval/<int:user_id>')
