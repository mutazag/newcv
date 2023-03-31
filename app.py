# https://code.visualstudio.com/docs/python/tutorial-flask

from flask import Flask, render_template
from flask import request, redirect
from flask import url_for, abort, send_from_directory
import os
from settings import read_settings
from storage.client import listFiles, uploadFile
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT')
BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY')
BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER')
#log env vars
logging.info(f'BLOB_ACCOUNT: {BLOB_ACCOUNT}')
logging.info(f'BLOB_STORAGE_KEY: {BLOB_STORAGE_KEY}')
logging.info(f'BLOB_CONTAINER: {BLOB_CONTAINER}')


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello, Flask!'


@app.route('/settings', methods=['GET'])
def settings():
    settings = read_settings()

    return render_template('settings.html', data=settings)


@app.route('/files', methods=['GET'])
def files():

    files = listFiles(BLOB_ACCOUNT, BLOB_STORAGE_KEY, BLOB_CONTAINER, 'prefix', 'delimiter')
    return render_template('files.html', files=files)


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

    uploadFile(BLOB_ACCOUNT, BLOB_STORAGE_KEY, BLOB_CONTAINER, upload_file)
    return redirect(url_for('files'))


if __name__ == '__main__':
    print('Starting Flask app', app.name)
    app.run()
