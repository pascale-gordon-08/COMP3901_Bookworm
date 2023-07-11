import os, nltk, PyPDF2, time,math, re, string
import math
from . import db, login_manager
from app import app
from flask import render_template, request, redirect, url_for, flash, send_file
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

"""PDF Processing"""
def extract_text_from_pdf(pdf_path, start_page):
    text_list = []

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Check if the start_page is within the valid range
        #if start_page < 0 or start_page >= reader.numPages:
            #raise ValueError('Invalid start_page value')

        # Iterate through the pages, starting from the specified start_page
        for page_num in range(start_page, len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text().strip()
            text_list.append(text)

    return text_list

def preprocess_sentences(sentences):
    # Remove punctuation
    sentences = [sentence.translate(str.maketrans('', '', string.punctuation)) for sentence in sentences]

    # Convert to lowercase
    sentences = [sentence.lower() for sentence in sentences]

    # Tokenize sentences into words
    #sentences = [word_tokenize(sentence) for sentence in sentences]
    sentences=[([PorterStemmer().stem(word) for word in nltk.word_tokenize(sentence)]) for sentence in sentences]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    sentences = [[word for word in sentence if word not in stop_words] for sentence in sentences]

    # Remove numbers and special characters
    sentences = [[re.sub('[^a-zA-Z]', '', word) for word in sentence] for sentence in sentences]

    # Remove empty strings
    sentences = [[word for word in sentence if word] for sentence in sentences]

    return sentences

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
    query = str(form.query.data)
    filtered_q = remove_stopwords(query)     
    return render_template('chat.html', form = form, filtered_q = filtered_q)


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
