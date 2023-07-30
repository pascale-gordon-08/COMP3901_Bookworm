import tensorflow as tf

from keras.models import load_model
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import numpy as np
import random
import PyPDF2
import re

model=load_model("app/lstm_model4.h5")

def lstm(name):
  fp='./uploads/'+name
  def extract_preprocess_lines(filepath):
    text_lines=[]
    with open(filepath,'rb') as pdf_flie:
        pdf_reader= PyPDF2.PdfReader(filepath)

        for page_num in range(len(pdf_reader.pages)):
          page = pdf_reader.pages[page_num]
          page_text = page.extract_text()

          text_lines.extend(page_text.splitlines())
        text_result= [''.join(c for c in s if c.isalpha() or c.isspace()) for s in text_lines]
        text_result= [s.strip() for s in text_result if s.strip()]
        return text_result[:100]




  def make_prediction(lst,model):
    #Tokenize the text
    tokenizer=Tokenizer()
    tokenizer.fit_on_texts(lst)
    sequences= tokenizer.texts_to_sequences(lst)

    #Pad sequences to be same length
    max_length=max(len(s) for s in sequences)
    padded_seq= pad_sequences(sequences,maxlen=50)

    predictions= model.predict(padded_seq)
    return predictions



  def generate_questions(text_list):
    question_template=["What is {text}?",
                    "Can you explain {text}?",
                    "Why is {text} important?",
                    "How does {text} work?",
                    ]
    questions=[]
    for t in text_list:
      qp= random.choice(question_template)
      question= qp.format(text=t)
      questions.append(question)
    return questions

  #Gets prediction from model and places headers into a list
  def headingsC(new_texts,predictions):
      result_lst=[]
      c=0
      for text, prediction in zip(new_texts, predictions):
          predicted_label = np.argmax(prediction)
          if predicted_label==1 and c<5:
              result_lst.append(text)
              c+=1
      quest=generate_questions(result_lst)
      return quest

  
  eg= extract_preprocess_lines(fp)
  p= make_prediction(eg,model)
  x= headingsC(eg,p)
  print(x)
  return x
    