import os
from flask import Flask, request ,jsonify, redirect, make_response, url_for, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from app.config import Config
from app.utils import *


app=Flask(__name__, static_url_path='', static_folder='converted')
app.config.from_object(Config)
cors = CORS(app)
port = int(os.environ.get("PORT", 5000))



@app.route('/converted/<file>', methods=['GET'])
def serve_file(file):
    return send_from_directory('converted', file)


@app.route('/', methods=['GET'])
def index():
    return redirect('/mongconverter/api/v1')


@app.route('/mongconverter/api/v1', methods=['GET'])
def send_formats():
    return jsonify({"media": {"audio" : ['mp3', 'aac', 'ogg', 'wav'], "video":['mp4', 'mkv', 'avi', 'ts']}})


@app.route('/mongconverter/api/v1/<media>', methods=['POST'])
def receive_files(media):
    format = request.args.get('format')
    data = request.files.get('file')
    filename = secure_filename(data.filename)
    if filename and f'.{filename.split(".")[-1]}' in app.config["UPLOAD_EXTENSIONS"]:
        data.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        if (data.content_type.split('/')[0] == 'audio' or data.content_type.split('/')[0] == 'video') and media == 'audio' :
            responds = mediaconverter(filename, format)
            if responds:
                return make_response(jsonify({"status": 200, "response": f'{url_for("serve_file", file=f"{responds}")}'}))
            else:
                return make_response(jsonify({"status": 502, "response": "file couldn't be processed"}))
        if data.content_type.split('/')[0] == 'video' and media == 'video':
            responds = mediaconverter(filename, format, True)
            pass
    return make_response(jsonify({"status": 403, "response": "file format not supported"}))


