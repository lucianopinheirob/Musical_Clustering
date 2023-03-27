from flask import Flask, request, redirect, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)

app.secret_key = "blablabla"
app.config['SESSION_COOKIE_NAME'] = 'Ls Cookie'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))


@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    saved_tracks = sp.current_user_saved_tracks(limit=50, offset=0)
    list_tracks = [saved_tracks['items'][i]['track']['name'] for i in range(50)]
    str_tracks = ""
    for track in list_tracks:
        str_tracks += f'{track} \n'
    return str_tracks

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="ebabc9cc8d824849a0ccda460050a82b",
        client_secret="848655af93d34806b1cc9ab1bf492763",
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-library-read",
    )



if __name__ == "__main__":
    app.run(debug=True)

