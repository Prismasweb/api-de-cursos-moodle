from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case, func
from models import User, Course, UserEnrolment, Enrol, GradeItem, GradeGrade
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://moodle_pruebas:pDHiRArZ56M3Zj74@74.208.40.186:3306/moodle_pruebas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/courses/<username>', methods=['GET'])
def get_courses(username):
    subquery = db.session.query(
        GradeGrade.finalgrade.label('coursefinalgrade'),
        GradeItem.courseid.label('courseid'),
        GradeGrade.userid.label('userid')
    ).join(GradeItem, GradeGrade.itemid == GradeItem.id).filter(
        GradeGrade.userid == User.id,
        GradeItem.courseid == Course.id
    ).subquery()

    results = db.session.query(
        User.id.label('userid'),
        func.concat(User.firstname, ' ', User.lastname).label('fullname'),
        User.username,
        User.email,
        Course.id.label('courseid'),
        Course.fullname.label('coursename'),
        func.coalesce(GradeItem.itemname, 'No hay tareas calificadas').label('itemname'),
        case(
            (GradeGrade.aggregationweight == 0, 'no tiene calificación'),
            else_=func.coalesce(GradeGrade.finalgrade, 'Sin calificación')
        ).label('finalgrade'),
        subquery.c.coursefinalgrade
    ).join(UserEnrolment, User.id == UserEnrolment.userid)\
     .join(Enrol, UserEnrolment.enrolid == Enrol.id)\
     .join(Course, Enrol.courseid == Course.id)\
     .outerjoin(GradeItem, (GradeItem.courseid == Course.id) & (GradeItem.hidden == 0))\
     .outerjoin(GradeGrade, (GradeGrade.itemid == GradeItem.id) & (GradeGrade.userid == User.id))\
     .outerjoin(subquery, (subquery.c.courseid == Course.id) & (subquery.c.userid == User.id))\
     .filter(User.username == username)\
     .filter(~db.session.query(
         User.id
     ).join(UserEnrolment, User.id == UserEnrolment.userid)
       .join(Enrol, UserEnrolment.enrolid == Enrol.id)
       .join(Course, Enrol.courseid == Course.id)
       .join(GradeItem, (GradeItem.courseid == Course.id) & (GradeItem.hidden == 0))
       .join(GradeGrade, (GradeGrade.itemid == GradeItem.id) & (GradeGrade.userid == User.id))
       .filter(User.id == 3)
       .filter(Course.id == Course.id)
       .exists()
     ).order_by(Course.fullname, GradeItem.itemname).all()

    courses = {}
    for row in results:
        row = dict(row._mapping)
        courseid = row['courseid']
        if courseid not in courses:
            courses[courseid] = {
                'courseid': courseid,
                'coursename': row['coursename'],
                'coursefinalgrade': row['coursefinalgrade'],
                'items': {}
            }
        item_key = f"{row['itemname']}_{row['finalgrade']}"
        if item_key not in courses[courseid]['items']:
            courses[courseid]['items'][item_key] = {
                'itemname': row['itemname'],
                'finalgrade': row['finalgrade'],
                'count': 1
            } 
        else:
            courses[courseid]['items'][item_key]['count'] += 1

    # Formatear los ítems para mostrar el conteo de repeticiones
    for course in courses.values():
        course['items'] = [
            {
                'itemname': f"{item['itemname']} ({item['count']} veces)",
                'finalgrade': item['finalgrade']
            } for item in course['items'].values()
        ]

    response = list(courses.values())
    
    return app.response_class(
        response=json.dumps(response, ensure_ascii=False),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True)
