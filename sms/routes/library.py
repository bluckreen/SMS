from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date, datetime
from extensions import db
from models.student import Student
from models.library import LibraryRecord

library_bp = Blueprint('library', __name__)

@library_bp.route('/')
def index():
    records = LibraryRecord.query.order_by(LibraryRecord.issue_date.desc()).all()
    return render_template('library/index.html', records=records)

@library_bp.route('/add', methods=['GET', 'POST'])
def add():
    students = Student.query.filter_by(admission_status=0).order_by(Student.full_name).all()
    if request.method == 'POST':
        student_id  = request.form.get('student_id')
        book_id     = request.form.get('book_id', '').strip()
        issue_date  = request.form.get('issue_date')
        due_date    = request.form.get('due_date')
        if not all([student_id, book_id, issue_date, due_date]):
            flash('Please fill all required fields.', 'danger')
            return render_template('library/add.html', students=students, today=date.today())
        def pd(d):
            try: return datetime.strptime(d, '%Y-%m-%d').date()
            except: return date.today()
        record = LibraryRecord(student_id=student_id, book_id=book_id,
                               issue_date=pd(issue_date), due_date=pd(due_date))
        db.session.add(record)
        db.session.commit()
        flash('Book issued successfully!', 'success')
        return redirect(url_for('library.index'))
    return render_template('library/add.html', students=students, today=date.today())

@library_bp.route('/return/<int:record_id>', methods=['POST'])
def return_book(record_id):
    record = LibraryRecord.query.get_or_404(record_id)
    record.return_date = date.today()
    record.status = 'Returned'
    record.fine = record.computed_fine
    db.session.commit()
    flash(f'Book returned. Fine: ₹{record.fine}', 'success' if record.fine == 0 else 'warning')
    return redirect(url_for('library.index'))
