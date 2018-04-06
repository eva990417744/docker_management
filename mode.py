from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///management.db'
db = SQLAlchemy(app)


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


if __name__ == '__main__':
    db.create_all()
# from encrypt import encrypt_password, validate_password
#
# user = User(username='admin', password=encrypt_password('admin'), email='admin@example.com')
# db.session.add(user)
# db.session.commit()
#
# user = User.query.filter_by(username='admin').first()
# print(validate_password(user.password, 'admin'))
