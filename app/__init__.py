import os
from flask import Flask, request,jsonify, redirect, make_response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from app.config import Config



app=Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)
port = int(os.environ.get("PORT", 5000))


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
        pass
    return make_response(jsonify({"status": 200}))


