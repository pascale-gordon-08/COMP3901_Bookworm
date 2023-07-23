import os, nltk, PyPDF2, time, math, re, string, openai, requests

from . import db, login_manager
from app import app, bm25
from .bm25 import (extract_text_from_pdf,ask_model,preprocess_sentences,preprocess_query,calculate_bm25_score, query)
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
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


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

"""Query Processing setup"""
def remove_stopwords(query):
    
    stopwords_list = stopwords.words('english')
    tokens = nltk.word_tokenize(query)
    filtered_tokens = [token for token in tokens if token.lower() not in stopwords_list]
    filtered_q = ', '.join(filtered_tokens)
    return filtered_q


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
        pdf.save(os.path.join(Config.UPLOAD_FOLDER, pdfname))
        pdfupload = PDF_file(pdfname)
        db.session.add(pdfupload)
        db.session.commit()
    
       
    return render_template('upload.html', form = form)


@app.route('/library')
def library():
    allPDF = db.session.execute(db.select(PDF_file)).scalars()
    pdfs = []
    for files in allPDF:
        pdfs.append(files.filename)
    
    return render_template('library.html', pdfs=pdfs)   


@app.route('/take_quiz')
def take_quiz():
    return render_template('quiz.html')



@app.route('/chat', methods=['GET','POST'])
def chat():  
    form = ChatForm()
    if form.validate_on_submit():
        
        query = form.messages.data
        answer = ask_model(query)
        
        return render_template('chat.html', form=form, answer = answer, query = query)
    # chathtml = render_template('container.html', messages = chat_messages)
    # if request.is_json:  
    #     return jsonify(html=chathtml)  # Return the updated chat container as JSON

    return render_template('chat.html', form=form)

"""@app.route('/prompts', methods=['POST'])
def messages():
    chathtml = render_template('container.html', messages = chat_messages)
    if request.is_json:  
        return jsonify(html=chathtml)  # Return the updated chat container as JSON"""
    


"""# @app.route('/extract', methods=['POST'])
# def extract_text():
#     pdf_path = request.json['pdf_path']
#     start_page = request.json['start_page']
#     text_list = extract_text_from_pdf(pdf_path, start_page)
#     return jsonify(text_list)

# @app.route('/ask', methods=['POST'])
# def ask_question():
#     form = ChatForm()
    
#     queries = request.json[form.messages.data]
#     page = request.json['page']
#     answer = ask_model(queries, page)
#     return jsonify(answer)

# @app.route('/preprocess', methods=['POST'])
# def preprocess_sentences_endpoint():
#     sentences = request.json['sentences']
#     preprocessed = preprocess_sentences(sentences)
#     return jsonify(preprocessed)

# @app.route('/preprocess_query', methods=['POST'])
# def preprocess_query_endpoint():
#     question = request.json['question']
#     preprocessed = preprocess_query(question)
#     return jsonify(preprocessed)

# @app.route('/calculate_score', methods=['POST'])
# def calculate_bm25_score_endpoint():
#     page_terms = request.json['page_terms']
#     query_terms = request.json['query_terms']
#     page_length = request.json['page_length']
#     avg_page_length = request.json['avg_page_length']
#     total_pages = request.json['total_pages']
#     term_idf = request.json['term_idf']
#     score = calculate_bm25_score(page_terms, query_terms, page_length, avg_page_length, total_pages, term_idf)
#     return jsonify(score)"""




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
"""
# BASE_URL = 'http://127.0.0.1:8080'
# def test_extract():
#     endpoint = '/extract'
#     url = BASE_URL + endpoint
#     data = {
#         "pdf_path": "../test.pdf",
#         "start_page": 0
#     }
#     response = requests.post(url, json=data)
#     print("Extracted text:")
#     print(response.json())

# # Test the /ask endpoint
# def test_ask(query):
#     endpoint = '/ask'
#     url = BASE_URL + endpoint
#     data = {
#         "query": query,
        
#     }
#     response = requests.post(url, json=data)
#     return response.json()


# Test the other endpoints similarly...
"""