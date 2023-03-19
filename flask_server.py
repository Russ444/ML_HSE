import joblib
import os
import re
import threading
import nltk
from stop_words import get_stop_words
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

test_forest = joblib.load("./random_forest.joblib")
test_vectorizer = joblib.load("./vectorizer.joblib")
english_stopwords = set(get_stop_words('english'))
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'eml'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess(path):
    f = open(path, encoding = "ISO-8859-1")
    email = f.read()
    f.close()
    content = ''
    for l in email.split('\n'):
        if not l.startswith('From:') and not l.startswith('Subject:') and not l.startswith('To:') \
        and not l.startswith('Date:') and not l.startswith('X-'):
            content += l.strip()

    def is_english_word(word):
        synsets = wordnet.synsets(word)
        return len(synsets) > 0 and synsets[0].lemmas()[0].name() == word.lower()

    text = re.sub(r'[^a-zA-Z\s]', '', content)
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token not in english_stopwords]
    english_words = [token for token in filtered_tokens if is_english_word(token)]
    return ' '.join(english_words)

def predict(path):
    tranformed_text = test_vectorizer.transform([preprocess(path)]).toarray()
    return "Spam" if not test_forest.predict(tranformed_text) else "Ham"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f"RESULT : {predict(os.path.join(app.config['UPLOAD_FOLDER'], filename))}"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

threading.Thread(target=app.run, kwargs={'host':'0.0.0.0','port':8090}).start() 
