from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with, marshal
from ..model import db, Packages, SubmitFeedback, Bookings

packages_bp = Blueprint('packages_bp', __name__)

api = Api(packages_bp)
src_parser = reqparse.RequestParser()
src_parser.add_argument('service_id', type=int, required=True, help='Service is required')
src_parser.add_argument('user_id', type=int, required=True, help='User ID is required')
src_parser.add_argument('package_name', type=str, required=True, help='Package name is required')
src_parser.add_argument('description', type=str, required=True, help='Description is required')
src_parser.add_argument('price', type=int, required=True, help='Price is required')

package_fields = {
    'id': fields.Integer,
    'package_name': fields.String,
    'description': fields.String,
    'price': fields.Integer,
    'service_id': fields.Integer,
    'user_id': fields.Integer,
    'average_rating': fields.Float,
}


class PackagesApi(Resource):
    def get(self, package_id=None):
        service_id = request.args.get('service_id')
        print("Service ID:", service_id)

        if package_id is None:
            print("Fetching all packages...")

            if service_id:
                packages = Packages.query.filter_by(service_id=service_id).all()
                print("Filtered Packages:", packages)
            else:
                packages = Packages.query.all()
                print("All Packages:", packages)

            for package in packages:
                print("Calculating for Package ID:", package.id)
                
                # Fetch all bookings for the current package
                bookings = Bookings.query.filter_by(package_id=package.id).all()
                print("Related Bookings:",bookings)
                
                feedbacks = []
                # Collect feedbacks related to each booking
                for booking in bookings:
                    feedback = SubmitFeedback.query.filter_by(booking_id=booking.id).all()
                    feedbacks.extend(feedback)

                print("Feedbacks for Package ID:", package.id, feedbacks)

                # Filter out feedbacks with None ratings
                valid_feedbacks = [fb.rating for fb in feedbacks if fb.rating is not None]

                if valid_feedbacks:
                    avg_rating = sum(valid_feedbacks) / len(valid_feedbacks)
                    package.average_rating = round(avg_rating, 1)
                else:
                    package.average_rating = None

            return {"packages": [marshal(package, package_fields) for package in packages]}

        else:
            package = Packages.query.get(package_id)
            if package:
                # Calculate average rating for a specific package
                bookings = Bookings.query.filter_by(package_id=package.id).all()
                feedbacks = []
                for booking in bookings:
                    feedback = SubmitFeedback.query.filter_by(booking_id=booking.id).all()
                    feedbacks.extend(feedback)

                if feedbacks:
                    avg_rating = sum(feedback.rating for feedback in feedbacks) / len(feedbacks)
                    package.average_rating = round(avg_rating, 1)
                else:
                    package.average_rating = None 

                return marshal(package, package_fields)
            else:
                return {"message": "Package not found"}, 404


    def post(self):
        try:
            args = src_parser.parse_args()
            new_package = Packages(
                package_name=args['package_name'],
                description=args['description'],
                price=args['price'],
                service_id=args['service_id'],
                user_id=args['user_id']
            )
            db.session.add(new_package)
            db.session.commit()
            return {"message": "Package created successfully"}, 201
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500

    @marshal_with(package_fields)
    def delete(self, package_id):
        try:
            package = Packages.query.get(package_id)
            if package:
                db.session.delete(package)
                db.session.commit()
                return {"message": "Package deleted successfully"}, 200
            else:
                return {"message": "Package not found"}, 404
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500
        
    @marshal_with(package_fields)
    def put(self, package_id):
        try:
            args = src_parser.parse_args()
            package = Packages.query.get(package_id)
            if package:
                package.package_name = args['package_name']
                package.description = args['description']
                package.price = args['price']
                package.service_id = args['service_id']
                package.user_id = args['user_id']
                db.session.commit()
                return {"message": "Package updated successfully"}, 200
            else:
                return {"message": "Package not found"}, 404
        except Exception as error:
            db.session.rollback()
            return {"message": str(error)}, 500

api.add_resource(PackagesApi, '/packages', '/packages/<int:package_id>')
