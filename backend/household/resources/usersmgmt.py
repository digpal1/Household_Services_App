from flask import Blueprint, jsonify, request
from flask_restful import Resource, reqparse, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from ..model import User, db, ProfessionalDetails
from ..sec import user_datastore
from werkzeug.utils import secure_filename
from flask_restful import Api, Resource
import os

user_bp = Blueprint('user_bp', __name__)
api = Api(user_bp)


role_fields = {
    "id": fields.Integer,
    "name": fields.String
}

professional_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "service_name": fields.String,
    "experience": fields.Integer
}

user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "full_name": fields.String,
    "email": fields.String,
    "roles": fields.List(fields.Nested(role_fields)),
    "address": fields.String,
    "pin_code": fields.String,
    "active": fields.Boolean,
    "professional_details": fields.Nested(professional_fields, allow_null=True) 
}

class UserResource(Resource):
    def get(self):
        try:
            users = User.query.all()
            # print("Users fetched:", users)
            if not users:
                return {"message": "No users found"}, 404

            user_data = []
            for user in users:
                user_info=marshal(user, user_fields)
                if user.professional_details:
                    user_info['service_name'] = user.professional_details.service_name
                    user_info['experience'] = user.professional_details.experience
                user_data.append(user_info)
            return {"users": user_data}, 200

        except Exception as e:
            print("Error fetching users:", str(e))
            return {"error": "An error occurred while fetching users"}, 500



    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

api.add_resource(UserResource, '/users')


class UserAction(Resource):
    @jwt_required()
    def post(self, user_id):
        """Update user details."""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('full_name', type=str, required=False)
        parser.add_argument('address', type=str, required=False)
        parser.add_argument('pin_code', type=str, required=False)
        parser.add_argument('role', type=str, required=True)
        parser.add_argument('service_name', type=str, required=False)
        parser.add_argument('experience', type=int, required=False)
        parser.add_argument('attachment', type=str, required=False)
        args = parser.parse_args()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if user_id in [1, 2, 3]:  # Assuming system-admin roles cannot be updated
            return jsonify({"message": "Cannot update system users"}), 403

        # Update user attributes
        user.username = args['username']
        user.email = args['email']
        if args['password']:
            user.password = check_password_hash(args['password'])  # Hash password securely

        user.full_name = args.get('full_name')
        user.address = args.get('address')
        user.pin_code = args.get('pin_code')
        user.role = args['role']  # Assign new role

        # Professional-specific fields
        if user.role == 'Professional':
            user.service_name = args.get('service_name')
            user.experience = args.get('experience')
            user.attachment = args.get('attachment')

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200


    def delete(self, user_id):
        """Delete a user."""
        user = user_datastore.find_user(id=user_id)
        if user is None:
            return {"error": "User not found"}, 404
        if user_id == 1:
            return {"error": "Cannot delete system admin user"}, 403
        # if user_id == 2:
        #     return {"error": "Cannot delete system professional user"}, 403
        # if user_id == 3:
        #     return {"error": "Cannot delete system  user"}, 403
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200

api.add_resource(UserAction, '/users/<int:user_id>')


class UserToggleActiveStatus(Resource):
    def put(self, user_id):
        try:
            # Get the JSON data from the request
            data = request.get_json()
            # Retrieve 'active' value from request data
            activate = data.get('active')

            if activate is None:
                return {"message": "Missing 'active' field in request body"}, 400

            print(f"Received user_id: {user_id}, activate: {activate}")

            # Find the user by ID
            user = user_datastore.find_user(id=user_id)
            print(f"Found user: {user}")

            if user is None:
                return {"message": "User not found"}, 404

            if user_id == 1:
                return {"message": "Cannot deactivate admin user"}, 403

            # Check role ID and activate/deactivate accordingly
            if user_id != 1: 
                user.active = activate
                db.session.commit()
                message = f"User : {user.full_name} successfully activated!" if activate else f"User : {user.full_name} successfully deactivated"
                return {"message": message}, 200

            else:
                user.active = not user.active
                db.session.commit()
                return {"message": "Success! User active status toggled successfully"}, 200

        except Exception as e:
            print("Error in toggling user active status:", str(e))
            return {"error": "An error occurred while toggling user status"}, 500

api.add_resource(UserToggleActiveStatus, '/users/<int:user_id>/toggle_active_status')

class ProfileApi(Resource):
    def get(self, user_id=None):
        # print(f"Received user_id: {user_id}")
        user = User.query.get(user_id)
        # print(f"Found user: {user}")
        
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_data = {
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'address': user.address,
            'pin_code': user.pin_code,
            'role': 'professional' if user.professional_details else 'user',
            'service_name': user.professional_details.service_name if user.professional_details else '',
            'experience': user.professional_details.experience if user.professional_details else ''
        }
        return jsonify({'user': user_data})

    def put(self, user_id=None): 
        try:
            # print(f"Received user_id: {user_id}")
            data = request.get_json()
            # print(data)

            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            if not user:
                return {"error": "User not found"}, 404

            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'address' in data:
                user.address = data['address']
            if 'email' in data:
                user.email = data['email']
            if 'experience' in data:
                user.experience = data['experience']
            if 'pin_code' in data:
                user.pin_code = data['pin_code']
            if 'role' in data:
                user.role = data['role']
            if 'service_name' in data:
                user.service_name = data['service_name']
            if 'username' in data:
                user.username = data['username']

            db.session.commit()
            return {"message": "Profile updated successfully"}, 200

        except Exception as e:
            print("Error updating user:", str(e))
            return {"error": "An error occurred while updating user"}, 500

api.add_resource(ProfileApi, '/api/profile_update', '/profile_update/<int:user_id>')
