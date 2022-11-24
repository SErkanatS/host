from flask import flash, redirect, render_template, session, url_for, request
from app.forms import LoginForm, TeacherRegistrationForm, SubjectForm, EduCenterRegistrationForm, CourseForm, EduTeacher
from app.models import Teacher, Subject, Educenter, Courses, Eduteachers
from app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required



sessiontype = 'Unauth'


@app.route('/')
def home():
    set_session()
    return render_template('home.html')




@app.route('/sign-in',  methods=['POST', 'GET'])
def sign_in():
    global sessiontype
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        teacher = Teacher.query.filter_by(email=form.email.data).first()
        edu_center = Educenter.query.filter_by(email=form.email.data).first()
        if teacher and bcrypt.check_password_hash(teacher.password, form.password.data):
            
            sessiontype = 'Teacher'
            login_user(teacher, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        elif edu_center and bcrypt.check_password_hash(edu_center.password, form.password.data):
            sessiontype = 'EduCenter'
            login_user(edu_center, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful! Please check the email and password!', 'danger')
    return render_template('sign-in.html', title='Sign-in', form=form)


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    teacher_form = TeacherRegistrationForm()
    if request.method == "POST":
        hashed_password = bcrypt.generate_password_hash(
            teacher_form.password.data).decode('utf-8')
        teacher = Teacher(
            first_name=teacher_form.first_name.data,
            last_name=teacher_form.last_name.data,
            phone_number=teacher_form.phone_number.data,
            email=teacher_form.email.data,
            password=hashed_password
        )
        db.session.add(teacher)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('sign_in'))

    return render_template('sign-up.html', title='Sign-up', teacher_form=teacher_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    if session['type'] == "Teacher":
        subjects = db.session.query(Subject).filter_by(
            teacher_id=current_user.id)
        return render_template('account.html', title='Account', subjects=subjects)
    elif session['type'] == 'EduCenter':
        courses = db.session.query(Courses).filter_by(edu_center_id = current_user.id)
        return render_template('account.html', title='Account', courses = courses)


@app.route("/account-update", methods=['POST', 'GET'])
@login_required
def account_update():
    if session['type'] == "Teacher":
      form = TeacherRegistrationForm()
      if request.method == "GET":
         form.email.data = current_user.email
         form.phone_number.data = current_user.phone_number
         form.city.data = current_user.city
         form.format_.data = current_user.format_
         form.languages.data = current_user.languages
         form.education.data = current_user.education
         form.experience.data = current_user.experience
         return render_template('account-update.html', title='Account', form=form)
      elif request.method == "POST":
         if form.validate_on_submit:
               current_user.email = form.email.data
               current_user.phone_number = form.phone_number.data
               current_user.city = form.city.data
               current_user.format_ = form.format_.data
               current_user.languages = form.languages.data
               current_user.education = form.education.data
               current_user.experience = form.experience.data
               db.session.commit()
               flash("Your account has been updated!", 'success')
               return redirect(url_for('account'))
    elif session['type'] == 'EduCenter':
      form = EduCenterRegistrationForm()
      if request.method == "GET":
         form.name.data = current_user.name
         form.email.data = current_user.email
         form.phone_number.data = current_user.phone_number
         form.address.data = current_user.address
         form.description.data = current_user.description
         return render_template('edu_account-update.html', title='Account', form=form)
      elif request.method == "POST":
         if form.validate_on_submit:
               current_user.name=form.name.data 
               current_user.email=form.email.data
               current_user.phone_number=form.phone_number.data 
               current_user.address=form.address.data 
               current_user.description=form.description.data 
               db.session.commit()
               flash("Your account has been updated!", 'success')
               return redirect(url_for('account'))


@app.route('/account/<id>/add_subject', methods=['GET', 'POST'])
def add_subject(id):
    teacher = Teacher.query.filter_by(id=id).first_or_404()
    form = SubjectForm()
    if request.method == "GET":
        return render_template('add_subject.html', form=form)
    else:
        if form.validate_on_submit:
            subject = Subject(teacher_id=teacher.id,
                              subject_name=form.subject_name.data,
                              subject_price=form.subject_price.data,
                              subject_description=form.subject_description.data)
            db.session.add(subject)
            db.session.commit()
            flash("New subject has been added!", 'success')
            return redirect(url_for('account'))




@app.route('/account/<id>/add_course', methods=['GET', 'POST'])
def add_course(id):
    edu_center = Educenter.query.filter_by(id=id).first_or_404()
    form = CourseForm()
    if request.method == "GET":
        return render_template('add_course.html', form=form)
    else:
        if form.validate_on_submit:
            course = Courses(edu_center_id=edu_center.id,
                              course_name=form.course_name.data,
                              course_price=form.course_price.data,
                              course_description=form.course_description.data)
            db.session.add(course)
            db.session.commit()
            flash("New course has been added!", 'success')
            course_cur_id =  course.id
            print(course_cur_id)
            return redirect(url_for('edu_teacher_modal', id = course.id))
        


@app.route('/edu_teacher_modal/<id>',  methods=['GET', 'POST'])
def edu_teacher_modal(id):
    course = Courses.query.filter_by(id=id).first_or_404()
    edu_teacher_form = EduTeacher()
    form = CourseForm()

    if request.method == "GET":
        print("kdkdkdkkdkdkd")
        return render_template('edu_teacher_modal.html', edu_teacher_form=edu_teacher_form, form=form)
    elif request.method == "POST":
            edu_teacher = Eduteachers(course_id=course.id,
                              first_name=edu_teacher_form.first_name.data,
                              last_name=edu_teacher_form.last_name.data,
                              languages=edu_teacher_form.languages.data,
                              info=edu_teacher_form.info.data)
            db.session.add(edu_teacher)
            db.session.commit()
            flash("Учитель добавлен успешно!f!", 'success')
            return redirect(url_for('edu_teacher_modal', id=id))

@app.route('/resume')
def resume():
   teachers = Teacher.query.all()
   return render_template('resume.html', teachers=teachers)

@app.route('/edu_centers')
def edu_centers():
   edu_centers = Educenter.query.all()
   return render_template('edu_centers.html', edu_centers=edu_centers)

@app.route('/edu_center_page/<edu_center_id>', methods=['GET', 'POST'])
@login_required
def edu_center_page(edu_center_id):
    current_user = db.session.query(Educenter).filter(Educenter.id == edu_center_id).first()
    courses = db.session.query(Courses).filter_by(edu_center_id=edu_center_id)
    return render_template("edu_center_page.html", user=current_user, courses=courses)


@app.route('/user_page/<teacher_id>', methods=['GET', 'POST'])
@login_required
def user_page(teacher_id):
    current_user = db.session.query(Teacher).filter(
        Teacher.id == teacher_id).first()
    subjects = db.session.query(Subject).filter_by(teacher_id=teacher_id)
    return render_template("user_page.html", user=current_user, subjects=subjects)


@app.route('/course_page/<course_id>', methods=['GET', 'POST'])
@login_required
def course_page(course_id):
    current_course = db.session.query(Courses).filter(
        Courses.id == course_id).first()
    edu_teachers = db.session.query(Eduteachers).filter_by(course_id=course_id)
    return render_template("course_page.html", course=current_course, edu_teachers=edu_teachers)

@app.route('/account/<id>/edit_subject', methods=['GET', 'POST'])
def edit_subject(id):
    subject = Subject.query.filter_by(teacher_id=id).first_or_404()
    form = SubjectForm()
    if request.method == "GET":
        form.subject_name.data = subject.subject_name
        form.subject_price.data = subject.subject_price
        form.subject_description.data = subject.subject_description
        return render_template('add_subject.html', form=form)
    else:
        if form.validate_on_submit:
            subject.subject_name = form.subject_name.data
            subject.subject_price = form.subject_price.data
            subject.subject_description = form.subject_description.data
            db.session.commit()
            flash("Subject has been edited!", 'success')
            return redirect(url_for('account'))

        

@app.route('/account/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    form = CourseForm()
    edu_teachers = db.session.query(Eduteachers).filter_by(course_id = course_id)
    courses = Courses.query.filter_by(id=course_id).first_or_404()
    print(edu_teachers)
    if request.method == "GET":
        form.course_name.data = courses.course_name
        form.course_price.data = courses.course_price
        form.course_description.data = courses.course_description
        return render_template('edit_course.html', form=form, edu_teachers=edu_teachers)
    else:
        if form.validate_on_submit:
            courses.course_name = form.course_name.data
            courses.course_price = form.course_price.data
            courses.course_description = form.course_description.data
            db.session.commit()
            flash("Course has been edited!", 'success')
            return redirect(url_for('account'))



@app.route('/account/edit_course/<id>/edit_edu_teacher', methods=['GET', 'POST'])
def edit_edu_teacher(id):
    edu_teacher = Eduteachers.query.filter_by(id=id).first_or_404()
    form = CourseForm()
    edu_teacher_form = EduTeacher()
    if request.method == "GET":
        edu_teacher_form.first_name.data = edu_teacher.first_name
        edu_teacher_form.last_name.data = edu_teacher.last_name
        edu_teacher_form.languages.data = edu_teacher.languages
        edu_teacher_form.info.data = edu_teacher.info
        return render_template('edit_edu_teacher.html', edu_teacher_form=edu_teacher_form, form=form)
    else:
        if edu_teacher_form.validate_on_submit:
            edu_teacher.first_name = edu_teacher_form.first_name.data
            edu_teacher.last_name = edu_teacher_form.last_name.data
            edu_teacher.languages = edu_teacher_form.languages.data
            edu_teacher.info = edu_teacher_form.info.data
            db.session.commit()
            flash("Subject has been edited!", 'success')
            return redirect(url_for('account'))


@app.route('/account/<id>/delete_subject', methods=['GET', 'POST'])
def delete_subject(id):
    subject = Subject.query.filter_by(id=id).first_or_404()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('account'))


@app.route('/account/<id>/delete_edu_teacher', methods=['GET', 'POST'])
def delete_edu_teacher(id):
    edu_teacher = Eduteachers.query.filter_by(id=id).first_or_404()
    db.session.delete(edu_teacher)
    db.session.commit()
    return redirect(url_for('account'))


@app.route('/account/<course_id>/delete_course', methods=['GET', 'POST'])
def delete_course(course_id):
    course = Courses.query.filter_by(id=course_id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('account'))


@app.route('/sign_up/edu_center', methods=['GET', 'POST'])
def edu_center_sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    edu_center_form = EduCenterRegistrationForm()
    if request.method == "POST":
        hashed_password = bcrypt.generate_password_hash(
            edu_center_form.password.data).decode('utf-8')
        edu_center = Educenter(
            name=edu_center_form.name.data,
            phone_number=edu_center_form.phone_number.data,
            email=edu_center_form.email.data,
            description=edu_center_form.description.data,
            address=edu_center_form.address.data,
            password=hashed_password
        )
        db.session.add(edu_center)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('sign_in'))

    return render_template('edu_centers_sign_up.html', title='Sign-up', edu_center_form=edu_center_form)






def set_session_teacher():
    session['type'] = 'Teacher'
    return f"The session has been Set"


@app.route('/set_session_edu')
def set_session_edu_center():
    session['type'] = 'EduCenter'
    return f"The session has been Set"

@app.route('/set_session')
def set_session():
    global sessiontype
    print(sessiontype)
    session['type'] = sessiontype
    return f"The session has been Set"
