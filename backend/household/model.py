from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RolesUser(db.Model):
    __tablename__ = 'roles_user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(128), unique=True)
    address = db.Column(db.String(120))
    pin_code = db.Column(db.String(20))

    roles = db.relationship('Role', secondary='roles_user', backref=db.backref('users', lazy='dynamic'))
    professional_details = db.relationship('ProfessionalDetails', uselist=False, back_populates='user', cascade='all, delete-orphan')
    packages = db.relationship('Packages', back_populates='user', cascade='all, delete-orphan')
    bookings = db.relationship('Bookings', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class ProfessionalDetails(db.Model):
    __tablename__ = 'professional_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_name = db.Column(db.String(80), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    attachment = db.Column(db.String(250), nullable=True)

    user = db.relationship('User', back_populates='professional_details')


class Services(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    base_price = db.Column(db.Integer)

    packages = db.relationship('Packages', back_populates='service', cascade='all, delete-orphan')
    bookings = db.relationship('Bookings', back_populates='service', cascade='all, delete-orphan')


class Packages(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    price = db.Column(db.Integer)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='packages')
    service = db.relationship('Services', back_populates='packages')
    bookings = db.relationship('Bookings', back_populates='package', cascade='all, delete-orphan')


class Bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    request_date = db.Column(db.Date)
    professional_name = db.Column(db.String(80))
    action = db.Column(db.Boolean())
    complete_date = db.Column(db.Date)
    status = db.Column(db.Boolean())

    user = db.relationship('User', back_populates='bookings')
    service = db.relationship('Services', back_populates='bookings')
    package = db.relationship('Packages', back_populates='bookings')
    submit_feedback = db.relationship('SubmitFeedback', uselist=False, back_populates='booking')

    def __repr__(self):
        return f'<Bookings {self.id} - {self.status}>'


class SubmitFeedback(db.Model):
    __tablename__ = 'submit_feedback'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rating = db.Column(db.Integer)
    remarks = db.Column(db.String(120))

    booking = db.relationship('Bookings', back_populates='submit_feedback')
