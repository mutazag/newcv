# https://code.visualstudio.com/docs/python/tutorial-flask

from flask import Flask, render_template
from flask import request, redirect
from flask import url_for, abort, send_from_directory
from flask_dropzone import Dropzone
from flask import session
# from flask_session import Session
import os
from settings import read_settings
from storage.client import listFiles, uploadFile, get_blobparts
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT')
BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY')
BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER')

SESSION_GUID = os.environ.get('SESSION_GUID', '1234')
# log env vars
logging.info(f'BLOB_ACCOUNT: {BLOB_ACCOUNT}')
logging.info(f'BLOB_STORAGE_KEY: {BLOB_STORAGE_KEY}')
logging.info(f'BLOB_CONTAINER: {BLOB_CONTAINER}')


app = Flask(__name__)
dropzone = Dropzone(app)

# configure app session
app.secret_key = SESSION_GUID
# clear session
# session.clear()
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)


@app.route('/')
def index():

    logging.info(f'session: {session}')

    user_session = session.get('userid', [])
    logging.info(f'user_session: {user_session}')
    if type(user_session) is not list:
        logging.info(f'user_session is not a list')
        user_session = []



    # append a guid to userid session
    from uuid import uuid4

    user_session.append(str(uuid4()))
    session['userid'] = user_session



    user_files = session.get('files', [])
    logging.info(f'files: {user_files}')
    if type(user_files) is not list:
        logging.info(f'user_files is not a list')
        user_files = []

    # return 'Hello, Flask!'
    return str(session['userid'])


@app.route('/settings', methods=['GET'])
def settings():
    settings = read_settings()

    return render_template('settings.html', data=settings)


@app.route('/files', methods=['GET'])
def files():

    user_files = session.get('files', [])
    logging.info(f'files: {user_files}')
    if type(user_files) is not list:
        logging.info(f'user_files is not a list')
        user_files = []

    files = listFiles(BLOB_ACCOUNT, BLOB_STORAGE_KEY, BLOB_CONTAINER, 'prefix', 'delimiter')
    return render_template('files.html', files=files)

@app.route('/cart', methods=['GET'])
def cart():
    files = session.get('files', [])
    logging.info(f'files: {files}')

    # {{file.blob_url}}?{{file.blob_sas}}">{{file.blob_name}}
    cart_files = [get_blobparts(f) for f in files]
    return render_template('cart.html', files=cart_files)


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    # clear files in session and refresh page to reload cart
    session['files'] = []
    render_template('cart.html', files=[])
    # return '', 204


@app.route('/cart/process', methods=['POST'])
def process_cart():
    selected_images = request.form.getlist('selected-images')
    logging.info(f'selected_images: {selected_images}')
    return '', 204

@app.route('/files', methods=['POST'])
def upload_file():
    # https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
    upload_file = request.files['file']
    filename = upload_file.filename
    # upload_file.stream
    logging.info(f'''Uploaded File: {type(upload_file)}\n
    Content Length: {upload_file.content_length}\n
    Content Type: {upload_file.content_type}\n
    Filename: {filename}''')

    uploaded_file_url = uploadFile(BLOB_ACCOUNT, BLOB_STORAGE_KEY, BLOB_CONTAINER, upload_file)
    logging.info(f'uploaded_file_url: {uploaded_file_url}')

    if 'files' not in session:
        session['files'] = []

    user_files = session.get('files', [])
    user_files.append(uploaded_file_url)
    session['files'] = user_files
    # log user_files
    logging.info(f'user_files: {user_files}')

    # return redirect(url_for('files'))
    return '', 204


if __name__ == '__main__':
    print('Starting Flask app', app.name)
    app.run()
