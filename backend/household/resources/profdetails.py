from datetime import datetime
from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from ..model import db, User, ProfessionalDetails, Services
from sqlalchemy import and_

prof_details_bp = Blueprint('prof_details_bp', __name__)
api = Api(prof_details_bp)

role_fields = {
    "id": fields.Integer,
    "name": fields.String
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

professional_fields = {
    "id": fields.Integer,
    "full_name": fields.String,
    "email": fields.String,
    "experience": fields.Integer,
    "service_name": fields.String,
    "address": fields.String,
    "pin_code": fields.String,
    "active": fields.Boolean,
    "attachment": fields.String
}

prof_composite_fields = {
    'professional': fields.Nested(professional_fields),
    'service': fields.Nested(service_fields)
}

# Professional details resource
class ProfDetails(Resource):
    @marshal_with(prof_composite_fields)
    def get(self, id):
        professional = ProfessionalDetails.query.filter_by(user_id=id).first()
        
        if not professional:
            return {"message": "Professional details not found"}, 404

        user = User.query.filter_by(id=id).first()

        service = Services.query.filter_by(service_name=professional.service_name).first()

        response_data = {
            'professional': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'experience': professional.experience,
                'service_name': professional.service_name,
                'address': user.address,
                'pin_code': user.pin_code,
                'active': user.active,
                'attachment': professional.attachment
            },
            'service': service,
        }

        return response_data

api.add_resource(ProfDetails, '/profdetails/<int:id>')
