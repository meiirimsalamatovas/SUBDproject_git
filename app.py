from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
# Настройка подключения к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SUBDproject.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Определение моделей базы данныхЫЫ
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    group = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    time = db.Column(db.String(50), nullable=False)

    # Связь с моделью Course
    course = db.relationship('Course', backref='schedules')

    # Связь с моделью Teacher
    teacher = db.relationship('Teacher', backref='schedules')

    def __repr__(self):
        return f'<Schedule {self.course.name} - {self.teacher.name}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    # Связь с моделью Student
    student = db.relationship('Student', backref='grades')

    # Связь с моделью Course
    course = db.relationship('Course', backref='grades')

    def __repr__(self):
        return f'<Grade {self.grade} for {self.student.name} in {self.course.name}>'

# Главная страница
@app.route("/")
def index():
    return render_template('index.html')

# Студенты
@app.route("/students")
def students():
    students = Student.query.all()  # Все студенты
    return render_template('view_students.html', students=students)

@app.route("/students/sorted")
def sorted_students():
    students = Student.query.order_by(Student.name).all()  # Сортировка по имени
    return render_template('view_students.html', students=students)

@app.route("/students/filter", methods=['GET', 'POST'])
def filter_students():
    if request.method == 'POST':
        group = request.form['group']  # Получение группы из формы
        students = Student.query.filter_by(group=group).all()  # Фильтрация по группе
        return render_template('view_students.html', students=students)
    return render_template('filter_students.html')

@app.route("/students/search", methods=['GET', 'POST'])
def search_students():
    if request.method == 'POST':
        keyword = request.form['keyword']
        students = Student.query.filter(Student.name.contains(keyword)).all()  # Поиск по имени
        return render_template('view_students.html', students=students)
    return render_template('search_students.html')

@app.route("/students/update/<int:id>", methods=['GET', 'POST'])
def update_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.group = request.form['group']
        try:
            db.session.commit()
            return redirect('/students')
        except:
            return 'Error updating student'
    return render_template('update_student.html', student=student)


@app.route("/students/delete/<int:id>")
def delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        return redirect('/students')
    except:
        return 'Error deleting student'


@app.route("/students/add", methods=['POST', 'GET'])
def add_students():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        group = request.form['group']
        new_student = Student(name=name, age=age, group=group)
        try:
            db.session.add(new_student)
            db.session.commit()
            return redirect('/students')
        except:
            return 'Error'
    return render_template('add_students.html')


# Преподаватели
@app.route("/teachers")
def teachers():
    teachers = Teacher.query.all()  # Все преподаватели
    return render_template('view_teachers.html', teachers=teachers)

@app.route("/teachers/delete/<int:id>")
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    try:
        db.session.delete(teacher)
        db.session.commit()
        return redirect('/teachers')
    except:
        return 'Error deleting teacher'

@app.route("/teachers/update/<int:id>", methods=['GET', 'POST'])
def update_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if request.method == 'POST':
        teacher.name = request.form['name']
        teacher.subject = request.form['subject']
        try:
            db.session.commit()
            return redirect('/teachers')
        except:
            return 'Error updating teacher'
    return render_template('update_teacher.html', teacher=teacher)


@app.route("/teachers/add", methods=['POST', 'GET'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        new_teacher = Teacher(name=name, subject=subject)
        try:
            db.session.add(new_teacher)
            db.session.commit()
            return redirect('/teachers')
        except:
            return 'Error'

    return render_template('add_teacher.html')

# Курсы
@app.route("/courses")
def courses():
    courses = Course.query.all()  # Все курсы
    return render_template('view_courses.html', courses=courses)

@app.route("/courses/delete/<int:id>")
def delete_course(id):
    course = Course.query.get_or_404(id)
    try:
        db.session.delete(course)
        db.session.commit()
        return redirect('/courses')
    except:
        return 'Error deleting course'


@app.route("/courses/update/<int:id>", methods=['GET', 'POST'])
def update_course(id):
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.name = request.form['name']
        course.description = request.form['description']
        try:
            db.session.commit()
            return redirect('/courses')
        except:
            return 'Error updating course'
    return render_template('update_course.html', course=course)


@app.route("/courses/add", methods=['POST', 'GET'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_course = Course(name=name, description=description)
        try:
            db.session.add(new_course)
            db.session.commit()
            return redirect('/courses')
        except:
            return 'Error'
    return render_template('add_course.html')


# Расписания
@app.route("/schedules")
def schedules():
    schedules = Schedule.query.all()  # Все расписания
    return render_template('view_schedules.html', schedules=schedules)

@app.route("/schedules/update/<int:id>", methods=['GET', 'POST'])
def update_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    if request.method == 'POST':
        schedule.time = request.form['time']
        schedule.course_id = request.form['course_id']
        schedule.teacher_id = request.form['teacher_id']
        try:
            db.session.commit()
            return redirect('/schedules')
        except:
            return 'Error updating schedule'
    courses = Course.query.all()
    teachers = Teacher.query.all()
    return render_template('update_schedule.html', schedule=schedule, courses=courses, teachers=teachers)


@app.route("/schedules/delete/<int:id>")
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    try:
        db.session.delete(schedule)
        db.session.commit()
        return redirect('/schedules')
    except:
        return 'Error deleting schedule'



@app.route("/schedules/add", methods=['POST', 'GET'])
def add_schedule():
    if request.method == 'POST':
        course_id = request.form['course_id']
        teacher_id = request.form['teacher_id']
        time = request.form['time']
        new_schedule = Schedule(course_id=course_id, teacher_id=teacher_id, time=time)
        try:
            db.session.add(new_schedule)
            db.session.commit()
            return redirect('/schedules')
        except:
            return 'Error'
    courses = Course.query.all()
    teachers = Teacher.query.all()
    return render_template('add_schedule.html', courses=courses, teachers=teachers)

# Оценки
@app.route("/grades")
def grades():
    grades = Grade.query.all()  # Все оценки
    return render_template('view_grades.html', grades=grades)

@app.route("/grades/update/<int:id>", methods=['GET', 'POST'])
def update_grade(id):
    grade = Grade.query.get_or_404(id)
    if request.method == 'POST':
        grade.grade = request.form['grade']
        try:
            db.session.commit()
            return redirect('/grades')
        except:
            return 'Error updating grade'
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('update_grade.html', grade=grade, students=students, courses=courses)


@app.route("/grades/delete/<int:id>")
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    try:
        db.session.delete(grade)
        db.session.commit()
        return redirect('/grades')
    except:
        return 'Error deleting grade'



@app.route("/grades/add", methods=['POST', 'GET'])
def add_grade():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        grade = request.form['grade']
        new_grade = Grade(student_id=student_id, course_id=course_id, grade=grade)
        try:
            db.session.add(new_grade)
            db.session.commit()
            return redirect('/grades')
        except:
            return 'Error'
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('add_grade.html', students=students, courses=courses)


@app.route("/students/total_count")
def total_count():
    # Получаем общее количество студентов
    total_students = Student.query.count()

    return render_template('student_total.html', total_students=total_students)


#Подсчет итогов по группам
@app.route("/students/group_totals")
def group_totals():
    group_counts=db.session.query(Student.group, func.count(Student.id)).group_by(Student.group).all()
    return render_template('group_totals.html', group_counts=group_counts)

# Перекрестный запрос: Комбинация данных из нескольких таблиц без явной связи
@app.route("/students_courses")
def students_courses():
    result = db.session.query(Student.name, Course.name) \
        .select_from(Student) \
        .join(Grade, Student.id == Grade.student_id) \
        .join(Course, Grade.course_id == Course.id) \
        .all()
    return render_template('students_courses.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)


