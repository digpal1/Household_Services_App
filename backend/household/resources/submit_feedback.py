from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from ..model import db, Bookings, SubmitFeedback

submit_feedback_bp = Blueprint('submit_feedback_bp', __name__)
api = Api(submit_feedback_bp)

src_parser = reqparse.RequestParser()
src_parser.add_argument('bookingId', type=int, required=True, help='Booking ID is required')
src_parser.add_argument('rating', type=int, required=True, help='Rating is required')
src_parser.add_argument('remarks', type=str, required=True, help='Feedback is required')



feedback_fields = {
    'id': fields.Integer,
    'booking_id': fields.Integer,
    'rating': fields.Integer,
    'remarks': fields.String,
}

class FeedbackApi(Resource):
    def get(self, user_id):
        pass

    def post(self):
        args = src_parser.parse_args()
        booking_id = args['bookingId']
        rating = args['rating']
        remarks = args['remarks']
        booking = Bookings.query.filter_by(id=booking_id).first()
        if not booking:
            return {'status': 'error', 'message': 'Booking not found'}
        
        booking.status = 1
        booking.complete_date = datetime.now()
        
        submit_feedback = SubmitFeedback(booking_id=booking_id, rating=rating, remarks=remarks)
        db.session.add(submit_feedback)
        db.session.commit()
        return {'status': 'success'}      

api.add_resource(FeedbackApi, '/submit_feedback')