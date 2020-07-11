from __future__ import print_function
import os
from flask import Flask,session, url_for, render_template, request, redirect
from requests_oauthlib import OAuth2Session  
import os
import pickle
import json

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app_config = {
    'client_id': os.getenv("HUBSPOT_CLIENT_ID"),
    'client_secret': os.getenv("HUBSPOT_CLIENT_SECRET"),
    'scopes': os.getenv("HUBSPOT_SCOPES"),
    'auth_uri': os.getenv("HUBSPOT_AUTHORIZATION_URL"),
    'token_uri': os.getenv("HUBSPOT_TOKEN_URL"),
    "redirect_uri": os.getenv("HUBSPOT_REDIRECT_URI")
}
@app.route('/')
def home():
    #print(app_config)
    return render_template("index.html")

@app.route('/login')
def login():
    oauth = OAuth2Session(client_id=app_config['client_id'],scope=app_config['scopes'],redirect_uri='http://localhost:5000/authorized')
    auth_url, state = oauth.authorization_url(app_config['auth_uri'])
    app_config['state']=state
    #print("Authorization URL")
    #print(auth_url)
    return redirect(auth_url)

@app.route('/authorized')
def get_token():
    code = request.values.get("code")
    #print("Code : %s"%code)
    oauth = OAuth2Session(app_config["client_id"], state=app_config['state'])
    https_url = request.url
    i = request.url.find(":")
    https_request_url = https_url[:i] + "s" + https_url[i:]
    #print(https_url)
    #print(https_request_url)
    token = oauth.fetch_token(app_config['token_uri'],
    authorization_response=https_request_url,
    include_client_id=True,
    method="POST",
    client_secret=app_config['client_secret'],
    body=f"""grant_type=authorization_code&client_id={app_config["client_id"]}&client_secret={app_config["client_secret"]}&redirect_uri={app_config["redirect_uri"]}&code={code}""",
    )
    #print("Token is %s"%token)
    app_config['token']=token
    SaveTokenToFile(token)
    ShowContacts()
    return 'Authorization Complete. Please continue with Slack.'

@app.route('/refresh_token',methods=["GET"])
def get_refresh_token():
    oauth = OAuth2Session(app_config["client_id"], state=app_config['state'])
    new_token=oauth.refresh_token(app_config['token_uri'],
    body=f"""grant_type=refresh_token&client_id={app_config["client_id"]}&client_secret={app_config["client_secret"]}&refresh_token={app_config["token"].get('refresh_token')}""",
    )
    app_config["oauth_token"]=new_token
    #have stored in oauth_token instead of token to compare
    SaveTokenToFile(new_token)
    print()
    return "Token Refreshed sucessfully!!!"

def SaveTokenToFile(token):
    with open('hubspottoken.pickle', 'wb') as tokenfile:
        pickle.dump(token, tokenfile)

def ShowContacts():
    hubspot = OAuth2Session(
        app_config['client_id'], 
        token=app_config['token'], 
        auto_refresh_url=app_config['token_uri'],
        auto_refresh_kwargs=app_config, 
        token_updater=SaveTokenToFile
    )

    # Call the 'Get all contacts' API endpoint
    response = hubspot.get('https://api.hubapi.com/contacts/v1/lists/all/contacts/all',)
    print('-----------------------------------------')
    print(json.dumps(response.json(), indent=2, sort_keys=True))

if __name__ == '__main__':
    app.run(port=5000,debug=True)

