import time

#This is just for isolation from other modules. In a fully working system, just import normally
import imp
import json
from json2html import *
from flask_oauth import OAuth
from flask import Flask, redirect, url_for, session, request

app = Flask(__name__)

#Come up with a randomized, better secret key
SECRET_KEY = "Seanathons"

#Facebook authentication info
DEBUG = True
FACEBOOK_APP_ID = "616728231763788"
FACEBOOK_APP_SECRET = "15a5991c03b4bf0474df84376a53bda6"
PERMISSIONS = 'email, user_tagged_places, user_status, user_location,user_about_me,user_likes,user_photos,user_tagged_places,user_work_history,user_education_history,user_location'

#Simple opening page for using API Functions. I KNOW I should have used a template.
placeholder_index = """<a href='/login'><img src='http://i.stack.imgur.com/4iiKJ.png' />
Click here</a> or on the button for Facebook Login, <a href='/tokenme'>Here</a> to retrieve your token, and <a href='/getDetails/Rome'>Here</a> with some argument to use the Place API."""

#move over to __init__.py once conflicts have been resolved
app = glob.app
lqserv = imp.load_source("location_query_service","app/controllers/location_query_service.py")


app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': (PERMISSIONS)}
)


@app.route('/')
def index():
    return placeholder_index


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print "The token we got was %s" % (resp['access_token'])
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s, token = %s' % \
        (me.data['id'], me.data['name'], request.args.get('next'), resp['access_token'])


@app.route('/tokenme')
def tokenme():
	return str(session.get('oauth_token'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
	app.run(port=5000, debug=True, host='0.0.0.0') 
