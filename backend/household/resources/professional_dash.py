from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from ..model import db, Bookings, User
from sqlalchemy import and_

professional_dash_bp = Blueprint('professional_dash_bp', __name__)
api = Api(professional_dash_bp)

src_parser = reqparse.RequestParser()
src_parser.add_argument('user_id', type=int, required=True, help='User id is required')

booking_fields = {
    'id': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
    'package_id': fields.Integer,
    'status': fields.Boolean,
    'request_date': fields.String,
    'complete_date': fields.String,
    'reject_date' : fields.String,
    'professional_name': fields.String,
    'action': fields.Boolean
}

customer_fields = {
    'user_id': fields.Integer,
    'username': fields.String,
    'full_name': fields.String,
    'address': fields.String,
    'pin_code': fields.String
 }

service_fields = {
    'id': fields.Integer,
    'service_name': fields.String,
    'description': fields.String,
    'base_price': fields.Integer
}
package_fields = {
    'id': fields.Integer,
    'package_name': fields.String,
    'description': fields.String,
    'price': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
}
professional_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "experience": fields.Integer 
}

professional_composite_fields = {
    'booking': fields.Nested(booking_fields),
    'service': fields.Nested(service_fields),
    'package': fields.Nested(package_fields),
    'professional': fields.Nested(professional_fields),
    'customer': fields.Nested(customer_fields)
}

class ProfessionalDashApi(Resource):
    @marshal_with(professional_composite_fields)
    def get(self):
        user_id = request.args.get('user_id')
        # print(user_id, args)

        if user_id is None:
            return {"message": "User id is required"}, 400

        professional_detail = User.query.filter_by(id=user_id).first()
        # print(professional_detail)
        if not professional_detail:
            return {"message": "Professional not found or not activated, contact admin"}, 404
        
        professional_name = professional_detail.full_name
        # print(professional_name)

        bookings = Bookings.query.filter_by(professional_name=professional_name).all()


        if not bookings:
            return {"message": "No bookings found"}, 404

        composite_response = []
        for booking in bookings:
            service = booking.service 
            package = booking.package  
            user = booking.user
   
            composite_response.append({
                'booking': {
                    'id': booking.id,
                    'service_id': booking.service_id,
                    'user_id': booking.user_id,
                    'package_id': booking.package_id,
                    'status': booking.status,
                    'request_date': booking.request_date,
                    'reject_date': booking.request_date,
                    'complete_date': booking.complete_date,
                    'professional_name': booking.professional_name,
                    'action': booking.action
                } if booking else None,


                'customer': {
                    'user_id': booking.user_id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'address': user.address,
                    'pin_code': user.pin_code
                } if user else None,
                
                'service': {
                    'id': service.id,
                    'service_name': service.service_name,
                    'description': service.description,
                    'base_price': service.base_price,
                } if service else None,
                'package': {
                    'id': package.id,
                    'package_name': package.package_name,
                    'description': package.description,
                    'price': package.price,
                    'service_id': package.service_id,
                    'user_id': package.user_id,
                } if package else None,
                
                'professional': {
                    'id': professional_detail.id,
                    'username': professional_detail.username,
                }
            })
        return composite_response, 200
    
    def post(self):
        data = request.get_json()
        booking_id = data.get('booking_id')
        action = data.get('status')

        if booking_id is None or action is None:
            return {"message": "Booking ID and new status are required"}, 400

        booking = Bookings.query.filter_by(id=booking_id).first()
        if not booking:
            return {"message": "Booking not found"}, 404

        booking.action = action
        db.session.commit()
        return {"message": "Booking status updated successfully"}, 200

api.add_resource(ProfessionalDashApi, '/professional_dash','/professional_dash/<int:user_id>')
