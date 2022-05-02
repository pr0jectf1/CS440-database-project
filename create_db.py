import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="pass1234",
    database="users"
    )

my_cursor = mydb.cursor()


q1 = "CREATE DATABASE cs491"
q2 = "Create Table user(username VARCHAR(255) PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL)"

q3 = "CREATE TABLE Post(PostID INT PRIMARY KEY AUTO_INCREMENT, subject VARCHAR(255) NOT NULL, content VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, date_created DATETIME NOT NULL, FOREIGN KEY (author) REFERENCES User(username))"
q4 = "CREATE TABLE Tag (TagID INT PRIMARY KEY AUTO_INCREMENT, tag VARCHAR(255), PostID INT NOT NULL, FOREIGN KEY (PostID) REFERENCES Post(PostID))"

q5 = "CREATE TABLE Comment(id INT PRIMARY KEY AUTO_INCREMENT, text VARCHAR(255) NOT NULL, sentiment VARCHAR(8) NOT NULL, date_created DATETIME NOT NULL, author VARCHAR(255) NOT NULL, post_id INT NOT NULL, FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post(PostID))"
q6 = "CREATE TABLE RATING(id INT PRIMARY KEY AUTO_INCREMENT, date_created DATETIME NOT NULL, author VARCHAR(255) NOT NULL, post_id INT NOT NULL, vote VARCHAR(255), FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post(PostID))"
q7 = "CREATE TABLE Downvote(id INT PRIMARY KEY AUTO_INCREMENT, date_created DATETIME NOT NULL, author VARCHAR(255) NOT NULL, post_id INT NOT NULL, vote VARCHAR(255), FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post(PostID))"
q8 = "CREATE TABLE Follower(id INT PRIMARY KEY AUTO_INCREMENT, user_following VARCHAR(255) NOT NULL, followed_user VARCHAR(255) NOT NULL, FOREIGN KEY (followed_user) REFERENCES User(username))"
q9 = "CREATE TABLE Hobby(id int PRIMARY KEY AUTO_INCREMENT, user VARCHAR(255) NOT NULL, hobby VARCHAR(255) NOT NULL, FOREIGN KEY (user) REFERENCES User(username))"
# print(q2)

# my_cursor.execute(q9)

