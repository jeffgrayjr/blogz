from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gx57lPD6X62rqNL'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    date_of_pub = db.Column(db.DateTime)
    

    def __init__(self, title, content, date_of_pub):
        self.title = title
        self.content = content
        self.date_of_pub = date_of_pub
        



@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args:
        post_id = request.args.get('id')
        single_post = Post.query.filter_by(id = post_id).first()
        posts = [single_post]
    else:
        posts = Post.query.all()
    
    return render_template('blog.html', title="Build-A-Blog!", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def add_entry():
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
            new_entry = Post(blog_title,blog_content, blog_post_date)
            db.session.add(new_entry)
            db.session.commit()
            blog_id =  Post.query.filter_by(title = blog_title).first().id
            return redirect('./blog?id=' + str(blog_id)) 
        else:
            return render_template('add_entry.html', title="Add a post", 
        blog_title=blog_title, title_error=title_error,
        blog_content=blog_content, entry_error=entry_error)
    
    return render_template('add_entry.html', title="Add a post!")

if __name__ == '__main__':
    app.run()