from flask import request, redirect, url_for, render_template, Flask, session
from mode import User
from flask_sqlalchemy import SQLAlchemy
from encrypt import validate_password
import os, datetime
from flask_login import LoginManager, login_required, logout_user, login_user

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///management.db'
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(days=8)
app.permanent_session_lifetime = datetime.timedelta(seconds=10 * 60)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not validate_password(user.password, request.form['password']):
            error = 'Invalid username or password'
        else:
            session.permanent = True
            try:
                request.form['remember']
            except:
                login_user(user)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                login_user(user=user, remember=True)
                return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', error=error)


@app.route("/settings")
@login_required
def settings():
    pass


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('login')


@app.route('/')
@login_required
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
