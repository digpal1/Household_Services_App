from flask import Blueprint, request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from ..sec import user_datastore
from ..model import db, Role, User, ProfessionalDetails

from flask_restful import Api, Resource

auth_bp = Blueprint('auth_bp', __name__)

api = Api(auth_bp)

# Login API
class LoginApi(Resource):
    def post(self):
        # Required username and password in the request body.

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        username = args['username']

        user = user_datastore.find_user(username=username)
        print(user.password)
        if not user:
            return {"message": "User not found. Check your credentials or sign up."}, 404

        # Verify password using inbuilt check_password_hash function
        if not check_password_hash(user.password, args['password']):
            return {"message": "Invalid credentials. Please try again."}, 401
        
        if not user.active:
            return {"message": "User is not active. Please contact admin."}, 401
        
        # Generate access token if user is authenticated
        if user:
            access_token = create_access_token(identity=user.roles[0].name)
            user_info = {"id": user.id, "username": user.username,"full_name": user.full_name, "email": user.email, "role": user.roles[0].name}
            return {"access_token": access_token, "user": user_info}, 200
        

    @jwt_required()
    def get(self):
        """
        Placeholder method to verify if the user is logged in.
        Requires a valid JWT token.
        """
        return jsonify({"message": "User is logged in."}), 200
    
api.add_resource(LoginApi, '/login')


class SignupApi(Resource):
    def post(self):
        user_parser = reqparse.RequestParser()
        user_parser.add_argument('role', type=str, required=True, help="User's role name")
        user_parser.add_argument('username', type=str, required=True, help='Username of the user')
        user_parser.add_argument('email', type=str, required=True, help='Email of the user')
        user_parser.add_argument('password', type=str, required=True, help='Password of the user')
        user_parser.add_argument('full_name', type=str, required=True, help="User's full name")
        user_parser.add_argument('address', type=str, required=True, help="User's address")
        user_parser.add_argument('pin_code', type=str, required=True, help="User's pin code")

        args = user_parser.parse_args()
        # print(args)

        role_name = args['role']
        username = args['username']
        email = args['email']
        password = args['password']
        full_name = args['full_name']
        address = args['address']
        pin_code = args['pin_code']

        try:
            # Retrieving the role based on the role name
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return {'message': f'Role {role_name} does not exist.'}, 400

            # Check if the username already exists
            if User.query.filter_by(username=username).first():
                return {'message': f'Username {username} already exists!'}, 400

            # If the role is "user", create a normal user
            if role_name == "user":
                user = user_datastore.create_user(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    roles=[role],
                    full_name=full_name,
                    address=address,
                    pin_code=pin_code,
                    active=True
                )
                db.session.add(user)
                db.session.commit()

            # If the role is "professional", additional fields are required
            elif role_name == "professional":
                user_parser.add_argument('service_name', type=str, required=True, help="Professional's service name")
                user_parser.add_argument('experience', type=int, required=True, help="Professional's experience")
                user_parser.add_argument('attachment', type=str, required=True, help="Professional's attachment")

                professional_args = user_parser.parse_args()
                # print(professional_args)

                service_name = professional_args['service_name']
                experience = professional_args['experience']
                attachment = professional_args['attachment']

                # Create the user
                prof = user_datastore.create_user(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    full_name=full_name,
                    address=address,
                    pin_code=pin_code,
                    roles=[role],
                    active=False
                )
                db.session.add(prof)
                db.session.commit()

                # Add professional details
                professional_details = ProfessionalDetails(
                    user_id=prof.id,
                    service_name=service_name,
                    experience=experience,
                    attachment=attachment
                )
                # print(professional_details)
                db.session.add(professional_details)
                db.session.commit()

            return {'message': f'Congratulations! You have successfully registered as {username}.'}, 200

        except Exception as e:
            db.session.rollback()
            return {"message": f"Error occurred: {str(e)}"}, 500

    def get(self):
        pass

api.add_resource(SignupApi, '/signup')
