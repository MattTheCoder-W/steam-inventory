import os
from flask import Blueprint, render_template
from flask import flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from . import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

from .scraper import check_prices

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.split(".", 1)[-1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        session['filename'] = filename
        return redirect(url_for("main.scrape"))

@main.route("/scrape", methods=['GET', 'POST'])
def scrape():
    try:
        filename = session['filename']
    except KeyError:
        return f"No file was uploaded... <a href='{url_for('main.index')}'>Go back to main page</a>"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    result = check_prices(filepath)

    return result
