from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
# from werkzeug import
from datetime import datetime
from flask_mail import Mail
import json

with open("config.json", "r") as c:
    param = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'secret-key-doubtforum'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=param['gmail-user'],
    MAIL_PASSWORD=param['gmail-password']
)
mail = Mail(app)

local_server = True

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_uri']  # mysql://username:password@localhost/db_name
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['prod_uri']  # mysql://username:password@localhost/db_name
db = SQLAlchemy(app)


class Posts(db.Model):
    # sno,name,phone_no,msg,email,date

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tag_line = db.Column(db.String(15), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    img_file = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=False)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ph_no = db.Column(db.String(15), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=False)


@app.route('/admin', methods=["GET", "POST"])
def admin():
    if 'user' in session and session['user'] == param['name']:
        posts = Posts.query.all()
        return render_template('cp.html', param=param, posts=posts)

    if request.method == "POST":
        name = request.form.get('username')
        password = request.form.get('pass')
        if name == param['name'] and password == param['password']:
            session['user'] = name
            posts = Posts.query.all()
            return render_template('cp.html', param=param, posts=posts)

    return render_template('login.html', param=param)


@app.route('/about')
def about():
    return render_template('about.html', param=param)


@app.route('/questions')
def questions():
    return render_template('questions.html', param=param)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    return render_template('index.html', param=param, posts=posts)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    post_data = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', param=param, post=post_data)


@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):
    if 'user' in session and session['user'] == param['name']:
        del_post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(del_post)
        db.session.commit()
        return redirect('/admin')



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/admin')



@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == param['name']:
        if request.method == 'POST':

            new_title = request.form.get('title')
            new_tag_line = request.form.get('tag_line')
            new_slug = request.form.get('slug')
            new_content = request.form.get('content')
            new_img_file = request.form.get('img_file')
            new_date = datetime.now()

            if sno == '0':

                new_post = Posts(title=new_title, tag_line=new_tag_line, slug=new_slug, content=new_content,
                                 img_file=new_img_file, date=new_date)
                db.session.add(new_post)
                db.session.commit()

                return redirect('/edit/0')

            else:

                post = Posts.query.filter_by(sno=sno).first()

                post.title = new_title
                post.tag_line = new_tag_line
                post.slug = new_slug
                post.content = new_content
                post.img_file = new_img_file
                post.date = new_date
                db.session.commit()

                return redirect('/edit/' + sno)

        data = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', post=data, sno=sno, param=param)


@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        """add entry to the database"""
        name = request.form.get('name')
        email = request.form.get('email')  # also add name attribute to contact.html
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, ph_no=phone, msg=message, email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New Doubt Hub contact from ' + name,
                          sender=email,
                          recipients=[param['gmail-user']],
                          body=message + "\n" + phone
                          )

    return render_template('contact.html', param=param)


app.run(debug=True)
