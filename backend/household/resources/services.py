from datetime import datetime
from flask import Blueprint, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with, marshal
from ..model import db, Services
from household.resources.cache_config import cache


services_bp = Blueprint('services_bp', __name__)

api = Api(services_bp)
src_parser = reqparse.RequestParser()
src_parser.add_argument('service_name', type=str, required=True, help='Service name is required')
src_parser.add_argument('description', type=str, required=True, help='Description is required')
src_parser.add_argument('base_price', type=int, required=True, help='Base price is required')

service_fields = {
    'id': fields.Integer,
    'service_name': fields.String,
    'description': fields.String,
    'base_price': fields.Integer
}

class ServicesApi(Resource):

    @cache.cached(timeout=10)
    def get(self, service_id=None):
        if service_id is None:
            services = Services.query.all()
            return {"services": [marshal(service, service_fields) for service in services]}
        else:
            service = Services.query.get(service_id)
            if service:
                return marshal(service, service_fields)
            else:
                return {"message": "Service not found"}, 404
    
    @marshal_with(service_fields)
    def post(self):
        try:
            args = src_parser.parse_args()
            new_service = Services(
                service_name=args['service_name'],
                description=args['description'],
                base_price=args['base_price']
            )
            db.session.add(new_service)
            db.session.commit()
            return {"message": "Service created successfully"}, 201
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500
        
    @marshal_with(service_fields)
    def delete(self, service_id):
        try:
            service = Services.query.get(service_id)
            if service:
                db.session.delete(service)
                db.session.commit()
                return {"message": "Service deleted successfully"}, 200
            else:
                return {"message": "Service not found"}, 404
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500
        
    @marshal_with(service_fields)
    def put(self, service_id):
        try:
            args = src_parser.parse_args()
            service = Services.query.get(service_id)
            if service:
                service.service_name = args['service_name']
                service.description = args['description']
                service.base_price = args['base_price']
                db.session.commit()
                return {"message": "Service updated successfully"}, 200
            else:
                return {"message": "Service not found"}, 404
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500

api.add_resource(ServicesApi, '/services', '/services/<int:service_id>', endpoint='service')