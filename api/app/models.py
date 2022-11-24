from flask import session
from app import app, db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship



@login_manager.user_loader
def load_user(user_id):
   if session['type'] == 'Teacher':
      return Teacher.query.get(int(user_id))
   elif session['type'] == 'EduCenter':
      return Educenter.query.get(int(user_id))
   else:
      return None

class Teacher(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key = True)
   first_name = db.Column(db.String(50), nullable = False)
   last_name = db.Column(db.String(50), nullable = False)
   email = db.Column(db.String(120), nullable = False, unique = True)
   phone_number = db.Column(db.String(20), nullable = False)
   education = db.Column(db.String(200), nullable = True)
   experience = db.Column(db.Text, nullable = True)
   city = db.Column(db.String(80), nullable = True)
   format_ = db.Column(db.String(80), nullable = True)
   languages = db.Column(db.String(80), nullable = True)
   password = db.Column(db.String(80), nullable = False)
   type = db.Column(db.String(80), nullable = False, default = "teacher")

   def __repr__(self):
      return f"Teacher('{self.first_name}'),Teacher('{self.last_name}'), Teacher('{self.email}'),  Teacher('{self.phonr_number}'), Teacher('{self.city}')"


class Subject(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
   subject_name = db.Column(db.String(80), nullable = False)
   subject_price = db.Column(db.Integer, nullable = False)
   subject_description = db.Column(db.Text, nullable = False)
   teacher = relationship("Teacher",backref="subjects") 


class Educenter(db.Model, UserMixin):
   
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(50), nullable = False)
   email = db.Column(db.String(120), nullable = False, unique = True)
   phone_number = db.Column(db.String(20), nullable = False)
   description = db.Column(db.Text, nullable = True)
   address = db.Column(db.String(80), nullable = True)
   password = db.Column(db.String(80), nullable = False)
   type = db.Column(db.String(80), nullable = False, default = "edu_center")


class Courses(db.Model):   
   id = db.Column(db.Integer, primary_key = True)
   edu_center_id = db.Column(db.Integer, db.ForeignKey('educenter.id'))
   course_name = db.Column(db.String(80), nullable = False)
   course_price = db.Column(db.Integer, nullable = False)
   course_description = db.Column(db.Text, nullable = False)
   edu_center = relationship("Educenter",backref="courses") 
   eduteachers = relationship(
        'Eduteachers',
        back_populates='course',

        cascade='save-update, merge, delete'
    )


class Eduteachers(db.Model):   
   id = db.Column(db.Integer, primary_key = True)
   course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable = False)
   first_name = db.Column(db.String(80), nullable = False)
   last_name = db.Column(db.Integer, nullable = False)
   info = db.Column(db.Text, nullable = False)
   languages = db.Column(db.String(20), nullable = False)
   course = relationship("Courses",back_populates='eduteachers') 
   
with app.app_context():
    db.create_all()
