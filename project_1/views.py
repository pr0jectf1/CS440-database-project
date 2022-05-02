
from unicodedata import category
import mysql.connector
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Post, Tag, User, Comment, Form, Follower, Hobby
from datetime import datetime, timedelta    

from flask_sqlalchemy import SQLAlchemy

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = Form()
    posts = Post.query.all()
    tags = Tag.query.all()
    
    return render_template("home.html", user=current_user, posts=posts, tags=tags, form=form)

@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method =='POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        tagString = request.form.get('tag')
        tags = tagString.split(", ")
        print(subject)
        print(content)
        print(tagString)
        print(tags)
        print(current_user)

        posts = Post.query.all()
        date = datetime.now()
        t = timedelta(days=1)
        count = 0

        #Check for all posts that were created by the current user less than 1 day ago.
        for post in posts:
            if (post.author == current_user.username):
                if (date - post.date_created) < t:
                    count = count + 1

        
        if not subject:
            flash('Subject cannot be empty', category='error')
        elif not content:
            flash('Content cannot be left empty', category='error')
        elif count > 2:
            flash('Can not make more than 2 posts per day.', category='error')
        else:
            
            if not tagString:
                post = Post(subject=subject, content=content, author=current_user.username)
                db.session.add(post)
                db.session.commit()
                flash('Post created', category='success')
                return redirect(url_for('views.home'))
            else:
                post = Post(subject=subject, content=content, author=current_user.username)
                db.session.add(post)
                db.session.commit()
                tags = tagString.split(", ")

                for tag in tags:
                    new_tag = Tag(tag=tag, PostID=post.PostID)
                    db.session.add(new_tag)
                    db.session.commit() 
                flash('Post created', category='success')   
                return redirect(url_for("views.home"))

    return render_template("create_post.html", user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(PostID=id).first()

    if not post:
        flash("Post does not exist.", category='error')
        
    elif current_user.username != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')

    return redirect(url_for('views.home'))

@views.route("/posts/<username>")
@login_required
def posts(username):
    form = Form()
    user = User.query.filter_by(username=username).all()

    if not user:
        flash('User does not exist.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=username).all()
    tags = Tag.query.all()
    return render_template("posts.html", user=current_user, posts=posts, username=username, tags=tags, form=form)

@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    form=Form()
    sentiment = form.sentiment.data
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(PostID=post_id)

        comments = Comment.query.filter_by(post_id=post_id)
        postCommentCount = 0
        for comment in comments:
            if current_user.username == comment.author:
                postCommentCount = postCommentCount + 1
        
        allComments = Comment.query.all()
        date = datetime.now()
        t = timedelta(days=1)
        totalCommentCount = 0

        #Check for all comments that were created by the current user less than 1 day ago.
        for comment in allComments:
            if (comment.author == current_user.username):
                if (date - comment.date_created) < t:
                    totalCommentCount = totalCommentCount + 1
        

        if postCommentCount > 0:
            flash('You cannot make more than 1 comment per post.', category='error')
        elif totalCommentCount > 2:
            flash('You can only make 3 comments per day.', category='error')
        elif post:
            comment = Comment(text=text, sentiment=sentiment, author=current_user.username, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')


    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist', category='error')
    elif current_user.username != comment.author and current_user.username != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/initialize-db', methods=['GET', 'POST'])
@login_required
def initDB():

    if request.method == 'POST':
        print("Testing passed")
        rejected = True
        response = ''

        try:
            
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="pass1234",
            database="users"
            )

            cursor = mydb.cursor()
           
            #sql will holde the sql statement
            sql = ''
            
            # waiting is if we are waiting to see a ';' to indicate the statement end.
            waiting = False
            for line in open('/Users/Luis Garcia/OneDrive/Desktop/cs491/project_1/sql/university.sql'):
                print("File was oppened")
                # Strip the line of the new line character, '\n'
                line = line.strip()

                # Is this just an empty line?
                if line == '':
                    # Yep, move on.
                    continue
                elif line[0] == '-' or line[0] == '/':
                    # We have a comment here, move on
                    continue
                elif line[len(line)-1] == ';' and waiting:
                    # We've been waiting for the end of statement character, ';'
                    # and now we've found it
                    waiting = False         # Set waiting to false
                    sql = sql + line        # Add the last line to the statement
                    print(sql)              # Output the statement to the terminal
                    cursor.execute(sql)     # Execute the statement
                    sql = ''                # Reset our sql variable
                    continue                # Move on with the for loop
                elif len(line) > 6:
                    # Is the length of the line > 6 (since we want to check up to index 5)?
                    if line[0] == 'C' and line[1] == 'R' and line[2] == 'E' and line[3] == 'A' and line[4] == 'T' and line[5] == 'E':
                        # Yep, did the first 5 char spell create? Yep!
                        # We're making a new table then
                        waiting = True      # Set waiting to true.
                        sql = sql + line    # Add the line to the sql variable
                        continue            # Move on with the for loop
                    elif waiting:
                        # The length is indeed longer, but we're not a create statement
                        # and we are waiting to be executed
                        sql = sql + line    # Add the line to the sql variable
                        continue            # Move on with the for loop
                    else:
                        # The length is indeed longer, but we're not waiting either
                        # Print and execute the command and continue on
                        print('Here')
                        print(line)
                        cursor.execute(line)
                        continue
                elif waiting:
                    # None of the above are true, but we're waiting
                    sql = sql + line        # Add the line to the sql variable
                    continue                # Move on with the for loop
                # Nothing above was true, and we're not waiting for an ';'
                # Print the command and execute it.
                print('Here')
                print(line)
                cursor.execute(line)
            # Create our response to the client and return it
            # message = {
            #     'status': 200,
            #     'message': 'Database successfully initialized!',
            # }
            # response = jsonify(message)
            # response.status_code = 200
            # return response
            flash('Database created', category='success')
        except Exception as e:
            # Was there some error in our code above?
            # Print it out to the terminal so we can try and debug it
            print(e)
        finally:
            if rejected == False:
                # If we've made it here, then we successfully executed out try
                # Now we can close our cursor and connection
                cursor.close()
                # conn.close()

    return render_template('initialize_db.html', user=current_user)


@views.route('/queries', methods=['GET'])
@login_required
def queries():
    
    return render_template('queries.html', user=current_user)

@views.route("/query1", methods=['GET', 'POST'])
@login_required
def query1():
    xtag = request.form.get('tag_x')
    ytag = request.form.get('tag_y')
    print(xtag)
    print(ytag)
    
    users = User.query.all()
    userList = []
    
    
    for user in users:
        # Check to see if a user has at least 2 posts
        if len(user.posts) > 1:
            
            x_check = False
            y_check = False

            for post in user.posts:
                
                for tag in post.tags:
                    # Verify the post has
                    if tag.tag == xtag:
                        x_check = True
                        break
                    elif tag.tag == ytag:
                        y_check = True
                    
                if x_check == True and y_check == True:
                    userList.append(user)
                    break

    return render_template('query1.html', user=current_user, users=users, x=xtag, y=ytag, userList=userList)

@views.route("/query2", methods=['GET', 'POST'])
@login_required
def query2():
    form = Form()
    user_x = request.form.get('user_x')
    if not user_x:
        flash('No user found with that username.', category='error')
        return redirect(url_for('views.queries'))
    
    positive_posts = []
    user_x = User.query.filter_by(username=user_x).first()
    for post in user_x.posts:
        if len(post.comments) > 0:
            dislike_count = 0
            for comment in post.comments:
                if comment.sentiment == 'dislike':
                    dislike_count = dislike_count+1
                    break
            if dislike_count == 0:
                print(post)
                positive_posts.append(post)
        
    return render_template('query2.html', user=current_user, user_x=user_x, positive_posts=positive_posts, form=form)

@views.route("/query3", methods=['GET'])
@login_required
def query3():
    users = User.query.all()
    userList = []
    highestCount = 1
    date = datetime(2022, 5, 1)
    print(date.strftime("%x"))

    for user in users:
        if len(user.posts) > 0:
            tempCount = 0
            for post in user.posts:
                if post.date_created.strftime("%x") == date.strftime("%x"):
                    tempCount = tempCount + 1
            if tempCount > highestCount:
                userList.clear()
                userList.append(user)
            elif tempCount == highestCount:
                userList.append(user)
    return render_template('query3.html', user=current_user, users=users, userList=userList)

@views.route("/query4", methods=['GET', 'POST'])
@login_required
def query4():
    user_x = request.form.get('user_x')
    user_y = request.form.get('user_y')

    print(user_x)
    print(user_y)

    users = User.query.all()
    userList = []

    for user in users:
        x_check = False
        y_check = False

        for follower in user.followers:
            if follower.user_following == user_x:
                print("x passed")
                x_check = True
            elif follower.user_following == user_y:
                print("y passed")
                y_check = True
            elif x_check == True and y_check == True:
                break
        if x_check == True and y_check == True:
            userList.append(user)
    return render_template('query4.html', user=current_user, userList=userList, user_x=user_x, user_y=user_y)

@views.route("/query5", methods=['GET'])
@login_required
def query5():
    
    users = User.query.all()

    userList = []

    for x in users:
        for y in users:
            if x.username != y.username:
                hobbyFound = False
                for x_hobby in x.hobbies:
                    for y_hobby in y.hobbies:
                        if x_hobby.activity == y_hobby.activity:
                            hobbyFound = True
                            break
                    
                    if hobbyFound == True:
                        break
                
                if hobbyFound == True:
                    pair = [x, y]
                    reversedPair = [y, x]
                    if reversedPair not in userList:
                        userList.append(pair)

    return render_template('query5.html', user=current_user, userList=userList)


@views.route("/query6", methods=['GET'])
@login_required
def query6():
    users = User.query.all()
    return render_template('query6.html', user=current_user, users=users)

@views.route("/query7", methods=['GET'])
@login_required
def query7():
    users = User.query.all()
    return render_template('query7.html', user=current_user, users=users)

@views.route("/query8", methods=['GET'])
@login_required
def query8():
    users = User.query.all()
    userList = []

    for user in users:
        if len(user.comments) > 0:
            likedComment = False
            for comment in user.comments:
                if comment.sentiment == 'like':
                    likedComment = True
                    break
            
            if likedComment == False:
                userList.append(user)
    return render_template('query8.html', user=current_user, userList=userList)

@views.route("/query9", methods=['GET'])
@login_required
def query9():
    users = User.query.all()
    userList = []

    for user in users:
        if len(user.posts) > 0:
            negativeComment = False

            for post in user.posts:
                
                for comment in post.comments:
                    if comment.sentiment == 'dislike':
                        negativeComment = True
                        break
                
                if negativeComment == True:
                    break
            
            if negativeComment == False:
                userList.append(user)
    return render_template('query9.html', user=current_user, users=users, userList=userList)

@views.route("/follow-user/<username>", methods=['GET'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    print(current_user.username)
    
    if len(user.followers) == 0:

        new_follower = Follower(user_following=current_user.username, followed_user=username)
        db.session.add(new_follower)
        db.session.commit()
        flash("Follow Successful")
    else:
        follow_check = False
        for follower in user.followers:
            print("here")
            if follower.user_following == current_user.username:
                follow_check = True
                flash("You already follow this person", category='error')
                break
        if follow_check == False:
            new_follower = Follower(user_following=current_user.username, followed_user=username)
            db.session.add(new_follower)
            db.session.commit()
            flash("Follow Successful")
    
    return redirect(url_for("views.home"))

@views.route('/hobbies', methods=['GET', 'POST'])
@login_required
def hobbyPage():
    form = Form()
    if request.method == 'POST':

        selectedHobby = form.passtime.data
        hobbyFound = False
        
        for hobby in current_user.hobbies:
            if hobby.activity == selectedHobby:
                hobbyFound = True
                flash('That is already one of your hobbies', category='error')
                break

        if hobbyFound == False:
            new_hobby = Hobby(owner=current_user.username, activity=selectedHobby)
            db.session.add(new_hobby)
            db.session.commit()
            flash('Hobby added!', category='success')

        return redirect(url_for('views.hobbyPage'))
    return render_template('hobbies.html', user=current_user, form=form)