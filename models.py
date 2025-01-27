from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'mdl_user'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    enrolments = db.relationship('UserEnrolment', backref='user')

class Course(db.Model):
    __tablename__ = 'mdl_course'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255))
    grade_items = db.relationship('GradeItem', backref='course')

class UserEnrolment(db.Model):
    __tablename__ = 'mdl_user_enrolments'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('mdl_user.id'))
    enrolid = db.Column(db.Integer, db.ForeignKey('mdl_enrol.id'))

class Enrol(db.Model):
    __tablename__ = 'mdl_enrol'
    id = db.Column(db.Integer, primary_key=True)
    courseid = db.Column(db.Integer, db.ForeignKey('mdl_course.id'))

class GradeItem(db.Model):
    __tablename__ = 'mdl_grade_items'
    id = db.Column(db.Integer, primary_key=True)
    courseid = db.Column(db.Integer, db.ForeignKey('mdl_course.id'))
    itemname = db.Column(db.String(255))
    hidden = db.Column(db.Integer)
    grades = db.relationship('GradeGrade', backref='grade_item')

class GradeGrade(db.Model):
    __tablename__ = 'mdl_grade_grades'
    id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.Integer, db.ForeignKey('mdl_grade_items.id'))
    userid = db.Column(db.Integer, db.ForeignKey('mdl_user.id'))
    finalgrade = db.Column(db.Float)
    aggregationweight = db.Column(db.Float)
