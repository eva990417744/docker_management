from flask import request, redirect, url_for, render_template, Flask, session
from mode import User
from flask_sqlalchemy import SQLAlchemy
from encrypt import validate_password, encrypt_password
import os, datetime, docker
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

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
client = docker.DockerClient(base_url='tcp://sumeragibi.date:2376')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = db.session.query(User).filter_by(username=request.form['username']).first()
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


@app.route("/user", methods=['GET', 'POST'])
@login_required
def user():
    error = None
    if request.method == 'POST':
        user = current_user
        if user is None or not validate_password(user.password, request.form['password']):
            error = 'Invalid username or password'
        else:
            try:
                if request.form['new_password_again'] != request.form['new_password']:
                    error = 'Inconsistent new password'
            except:
                error = 'Please fill in all the items'
            else:
                change = db.session.query(User).filter_by(username=user.username).first()
                change.password = encrypt_password(request.form['new_password'])
                db.session.add(change)
                db.session.commit()
                logout_user()
                return redirect('/')
    return render_template('user.html', error=error)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/images')
@login_required
def images():
    images = []
    for image in client.images.list():
        images.append(
            {'id': image.attrs['Id'][7:19], 'tags': image.attrs['RepoTags'][0], 'created': image.attrs['Created'][:10],
             'size': str(round(int(image.attrs['VirtualSize']) / 1048576, 2)) + 'MB'})
    return render_template('images.html', images=images)


@app.route('/image/<id>')
@login_required
def image(id):
    image = client.images.get(id)
    return render_template('image.html', image=image.attrs)


@app.route('/configuration')
@login_required
def configuration():
    config = client.configs.list()
    for con in config:
        print(con.attrs)


@app.route('containers')
@login_required
def containers():
    return ''


if __name__ == '__main__':
    app.run(debug=True, port=5000)
