from flask import Flask, Response, render_template, request
from flask.ext.login import LoginManager, UserMixin, login_required

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('frontpage.html')
    elif request.method == 'POST':
        login_user(request.form["username"])

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        if not next_is_valid(next):
            return flask.abort(400)

        return render_template('frontpage.html', username = request.form["username"])

if __name__ == '__main__':
    app.run(debug=True)
