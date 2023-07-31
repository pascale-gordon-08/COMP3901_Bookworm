import os, nltk, PyPDF2, time, math, re, string, openai, requests,datetime,language_tool_python
from . import db, login_manager
from sqlalchemy import func
from app import app
from .bm25 import (processing)
from .lstm import (lstm)
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from .forms import UploadForm, RegistrationForm, ChatForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .config import Config
from .models import PDF_file, User, Conversation, Quiz
from flask_dropzone import Dropzone
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from language_tool_python import LanguageTool


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


"""Dropzone configuration"""
app.config.update(DROPZONE_MAX_FILE_SIZE = 1024, DROPZONE_UPLOAD_MULTIPLE = False, DROPZONE_ENABLE_CSRF = True)
dropzone = Dropzone(app)


"""Login Manager"""
@login_manager.user_loader
def load_user(uid):    
    return User.query.get(int(uid))

###
# Routing for application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/upload', methods = ['POST', 'GET'])
@login_required
def upload():
    """Render the website's upload page."""    
    form = UploadForm()    
    if request.method == 'POST':
        pdf = request.files.get('file')
        pdfname = secure_filename(pdf.filename)
        pdf_path = os.path.join(Config.UPLOAD_FOLDER, pdfname)
        pdf.save(pdf_path)
        pdfupload = PDF_file(pdfname)
        db.session.add(pdfupload)
        db.session.commit()
        pdff = PDF_file.query.filter_by(filename=pdfname).first()
        
        pdfid = pdff.pid
        session['filename'] = pdfname
        session['upload_folder'] = Config.UPLOAD_FOLDER
        session['pdf_path'] = pdf_path      
        session['pid']=pdfid       
    return render_template('upload.html', form = form)


@app.route('/library')
@login_required
def library():
    allPDF = db.session.execute(db.select(PDF_file)).scalars()
    pdfs = []
    for files in allPDF:
        pdfs.append(files.filename)    
    return render_template('library.html', pdfs=pdfs)

  
@app.route('/fromlibrary/<librarypdf>', methods=['GET'])
def fromlibrary(librarypdf):
    pdfname = librarypdf
    pdf = PDF_file.query.filter_by(filename=pdfname).first()
    pdfid = pdf.pid
    session['filename'] = pdfname
    session['pid']=pdfid
    return redirect(url_for('bwc'))


@app.route('/take_quiz')
@login_required
def take_quiz():
    return render_template('quiz.html')


@app.route('/bookwormchat', methods=['GET','POST'])
@login_required
def bwc():
    form = ChatForm()
    filename = session.get('filename')
    suggestions = lstm(filename)
    user_id = session.get('uid')
    pdfhistory = (
        db.session.query(PDF_file.filename, PDF_file.pid)
        .join(Conversation, PDF_file.pid == Conversation.pid)
        .filter(Conversation.user_id == user_id)
        .group_by(PDF_file.pid)
        .all()
    )
    historynames = (
        db.session.query(PDF_file.filename, PDF_file.pid)
        .join(Conversation, PDF_file.pid == Conversation.pid)
        .filter(Conversation.user_id == user_id)
        .group_by(PDF_file.pid)
        .all()
    )    
    if request.method == 'POST' and form.validate_on_submit():
        query = form.messages.data
        answer = processing(query, filename)             
        return jsonify(answer = answer)    
    return render_template('chat.html', form = form, filename = filename, suggestions = suggestions, historynames = historynames)

@app.route('/bookwormchat/<int:pid>', methods=['GET','POST'])
@login_required
def bwch(pid):
    form = ChatForm()
    pdfname = PDF_file.query.filter_by(pid=pid).first()
    session['filename'] = pdfname.filename
    session['pid']=pid
    filename = session.get('filename')
    suggestions = lstm(filename)
    user_id = session.get('uid')    
    pdfhistory = (db.session.query(Conversation.question, Conversation.answer)
    .filter(Conversation.pid == pid, Conversation.user_id == user_id)
    .all()
    )
    historynames = (
        db.session.query(PDF_file.filename, PDF_file.pid)
        .join(Conversation, PDF_file.pid == Conversation.pid)
        .filter(Conversation.user_id == user_id)
        .group_by(PDF_file.pid)
        .all()
    )
    if request.method == 'POST' and form.validate_on_submit():
        query = form.messages.data
        answer = processing(query, filename)             
        return jsonify(answer = answer)    
    return render_template('chat.html', form = form, filename = filename, suggestions = suggestions, pdfhistory = pdfhistory, historynames = historynames)


@app.route('/chat', methods=['GET','POST'])
@login_required
def chat():
    form = ChatForm()
    filename = session.get('filename')    
    if form.validate_on_submit:
        query = form.messages.data
        answer = processing(query, filename)
        date = datetime.date.today()
        conversation_upload = Conversation(session.get('uid'), session.get('pid'), date, query, answer)
        db.session.add(conversation_upload)
        db.session.commit()
        return jsonify(answer = answer)
    return jsonify(errors=form.errors)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        password = generate_password_hash(form.password.data ,method='sha256')
        newuser = User(fname, lname, email, password)
        uemail = User.query.filter_by(email=form.email.data).first()
        if uemail:
            flash('Email already exists', 'danger')
        else:
            db.session.add(newuser)
            db.session.commit()
            flash('Successfully Registered. Now you may Log In!', 'success')            
            return redirect(url_for('signin'))
    else:
        flash_errors(form)        
    return render_template('signup.html', form = form)


@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                userid = user.uid
                session['uid']=userid
                flash('Logged in Successfully', 'success')
                return redirect(url_for('upload'))
            flash("Invalid email or password!!", 'danger')
    return render_template('signin.html', form = form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('home'))


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')