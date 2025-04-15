from datetime import datetime
from flask import Blueprint, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from ..model import db, Bookings
from household.resources.cache_config import cache

all_bookings_bp = Blueprint('all_bookings_bp', __name__)
api = Api(all_bookings_bp)

booking_fields = {
    'id': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
    'package_id': fields.Integer,
    'status': fields.Boolean,
    'request_date': fields.String,
    'complete_date': fields.String,
    'reject_date': fields.String,
    'professional_name': fields.String,
    'action': fields.Boolean
}


class AllBookings(Resource):
    @marshal_with(booking_fields)
    @cache.cached(timeout=10)
    def get(self):
        bookings = Bookings.query.all()
        return bookings

api.add_resource(AllBookings, '/all_bookings')
