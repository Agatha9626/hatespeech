import re 
import tweepy 
import bcrypt
import datetime;
from tweepy import OAuthHandler 
from textblob import TextBlob 
from textblob.sentiments import NaiveBayesAnalyzer
from flask_mysqldb import MySQL,MySQLdb

from flask import Flask, render_template , redirect, url_for, request, redirect,session


def clean_tweet( tweet): 

        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 
         
def get_tweet_sentiment( tweet): 
        
        analysis = TextBlob(clean_tweet(tweet)) 
        if analysis.sentiment.polarity > 0:
            return "positive"
        elif analysis.sentiment.polarity == 0:
            return "neutral"
        else:
            return "negative"


def get_tweets(api, query, count=5): 
        
        count = int(count)
        tweets = [] 
        try: 
            
            fetched_tweets = tweepy.Cursor(api.search_tweets, q=query, lang ='en', tweet_mode='extended').items(count)
            
            for tweet in fetched_tweets: 
                
                parsed_tweet = {} 

                if 'retweeted_status' in dir(tweet):
                    parsed_tweet['text'] = tweet.retweeted_status.full_text
                else:
                    parsed_tweet['text'] = tweet.full_text

                parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text']) 

                if tweet.retweet_count > 0: 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
            return tweets 
        except tweepy.TweepyException as e: 
            print("Error : " + str(e)) 

app = Flask(__name__)
app.static_folder = 'static'

app.secret_key = "secretttt_keyyyy"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hatespeech detection'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
  return render_template("index.html")

@app.route('/register', methods=["GET","POST"])
def register():
     msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO account VALUES (NULL, %s, %s, %s)', (username, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
     elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
     return render_template('register.html', msg=msg)
    # if request.method == 'GET':
    #     return render_template ("register.html")
    # else: 
    #     firstname = request.form['firstname']
    #     lastname = request.form['lastname']
    #     email = request.form ['email']
    #     password = request.form ['password'].encode('utf-8')
    #     hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
    #     cur = mysql.connection.cursor()
    #     cur.execute("INSERT INTO users(firstname, lastname, email,password) VALUES (%s,%s,%s,%s)", (firstname,lastname,email,hash_password,))
    #     mysql.connection.commit()
    #     session['firstname'] = request.form['firstname']
    #     session['lastname'] = request.form['lastname']
    #     session['email'] = request.form['email']
    #     return render_template("register.html")

@app.route('/login', methods =['GET', 'POST'])
 
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM account WHERE username = %s AND password = %s', (username, password,))
        cursor.execute('SELECT * FROM account WHERE username = %s ', (username, ))
        # Fetch one record and return result
        account = cursor.fetchone()
        print(f"account {account}")
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            #  if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('index.html', msg=msg)
            
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

    
    # if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
    #     email = request.form['email']
    #     password = request.form['password'].encode('utf-8')
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute("SELECT * FROM users WHERE email = % s AND password = % s", (email, password, ))
    #     user = cursor.fetchone()
        
    #     if user:
    #         if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
    #             session['loggedin'] = True
    #             session['firstname'] = user['firstname']
    #             session['email'] = user['email']
    #             return 'Logged in successfully !'
    #             # return render_template('index.html', msg = msg)
    #     else:
    #         msg = 'Incorrect username / password !'
    # return render_template('index.html', msg = msg)
# @app.route('/login', methods=["GET", "POST"])

# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password'].encode('utf-8')


#         curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         curl.execute("SELECT * from users where email=%s",(email,))
#         user = curl.fetchone()
#         curl.close()

#         if len(user) > 0:
#             if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
#                 session['firstname'] = user['firstname']
#                 session['email'] = user['email']
#                 return render_template("index.html")
#             else:
#                 return "Error password and email do not match"
#         else:
#             return "Error user not found"
#     else:
#         return render_template("login.html")        

# ******Phrase level sentiment analysis
@app.route("/predict", methods=['POST','GET'])
def pred():
	if request.method=='POST':
            query=request.form['query'] #fetch values from input tag in index.html
            count=request.form['num']
            fetched_tweets = get_tweets(api,query, count) #gets query and count and get sentiments
            return render_template('result.html', result=fetched_tweets)

# fetched_tweets
# [
#   {"text" : "tweet1", "sentiment" : "sentiment1"},
#   {"text" : "tweet2", "sentiment" : "sentiment2"},
#   {"text" : "tweet3", "sentiment" : "sentiment3"}
# ]

#Sentence level sentiment analysis
@app.route("/predict1", methods=['POST','GET'])
def pred1():
    
	if request.method=='POST':
            text = request.form['txt']
            blob = TextBlob(text)
            if blob.sentiment.polarity > 0:
                text_sentiment = "positive"
            elif blob.sentiment.polarity == 0:
                text_sentiment = "neutral"
            else:
                text_sentiment = "negative"
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            tweet = text
            sentiment = text_sentiment
            ct = datetime.datetime.now()
            timestamp = ct
            user = 'agatha'

            cursor.execute('INSERT INTO tweets VALUES (NULL, %s, %s, %s, %s)', (tweet,sentiment,timestamp,user,))
            mysql.connection.commit()
        
            return render_template('result1.html',msg=text, result=text_sentiment)

      

        
    

@app.route("/predict2", methods=['POST','GET'])
def pred2():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method=='POST':
        global text
        text = request.form['txt']

        blob = TextBlob(text)
        if blob.sentiment.polarity > 0:
            text_sentiment = "positive"
        elif blob.sentiment.polarity == 0:
            text_sentiment = "neutral"
        else:
            text_sentiment = "negative"

            # Create variables for easy access
        tweet = request.form['tweet']
        sentiment = request.form['sentiment']
        timestamp = request.form['timestamp']
        user = request.form['user']

        # cursor.execute('INSERT INTO tweets VALUES (NULL, %s, %s, %s, %s)', (tweet,sentiment,timestamp,user,))
    return render_template('result1.html',msg=text, result=text_sentiment)



if __name__ == '__main__':
    # app.run(debug=True ,port=8080,use_reloader=False)
    
    consumer_key = 'VFfIhJ35F4NDehHHjeaOkmiTd' 
    consumer_secret = 'jJky5fF3neyyPF0B3GvwbtlCyiX2tR7rDHFzNLHH8QghaVUyKs'
    access_token = '1563263998002225152-NA3vB40Hec3ICxry5C6RaFoTkcCcHq'
    access_token_secret = 'JZKuBGE2uI5iiKd48xlRqgGkoC7G6l06RLlr35eONDV9x'

    try: 
        auth = OAuthHandler(consumer_key, consumer_secret)  
        auth.set_access_token(access_token, access_token_secret) 
        api = tweepy.API(auth)
    except: 
        print("Error: Authentication Failed") 

    app.debug=True
    app.run(host='localhost')
