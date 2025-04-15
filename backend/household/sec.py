from flask_security import SQLAlchemyUserDatastore
from .model import User, Role, db, RolesUser


user_datastore = SQLAlchemyUserDatastore(db, User, Role, RolesUser)
