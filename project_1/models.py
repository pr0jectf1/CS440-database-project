from datetime import timezone
from email.policy import default
from enum import unique
from . import db
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import SelectField
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    username = db.Column(db.String, primary_key=True, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    followers = db.relationship('Follower', backref='user', passive_deletes=True)
    hobbies = db.relationship('Hobby', backref='user', passive_deletes=True)

    def get_id(self):
        return (self.username)
    

class Post(db.Model):
    PostID = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    tags = db.relationship('Tag', backref='post', passive_deletes=True)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    # ratings = db.relationship('Rating', backref='post', passive_deletes=True)
    # downvotes = db.relationship('Downvote', backref='post', passive_deletes=True)
    

class Tag(db.Model):
    TagID = db.Column(db.Integer, primary_key=True, nullable=False)
    tag = db.Column(db.String(255))
    PostID = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)
    sentiment = db.Column(db.String(8), nullable=False)

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_following = db.Column(db.String(255), nullable=False)
    followed_user = db.Column(db.String(255), db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)

class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(255), db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)
    activity = db.Column(db.String(255), nullable=False)


class Form(FlaskForm):
    sentiment = SelectField('sentiment', choices=[('like', 'Like'), ('dislike', 'Dislike')])
    passtime = SelectField('hobby', choices=[('hiking', 'hiking'), ('swimming', 'swimming'), ('calligraphy', 'calligraphy'), ('bowling', 'bowling'), ('movie', 'movie'), ('cooking', 'cooking'), ('dancing', 'dancing')])
