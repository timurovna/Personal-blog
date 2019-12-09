import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, UserMixin, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "personalblog.db"))

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    text = db.Column(db.String(500), unique=False, nullable=False)
    date = db.Column(db.String(100), default=datetime.now())
    user_id = db.Column(db.Integer, unique=False, nullable=False)

    def get_user(self):
        return User.query.filter_by(id=self.user_id).first()

    def get_comments(self):
        return Comment.query.filter_by(post_id=self.id).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    date_of_birth = db.Column(db.String(15), unique=False, nullable=False)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()


class Comment(db.Model):
    post_id = db.Column(db.Integer, unique=False, nullable=False)
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    text = db.Column(db.String(500), unique=False, nullable=False)
    author = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(100), default=datetime.now())
    user_id = db.Column(db.Integer, unique=False, nullable=False)


@app.route('/')
def heading():
    return render_template('index.html')


@app.route('/my_posts', methods = ['POST', 'GET'])
def my_posts():
    a = request.form
    if 'mypost' in a and 'postheading' in a and current_user.is_authenticated:
        text = a['mypost']
        title = a['postheading']
        my_post = Post(user_id=current_user.id, title=title, text=text)
        db.session.add(my_post)
        db.session.commit()
    my_posts = Post.query.all()
    comments = Comment.query.all()
    return render_template('my_posts.html', posts=my_posts, comments=comments)


@app.route('/delete_post', methods = ['GET'])
def delete_post():
    post_id = request.args.get('post_id')
    if post_id is not None:
        my_post = Post.query.filter_by(id=post_id).first()

        db.session.delete(my_post)
        db.session.commit()
    return "<h2>Deleted post with id "+post_id+"</h2><br /><a href=\"/my_posts\">go back</a>"


@app.route('/edit_post', methods = ['GET'])
def edit_post():
    post_id = request.args.get('post_id')

    my_post = Post.query.filter_by(id=post_id).first()
    return render_template('edit_post.html', title=my_post.title, text=my_post.text, post_id=post_id)


@app.route('/edited_post_submit', methods = ['POST'])
def edited_post_submit():
    my_request = request.form
    post_id = my_request.get('post_id')
    my_post = Post.query.filter_by(id=post_id).first()
    my_post.title = my_request.get('title')
    my_post.text = my_request.get('text')
    db.session.commit()
    return "<h2>Post successfully updated!</h2><br /><a href=\"/my_posts\">go back</a>"


@app.route('/sign_up', methods = ['POST', 'GET'])
def sign_up():
    a = request.form
    if 'firstname' in a and 'lastname' in a and 'email' in a and 'password' in a and 'birthday' in a:
        first_name = a['firstname']
        last_name = a['lastname']
        email = a['email']
        password = a['password']
        date_of_birth = a['birthday']
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, date_of_birth=date_of_birth)
        db.session.add(new_user)
        db.session.commit()
        return render_template('sign_up_success.html')
    return render_template('sign_up.html')


@app.route('/sign_in', methods = ['POST', 'GET'])
def sign_in():
    error = None

    if request.method == 'POST':
        a = request.form
        user_email = a['email']
        user = User.query.filter_by(email=user_email).first()
        if user.password != a['password']:
            error = 'Invalid credentials.Please try again'
        else:
            login_user(user)
            return redirect('http://127.0.0.1:5000/')
    return render_template('sign_in.html', error=error)


@app.route('/sign_out')
def sign_out():
    logout_user()
    return redirect('http://127.0.0.1:5000/')


@app.route('/comment_submit', methods = ['POST'])
def comment_submit():
    print('entered')
    a = request.form
    if 'comment' in a:
        comment = a['comment']
        post_id = a['post_id']
        author = current_user.first_name + " " + current_user.last_name
        print(comment, post_id)
        new_comment = Comment(text=comment, author=author, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect('http://127.0.0.1:5000/my_posts')


if __name__ == '__main__':
    #db.create_all()
    #User.__table__.drop(db.engine)
    #Comment.__table__.drop(db.engine)
    app.run()