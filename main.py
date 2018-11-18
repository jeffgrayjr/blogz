from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime, re


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gx57lPD6X62rqNL'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    date_of_pub = db.Column(db.DateTime)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, content, date_of_pub, poster):
        self.title = title
        self.content = content
        self.date_of_pub = date_of_pub
        self.poster = poster
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='poster')


    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'display_all', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email = email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        else:
            if user:
                flash("user password incorrect",'error')
            else:
                flash("username does not exist",'error')
            


    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    email_regex = '^(\w+(@){1}\w+(\.){1}\w+)$'
    

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user input
        if not email or not password or not verify:
            flash('All fields are required', 'error')
            return render_template('/signup.html')

        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('/signup.html')

        if len(password) < 3:
            flash('Password too short', 'error')
            return render_template('/signup.html')

        existing_user = User.query.filter_by(email = email).first()

        if not existing_user:
            if re.match(email_regex, email):
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
            else:
                flash('not a valid email address', 'error')
        else:
            #todo existing user message
            flash('username already exists', 'error')
            


    return render_template('/signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def display_all():

    posts = Post.query.join(User, Post.poster_id==User.id).add_columns(Post.id, Post.title, Post.content, Post.date_of_pub,User.email, User.id)

    if request.args:
        if request.args.get('id'):
            post_id = request.args.get('id')
            #posts = posts.query.filter_by(id = post_id).first()
            posts = posts.filter(Post.id == post_id)
        elif request.args.get('user'):
            post_owner = request.args.get('user')
            posts = posts.filter(Post.poster_id == post_owner)
    
    return render_template('blog.html', title="Build-A-Blog!", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def add_entry():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['blogtitle']
        blog_content = request.form['blogentry']
        blog_post_date = datetime.datetime.now()
        
        entry_error = ''
        title_error = ''

        if not blog_title:
            title_error = "Please enter a title for your post"
        if not blog_content:
            entry_error = "Please add some content to your post"
        
        if not title_error and not entry_error:
            new_entry = Post(blog_title,blog_content, blog_post_date, owner)
            db.session.add(new_entry)
            db.session.commit()
            blog_id =  Post.query.filter_by(title = blog_title).first().id
            return redirect('./blog?id=' + str(blog_id)) 
        else:
            return render_template('add_entry.html', title="Add a post", 
        blog_title=blog_title, title_error=title_error,
        blog_content=blog_content, entry_error=entry_error)
    
    return render_template('add_entry.html', title="Add a post!")

@app.route('/', methods=['POST', 'GET'])
def index():
    authors = User.query.all()
   # posts = Post.query.all()
    return render_template('index.html', title="Home", authors=authors)

if __name__ == '__main__':
    app.run()