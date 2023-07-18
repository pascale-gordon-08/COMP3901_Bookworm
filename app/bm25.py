import openai, nltk
import PyPDF2
import math
import re
import string
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def extract_text_from_pdf(pdf_path):
    text_list = []
    start_page = 0
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Iterate through the pages, starting from the specified start_page
        for page_num in range(start_page, len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text().strip()
            text_list.append(text)

    return text_list

x= extract_text_from_pdf('/uploads/pdfcoffee.com_it-for-csec-pdf-free.pdf')

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


preprocessed_sentences = preprocess_sentences(x)
query="What are the advantages and disadvantages of information processing?"

def preprocess_query(question):
  stop_words = set(stopwords.words('english'))

  #question= ' '.join([word for word in nltk.word_tokenize(question) if word.lower() not in stop_words])
  #question= ' '.join([PorterStemmer().stem(word) for word in question])
  question=' '.join([PorterStemmer().stem(word.lower()) for word in nltk.word_tokenize(question) if word.lower() not in stopwords.words('english')])
  question = ' '.join([re.sub('[^a-zA-Z\s]', '', question)])

  return question.split()


query_terms= preprocess_query(query)

page_lengths=[len(terms) for terms in preprocessed_sentences]
avg_page_length= sum(page_lengths)/ len(page_lengths)

term_idf={}
total_pages=len(preprocessed_sentences)

for term in query_terms:
  #Calculate document frequency for the term - the number of pages containing the term
  df= sum(1 for terms in preprocessed_sentences if term in terms)
  #Calculate IDF using the document frequency
  idf= math.log((total_pages - df + 0.5) / (df + 0.5))
  term_idf[term]= idf


def calculate_bm25_score(page_terms, query_terms, page_length, avg_page_length, total_pages, term_idf, b=0.75, k1=1.2):
    score = 0

    for term in query_terms:
        if term in page_terms:
            tf = page_terms.count(term)  # Term frequency in the page
            idf = term_idf.get(term, 0)  # Inverse document frequency

            # BM25 formula
            score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + (b * page_length / avg_page_length))))

    return score


bm25_scores=[calculate_bm25_score(preprocessed_sentences[i],query_terms, page_lengths[i],avg_page_length,total_pages,term_idf)
  for i in range(total_pages)
            ]

ranked_pages = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)

ans_page=ranked_pages[0][0]
p= x[ans_page]
openai.api_key = "placeKeyhere"

def ask_model(query, page):
    prompt = page.join([
        "Answer the question base on the context\n\n"
        "Context:" + page + "\n\n"
        "Question:" + query + "\n\n"
        "Answer:"
    ])
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    answer = completion.choices[0].message.content.split(":")[-1].strip()
    return answer

answer= ask_model(query,p)