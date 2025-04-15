from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..model import db, User, ProfessionalDetails
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile_bp', __name__)
api = Api(profile_bp)

UPLOAD_FOLDER = 'path_to_save_attachments'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ProfileApi(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
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

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        data = request.form
        user.email = data.get('email')
        user.username = data.get('username')
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        user.full_name = data.get('full_name')
        user.address = data.get('address')
        user.pin_code = data.get('pin_code')

        if data.get('role') == 'professional':
            if not user.professional_details:
                user.professional_details = ProfessionalDetails(user_id=user.id)
            user.professional_details.service_name = data.get('service_name')
            user.professional_details.experience = data.get('experience')

        if 'attachment' in request.files:
            attachment = request.files['attachment']
            if allowed_file(attachment.filename):
                filename = secure_filename(attachment.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                attachment.save(file_path)
                user.professional_details.attachment = file_path
            else:
                return jsonify({"message": "Invalid file format"}), 400

        db.session.commit()

        return jsonify({"message": "Profile updated successfully"})

api.add_resource(ProfileApi, '/profile_update')
