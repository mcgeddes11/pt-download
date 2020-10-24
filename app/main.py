#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file, redirect, url_for
from pytube import YouTube
from urllib.parse import urlparse
from wtforms import StringField
from wtforms.validators import URL
from io import BytesIO
import time

DEVELOPMENT_ENV = True

app = Flask(__name__)

app_data = {
    "name":         "Pytube Downloader",
    "description":  "A basic Flask app using bootstrap for layout",
    "author":       "Jon Cocks",
    "html_title":   "Pytube Downloader",
    "project_name": "Pytube Downloader",
    "keywords":     "flask, webapp, template, basic",
    "failure_message": ""
}


@app.route('/')
def index():
    return render_template('index.html', app_data=app_data)

@app.route("/download_failure")
def download_failure():
    return render_template('failure.html', app_data=app_data, message="failed, idk?")

@app.route('/download_resource', methods=['POST'])
def download_resource():
    url = request.form['yt_url']
    # Validate URL
    url_is_valid = validate_url(url)
    # Return with message if invalid
    if not url_is_valid:
        app_data["failure_message"] = "Invalid Youtube URL"
        return redirect(url_for('download_failure'))

    output_type = request.form["output_type"]
    print(url)
    print(output_type)
    response = get_resource_to_buffer(url, output_type)
    if response["stream"] is None:
        # Redirect to index page
        print("Get failed, maybe retry?")
        app_data["failure_message"] = response["message"]
        return redirect(url_for('download_failure'))
    else:
        # Send the file
        print("Get succeeded! enjoy your download")
        return send_file(
            response["stream"],
            as_attachment=True,
            attachment_filename=response["filename"],
            mimetype='video/mp4'
        )

def validate_url(url):
    urlparts = urlparse(url)
    tf = urlparts.scheme == "https" and urlparts.netloc in ["youtube.com","www.youtube.com"]
    return tf

def get_resource_to_buffer(url, file_type):
    # TODO: proper error checking
    RETRY_COUNT = 5
    buffer = BytesIO()
    # This is finnicky, try a few times
    retries = 0
    mov = None
    while mov is None and retries < RETRY_COUNT:
        try:
            mov = YouTube(url)
        except Exception as e:
            retries += 1
            time.sleep(1)
            if retries >= RETRY_COUNT:
                return {"stream": None, "filename": None, "message": "Retry count exceeded, maybe retry?"}
    if file_type == "video":
        stream = mov.streams.get_highest_resolution()
    else:
        stream = mov.streams.get_audio_only()
    stream.stream_to_buffer(buffer)
    buffer.seek(0)

    return {"stream": buffer, "filename": stream.default_filename ,"message": "success"}

if __name__ == '__main__':
    app.run(debug=True, use_debugger=True, use_reloader=True, passthrough_errors=True)
    # app.run(host='0.0.0.0', debug=True, port=80)