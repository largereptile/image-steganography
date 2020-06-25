import os
import random
import string

from flask import Flask, request, flash, jsonify, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from image_editor import ImageEditor

app = Flask(__name__)
CORS(app)  # oof ouch cant request media from myself without this

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = 'uploads/'
INVALID = {'url': "invalid"}


def random_string(string_length=8):
    """Generates a string of random characters for unique file names"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def allowed_file(file_ext):
    """Ensures file is an image"""
    return file_ext.strip(".") in ALLOWED_EXTENSIONS


def encode_to_file(old_filename, png_filename, message):
    """Use ImageEditor to write message to image and save locally"""
    img = ImageEditor(old_filename)
    img.encode(message)
    os.remove(old_filename)
    img.save_changes(filename=png_filename)


def decode_from_file(filename):
    img = ImageEditor(filename)
    msg = img.extract_message()
    return msg


@app.route('/steganography/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/steganography/encode', methods=['POST'])
def encode():
    if request.method == 'POST':  # no get requests here kiddo
        if 'file' not in request.files:  # ensures file is given
            flash('No file part')
            return jsonify(INVALID)
        message = request.form['message']  # TODO check message exists
        file = request.files['file']
        if file.filename == '':  # makes sure filename exists
            flash('No selected file')
            return jsonify(INVALID)

        file_ext = os.path.splitext(file.filename)[1]
        random_name = random_string(8)
        old_filename = f"{random_name}{file_ext}"  # preserving file extension, might not be necessary
        old_filename = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
        png_filename = f"{random_name}.png"
        png_filename = os.path.join(app.config['UPLOAD_FOLDER'], png_filename)

        if file and allowed_file(file_ext):
            file.save(old_filename)
            encode_to_file(old_filename, png_filename, message)
            filename = f"{random_name}.png"
            return jsonify({'url': f"https://harru.club:5000{url_for('uploaded_file', filename=filename)}"})

    return jsonify(INVALID)


@app.route('/steganography/decode', methods=['POST'])
def decode():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return jsonify(INVALID)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return jsonify(INVALID)

        file_ext = os.path.splitext(file.filename)[1]
        filename = secure_filename(f"{random_string(8)}{file_ext}")
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if file and allowed_file(file_ext):
            file.save(filename)
            message = decode_from_file(filename)
            return jsonify({'message': message})

        return jsonify(INVALID)


if __name__ == "__main__":
    # hmm maybe i should have removed these
    context = ("/etc/letsencrypt/live/harru.club/fullchain.pem", "/etc/letsencrypt/live/harru.club/privkey.pem")
    app.run(host='0.0.0.0', port=5000, ssl_context=context)


