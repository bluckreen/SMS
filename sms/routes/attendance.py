from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.student import Student
from models.attendance import Attendance, Mark

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
def index():
    students = Student.query.filter_by(admission_status=0).order_by(Student.full_name).all()
    return render_template('attendance/index.html', students=students)

@attendance_bp.route('/add', methods=['GET', 'POST'])
def add():
    students = Student.query.filter_by(admission_status=0).order_by(Student.full_name).all()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        semester   = request.form.get('semester')
        course     = request.form.get('course', '').strip()
        total      = int(request.form.get('total_classes', 0) or 0)
        attended   = int(request.form.get('classes_attended', 0) or 0)
        if not all([student_id, semester, course]):
            flash('Please fill all required fields.', 'danger')
            return render_template('attendance/add.html', students=students)
        record = Attendance(student_id=student_id, semester=semester,
                            course=course, total_classes=total, classes_attended=attended)
        record.status = record.computed_status
        db.session.add(record)
        db.session.commit()
        flash('Attendance record added!', 'success')
        return redirect(url_for('attendance.index'))
    return render_template('attendance/add.html', students=students)

@attendance_bp.route('/student/<int:student_id>')
def student_attendance(student_id):
    student = Student.query.get_or_404(student_id)
    records = Attendance.query.filter_by(student_id=student_id).all()
    marks   = Mark.query.filter_by(student_id=student_id).all()
    return render_template('attendance/student.html',
                           student=student, records=records, marks=marks)

@attendance_bp.route('/marks/add', methods=['GET', 'POST'])
def add_marks():
    students = Student.query.filter_by(admission_status=0).order_by(Student.full_name).all()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        semester   = request.form.get('semester')
        course     = request.form.get('course', '').strip()
        obtained   = float(request.form.get('marks_obtained', 0) or 0)
        maximum    = float(request.form.get('maximum_marks', 100) or 100)
        grade      = request.form.get('grade', '')
        status     = request.form.get('status', 'Pass')
        sgpa       = request.form.get('sgpa', '')
        mark = Mark(student_id=student_id, semester=semester, course=course,
                    marks_obtained=obtained, maximum_marks=maximum,
                    grade=grade, status=status,
                    sgpa=float(sgpa) if sgpa else None)
        db.session.add(mark)
        db.session.commit()
        flash('Marks record added!', 'success')
        return redirect(url_for('attendance.index'))
    return render_template('attendance/add_marks.html', students=students)
