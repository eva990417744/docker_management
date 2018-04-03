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
            error = '账号或密码错误'
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
            error = '账号或密码错误'
        else:
            try:
                if request.form['new_password_again'] != request.form['new_password']:
                    error = '两次输入的新密码不一致'
            except:
                error = '请填写所有项目'
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
            {'id': image.attrs['Id'][7:17], 'tags': image.attrs['RepoTags'][0], 'created': image.attrs['Created'][:10],
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
    version = client.version()
    info = client.info()
    return render_template('configuration.html', version=version, info=info)


@app.route('/containers')
@login_required
def containers():
    containers = []
    for container in client.containers.list(all=True):
        a = {'id': container.attrs['Id'], 'name': container.attrs['Name'],
             'image': container.attrs['Config']['Image'], 'status': container.attrs['State']['Status']}
        if container.attrs['Path'] != container.attrs['Config']['Cmd'][0]:
            a['cmd'] = container.attrs['Path'] + '  ' + container.attrs['Config']['Cmd'][0]
        else:
            a['cmd'] = container.attrs['Path']
        try:
            b = list(container.attrs['NetworkSettings']['Ports'].keys())[0]
            if container.attrs['NetworkSettings']['Ports'][b] is not None:
                a['ports'] = (container.attrs['NetworkSettings']['Ports'][b][0]['HostIp'] + ':' +
                              container.attrs['NetworkSettings']['Ports'][b][0][
                                  'HostPort'] + '->' + b)
            else:
                a['ports'] = b
        except:
            a['ports'] = ''

        containers.append(a)
    return render_template('containers.html', containers=containers)


@app.route('/container/<id>')
@login_required
def container(id):
    a = client.containers.get(id).attrs
    return render_template('container.html', container=a)


@app.route('/dockerhub')
@login_required
def dockerhub(name='alpine'):
    if request.method == 'GET':
        images = client.images.search(name)
        return render_template('dockerhub.html', images=images)
    else:
        images = client.images.search(request.form['term'])
        return render_template('dockerhub.html', images=images)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
