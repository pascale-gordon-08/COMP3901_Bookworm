from calendar import c
from . import db
from datetime import datetime
from sqlalchemy.sql import func
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    uid=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(255))
    lname=db.Column(db.String(255))
    email=db.Column(db.String(255), unique=True, nullable=False)
    password=db.Column(db.String, nullable=False)
    con = db.relationship('Conversation', backref='User')
    qr= db.relationship('Quiz', backref='User')
    


    def __init__(self,fname,lname,email,password):
        self.fname=fname
        self.lname=lname
        self.email=email
        self.password=password

    def get_id(self):
        return self.uid

    def __repr__(self):
        return '<User %r>' % (self.uid)
    

class PDF_file(db.Model):
    __tablename__= 'PDF_file'
    pid=db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(255))
    pcon = db.relationship('Conversation', backref='PDF_file')

    def __init__(self,filename):
        self.filename=filename


    def __repr__(self):
        return '<PDF_file %r>' % (self.filename)


class Conversation(db.Model):
    __tablename__= 'Conversation'

    cid=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey(User.uid)) 
    pid=db.Column(db.Integer, db.ForeignKey(PDF_file.pid))
    date=db.Column(db.DateTime(),default=func.now())
    question=db.Column(db.String(255))
    answer=db.Column(db.Text)
    

    def __init__(self,user_id,pid,date,question,answer):
        self.user_id=user_id 
        self.pid= pid
        self.date= date
        self.question= question
        self.answer= answer

    def __repr__(self):
        return '<Conversation %r>' % (self.user_id)



class Quiz(db.Model):
    __tablename__= 'Quiz'
    quiz_id=db.Column(db.Integer, primary_key=True)
    uid=db.Column(db.Integer,db.ForeignKey(User.uid))
    subject=db.Column(db.String(255))
    quiz_question=db.Column(db.String(255))
    quiz_answer=db.Column(db.String(255))
    opt1=db.Column(db.String(255))
    opt2=db.Column(db.String(255))
    opt3=db.Column(db.String(255))
    opt4=db.Column(db.String(255))
    score=db.Column(db.Integer)

    def __init__(self,uid,subject,quiz_question,quiz_answer,opt1,opt2,opt3,opt4,score):
        self.uid=uid
        self.subject=subject
        self.quiz_question=quiz_question
        self.quiz_answer=quiz_answer
        self.opt1=opt1
        self.opt2=opt2
        self.opt3=opt3
        self.opt4=opt4
        self.score=score

    def __repr__(self):
        return '<Quiz %r>' % (self.subject)
