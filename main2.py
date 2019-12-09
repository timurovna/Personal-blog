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


class Post(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    heading = db.Column(db.String(80), unique=False, nullable=False)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    author = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(100), default=datetime.now())
    user_id = db.Column(db.Integer, unique=False, nullable=False)

    def get_comments(self):
        return Comment.query.filter_by(post_id=self.id).all()


class Comment(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    author = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(100), default=datetime.now())
    post_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, unique=False, nullable=False)


@app.route('/')
def heading():
    return render_template('index.html')


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/sign_up_submit', methods=['POST'])
def sign_up_submit():
    form = request.form
    if 'first_name' in form and 'last_name' in form and 'email' in form and 'password' in form and 'date_of_birth' in form:
        first_name = form['first_name']
        last_name = form['last_name']
        email = form['email']
        password = form['password']
        date_of_birth = form['date_of_birth']
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, date_of_birth=date_of_birth)
        db.session.add(new_user)
        db.session.commit()
        return render_template('sign_up_success.html')


@app.route('/sign_in', methods=['GET'])
def sign_in():
    return render_template('sign_in.html')


@app.route('/sign_in_success', methods=['POST'])
def sign_in_success():
    form = request.form
    email = form['email']
    user = User.query.filter_by(email=email).first()
    if user.password == form['password']:
        login_user(user)
        return redirect('http://127.0.0.1:5000')
    else:
        error = 'Invalid credentials. Please try again'
        return render_template('sign_in.html', error=error)


@app.route('/sign_out', methods = ['GET'])
def sign_out():
    logout_user()
    return redirect('http://127.0.0.1:5000/')


@app.route('/my_posts', methods = ['GET'])
def my_posts():
    posts = Post.query.all()
    comments = Comment.query.all()
    return render_template('my_posts.html', posts=posts, comments=comments)


@app.route('/post_submit', methods = ['POST'])
def post_submit():
    form = request.form
    if 'heading' in form and 'text' in form and current_user.is_authenticated:
        heading = form['heading']
        text = form['text']
        author = current_user.first_name + " " + current_user.last_name
        post = Post(text=text, heading=heading, author=author, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
    return redirect('http://127.0.0.1:5000/my_posts')


@app.route('/delete_post', methods = ['GET'])
def delete_post():
    post_id = request.args.get('post_id')
    post = Post.query.filter_by(id=post_id).first()
    for c in comments:
        db.session.delete(c)
    db.session.delete(post)
    db.session.commit()
    return redirect('http://127.0.0.1:5000/my_posts')


@app.route('/edit_post', methods = ['GET'])
def edit_post():
    post_id = request.args.get('post_id')
    post_to_edit = Post.query.filter_by(id=post_id).first()
    heading = post_to_edit.heading
    text = post_to_edit.text
    return render_template('edit_post.html', heading=heading, text=text, post_id=post_id)


@app.route('/edited_post_submit', methods = ['POST'])
def edited_post_submit():
    form = request.form
    print(form)
    post_id = form['post_id']
    post = Post.query.filter_by(id=post_id).first()
    post.heading = form['heading']
    post.text = form['text']
    db.session.commit()
    return "<h2>Post successfully updated!</h2><br /><a href=\"/my_posts\">go back</a>"


@app.route('/comment_submit', methods = ['POST'])
def comment_submit():
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


@app.route('/comment_delete', methods = ['GET'])
def comment_delete():
    comment_id = request.args.get('comment_id')
    comment_to_delete = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect('http://127.0.0.1:5000/my_posts')


@app.route('/comment_edit', methods = ['GET'])
def comment_edit():
    comment_id = request.args.get('comment_id')
    comment_to_edit = Comment.query.filter_by(id=comment_id).first()
    text = comment_to_edit.text
    return render_template('comment_edit.html', text=text, comment_id=comment_id)


@app.route('/edited_comment_submit', methods = ['POST'])
def edited_comment_submit():
    a = request.form
    print(a)
    comment_id = a['comment_id']
    comment = Comment.query.filter_by(id=comment_id).first()
    comment.text = a['comment']
    db.session.commit()
    return "<h2>Your comment successfully updated!</h2><br /><a href=\"/my_posts\">go back</a>"



if __name__ == '__main__':
    db.create_all()
    #Post.__table__.drop(db.engine)
    #Comment.__table__.drop(db.engine)
    app.run()
