import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from extensions import db
from models.student import Student
from models.document import StudentDocument

students_bp = Blueprint('students', __name__)
ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

def parse_date(d):
    try:
        return datetime.strptime(d, '%Y-%m-%d').date() if d else None
    except Exception:
        return None

def save_file(file, subfolder, prefix=''):
    if file and file.filename and allowed_file(file.filename):
        folder = os.path.join('static', 'uploads', subfolder)
        os.makedirs(folder, exist_ok=True)
        filename = secure_filename(f"{prefix}_{file.filename}")
        file.save(os.path.join(folder, filename))
        return f"uploads/{subfolder}/{filename}"
    return None


# ── List ─────────────────────────────────────────────────────────────────────
@students_bp.route('/')
def index():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('students/index.html', students=students)


# ── Step 1: Personal ─────────────────────────────────────────────────────────
@students_bp.route('/register', methods=['GET'])
def register():
    session.pop('reg_data', None)
    return render_template('students/register_personal.html', form_data={})

@students_bp.route('/register/personal', methods=['POST'])
def register_personal():
    form_data = {k: request.form.get(k, '').strip() for k in
                 ['aadhaar_id','full_name','date_of_birth','gender',
                  'nationality','blood_group','native_language','religion','caste']}

    if not all([form_data['aadhaar_id'], form_data['full_name'], form_data['date_of_birth']]):
        flash('Please fill all required fields.', 'danger')
        return render_template('students/register_personal.html', form_data=form_data)

    if Student.query.filter_by(aadhaar_id=form_data['aadhaar_id']).first():
        flash('A student with this Aadhaar ID already exists.', 'danger')
        return render_template('students/register_personal.html', form_data=form_data)

    photo_path = save_file(request.files.get('photo'), 'photos', form_data['aadhaar_id'])
    if photo_path:
        form_data['photo_path'] = photo_path

    session['reg_data'] = form_data
    return redirect(url_for('students.register_contact'))


# ── Step 2: Contact ───────────────────────────────────────────────────────────
@students_bp.route('/register/contact', methods=['GET', 'POST'])
def register_contact():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        session['reg_data'].update({k: request.form.get(k, '') for k in
            ['present_premises','present_locality','present_sub_locality',
             'present_country','present_state','present_district','present_pincode',
             'emergency_contact','student_mobile','student_email','parent_mobile','parent_email']})
        session.modified = True
        return redirect(url_for('students.register_permanent'))
    return render_template('students/register_contact.html', form_data=session['reg_data'])


# ── Step 3: Permanent Address ─────────────────────────────────────────────────
@students_bp.route('/register/permanent', methods=['GET', 'POST'])
def register_permanent():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        same = request.form.get('same_as_present') == 'on'
        reg = session['reg_data']
        if same:
            session['reg_data'].update({
                'same_as_present': True,
                'permanent_premises': reg.get('present_premises',''),
                'permanent_locality': reg.get('present_locality',''),
                'permanent_sub_locality': reg.get('present_sub_locality',''),
                'permanent_country': reg.get('present_country',''),
                'permanent_state': reg.get('present_state',''),
                'permanent_district': reg.get('present_district',''),
                'permanent_pincode': reg.get('present_pincode',''),
            })
        else:
            session['reg_data'].update({
                'same_as_present': False,
                **{k: request.form.get(k, '') for k in
                   ['permanent_premises','permanent_locality','permanent_sub_locality',
                    'permanent_country','permanent_state','permanent_district','permanent_pincode']}
            })
        session.modified = True
        return redirect(url_for('students.register_family'))
    return render_template('students/register_permanent.html', form_data=session['reg_data'])


# ── Step 4: Family ────────────────────────────────────────────────────────────
@students_bp.route('/register/family', methods=['GET', 'POST'])
def register_family():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        session['reg_data'].update({
            **{k: request.form.get(k, '') for k in
               ['father_name','father_occupation','father_qualification',
                'mother_name','mother_occupation','mother_qualification',
                'guardian_name','guardian_occupation','guardian_mobile',
                'guardian_email','annual_family_income']},
            'guardian_different': request.form.get('guardian_different') == 'on',
        })
        session.modified = True
        return redirect(url_for('students.register_admission'))
    return render_template('students/register_family.html', form_data=session['reg_data'])


# ── Step 5: Admission ─────────────────────────────────────────────────────────
@students_bp.route('/register/admission', methods=['GET', 'POST'])
def register_admission():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        session['reg_data'].update({
            'admission_number':  request.form.get('admission_number',''),
            'date_of_admission': request.form.get('date_of_admission',''),
            'academic_year':     request.form.get('academic_year',''),
            'admission_quota':   request.form.get('admission_quota',''),
            'admission_status':  int(request.form.get('admission_status', 0)),
        })
        session.modified = True
        return redirect(url_for('students.register_academic'))
    return render_template('students/register_admission.html', form_data=session['reg_data'])


# ── Step 6: Academic ──────────────────────────────────────────────────────────
@students_bp.route('/register/academic', methods=['GET', 'POST'])
def register_academic():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        session['reg_data'].update({k: request.form.get(k, '') for k in
            ['course_enrolled','department','semester','batch','register_number',
             'medium_of_instruction','previous_school',
             'tc_number','tc_issue_date','tc_issued_by','tc_reason','tc_remarks']})
        session.modified = True
        return redirect(url_for('students.register_documents'))
    return render_template('students/register_academic.html', form_data=session['reg_data'])


# ── Step 7: Documents ─────────────────────────────────────────────────────────
@students_bp.route('/register/documents', methods=['GET', 'POST'])
def register_documents():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        doc_types = ['aadhaar','sslc','plus_two','admit_card',
                     'birth_cert','bona_fide','caste_cert','disability_cert','income_cert']
        docs = {}
        prefix = session['reg_data'].get('aadhaar_id','doc')
        for dt in doc_types:
            path = save_file(request.files.get(dt), 'documents', f"{prefix}_{dt}")
            if path:
                docs[dt] = path
        session['reg_data']['documents'] = docs
        session.modified = True
        return redirect(url_for('students.register_health'))
    return render_template('students/register_documents.html', form_data=session['reg_data'])


# ── Step 8: Health ────────────────────────────────────────────────────────────
@students_bp.route('/register/health', methods=['GET', 'POST'])
def register_health():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))
    if request.method == 'POST':
        session['reg_data'].update({
            **{k: request.form.get(k, '') for k in
               ['medical_conditions','allergies','disability','insurance_id',
                'special_support','counselling_records']},
            'medical_insurance': request.form.get('medical_insurance') == '1',
        })
        session.modified = True
        return redirect(url_for('students.register_hostel'))
    return render_template('students/register_health.html', form_data=session['reg_data'])


# ── Step 9: Hostel & Transport — FINAL SAVE ───────────────────────────────────
@students_bp.route('/register/hostel', methods=['GET', 'POST'])
def register_hostel():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))

    if request.method == 'POST':
        reg = session['reg_data']
        reg.update({
            **{k: request.form.get(k, '') for k in
               ['room_type','assigned_room_no','hostel_fee_status','student_hostel_status',
                'hostel_admission_date','residential_status','transport_no',
                'pickup_point','drop_point','transport_fee_status','transport_start_date']},
            'requires_hostel':    request.form.get('requires_hostel') == '1',
            'requires_transport': request.form.get('requires_transport') == '1',
        })

        try:
            income = float(reg.get('annual_family_income') or 0)
        except ValueError:
            income = 0.0

        student = Student(
            # Personal
            aadhaar_id=reg['aadhaar_id'], full_name=reg['full_name'],
            date_of_birth=parse_date(reg['date_of_birth']),
            gender=reg.get('gender'), nationality=reg.get('nationality'),
            blood_group=reg.get('blood_group'), native_language=reg.get('native_language'),
            religion=reg.get('religion'), caste=reg.get('caste'),
            photo_path=reg.get('photo_path'),
            # Contact
            present_premises=reg.get('present_premises'),
            present_locality=reg.get('present_locality'),
            present_sub_locality=reg.get('present_sub_locality'),
            present_country=reg.get('present_country'),
            present_state=reg.get('present_state'),
            present_district=reg.get('present_district'),
            present_pincode=reg.get('present_pincode'),
            emergency_contact=reg.get('emergency_contact'),
            student_mobile=reg.get('student_mobile'),
            student_email=reg.get('student_email'),
            parent_mobile=reg.get('parent_mobile'),
            parent_email=reg.get('parent_email'),
            # Permanent
            same_as_present=reg.get('same_as_present', False),
            permanent_premises=reg.get('permanent_premises'),
            permanent_locality=reg.get('permanent_locality'),
            permanent_sub_locality=reg.get('permanent_sub_locality'),
            permanent_country=reg.get('permanent_country'),
            permanent_state=reg.get('permanent_state'),
            permanent_district=reg.get('permanent_district'),
            permanent_pincode=reg.get('permanent_pincode'),
            # Family
            father_name=reg.get('father_name'), father_occupation=reg.get('father_occupation'),
            father_qualification=reg.get('father_qualification'),
            mother_name=reg.get('mother_name'), mother_occupation=reg.get('mother_occupation'),
            mother_qualification=reg.get('mother_qualification'),
            guardian_different=reg.get('guardian_different', False),
            guardian_name=reg.get('guardian_name'), guardian_occupation=reg.get('guardian_occupation'),
            guardian_mobile=reg.get('guardian_mobile'), guardian_email=reg.get('guardian_email'),
            annual_family_income=income,
            # Admission
            admission_number=reg.get('admission_number'),
            date_of_admission=parse_date(reg.get('date_of_admission')),
            academic_year=reg.get('academic_year'),
            admission_quota=reg.get('admission_quota'),
            admission_status=reg.get('admission_status', 0),
            # Academic
            course_enrolled=reg.get('course_enrolled'),
            department=reg.get('department'), semester=reg.get('semester'),
            batch=reg.get('batch'), register_number=reg.get('register_number'),
            medium_of_instruction=reg.get('medium_of_instruction'),
            previous_school=reg.get('previous_school'),
            tc_number=reg.get('tc_number'),
            tc_issue_date=parse_date(reg.get('tc_issue_date')),
            tc_issued_by=reg.get('tc_issued_by'), tc_reason=reg.get('tc_reason'),
            tc_remarks=reg.get('tc_remarks'),
            # Health
            medical_conditions=reg.get('medical_conditions'),
            allergies=reg.get('allergies'), disability=reg.get('disability'),
            medical_insurance=reg.get('medical_insurance', False),
            insurance_id=reg.get('insurance_id'),
            special_support=reg.get('special_support'),
            counselling_records=reg.get('counselling_records'),
            # Hostel
            requires_hostel=reg.get('requires_hostel', False),
            room_type=reg.get('room_type'), assigned_room_no=reg.get('assigned_room_no'),
            hostel_fee_status=reg.get('hostel_fee_status'),
            student_hostel_status=reg.get('student_hostel_status'),
            hostel_admission_date=parse_date(reg.get('hostel_admission_date')),
            residential_status=reg.get('residential_status'),
            # Transport
            requires_transport=reg.get('requires_transport', False),
            transport_no=reg.get('transport_no'),
            transport_fee_status=reg.get('transport_fee_status'),
            pickup_point=reg.get('pickup_point'), drop_point=reg.get('drop_point'),
            transport_start_date=parse_date(reg.get('transport_start_date')),
        )

        session.modified = True
        return redirect(url_for('students.register_interests'))

    return render_template('students/register_hostel.html', form_data=session['reg_data'])


# ── Step 10: Interests & Career — FINAL SAVE ──────────────────────────────────
@students_bp.route('/register/interests', methods=['GET', 'POST'])
def register_interests():
    if 'reg_data' not in session:
        return redirect(url_for('students.register'))

    if request.method == 'POST':
        reg = session['reg_data']
        reg.update({
            'hobbies':                 request.form.get('hobbies', ''),
            'favourite_subjects':      request.form.get('favourite_subjects', ''),
            'preferred_learning':      request.form.get('preferred_learning', ''),
            'soft_skills_to_improve':  request.form.get('soft_skills_to_improve', ''),
            'career_goal':             request.form.get('career_goal', ''),
            'reason_for_career':       request.form.get('reason_for_career', ''),
            'interested_entrepreneur': request.form.get('interested_entrepreneur') == '1',
            'interested_corporate':    request.form.get('interested_corporate') == '1',
        })

        try:
            income = float(reg.get('annual_family_income') or 0)
        except ValueError:
            income = 0.0

        student = Student(
            aadhaar_id=reg['aadhaar_id'], full_name=reg['full_name'],
            date_of_birth=parse_date(reg['date_of_birth']),
            gender=reg.get('gender'), nationality=reg.get('nationality'),
            blood_group=reg.get('blood_group'), native_language=reg.get('native_language'),
            religion=reg.get('religion'), caste=reg.get('caste'),
            photo_path=reg.get('photo_path'),
            present_premises=reg.get('present_premises'),
            present_locality=reg.get('present_locality'),
            present_sub_locality=reg.get('present_sub_locality'),
            present_country=reg.get('present_country'),
            present_state=reg.get('present_state'),
            present_district=reg.get('present_district'),
            present_pincode=reg.get('present_pincode'),
            emergency_contact=reg.get('emergency_contact'),
            student_mobile=reg.get('student_mobile'),
            student_email=reg.get('student_email'),
            parent_mobile=reg.get('parent_mobile'),
            parent_email=reg.get('parent_email'),
            same_as_present=reg.get('same_as_present', False),
            permanent_premises=reg.get('permanent_premises'),
            permanent_locality=reg.get('permanent_locality'),
            permanent_sub_locality=reg.get('permanent_sub_locality'),
            permanent_country=reg.get('permanent_country'),
            permanent_state=reg.get('permanent_state'),
            permanent_district=reg.get('permanent_district'),
            permanent_pincode=reg.get('permanent_pincode'),
            father_name=reg.get('father_name'), father_occupation=reg.get('father_occupation'),
            father_qualification=reg.get('father_qualification'),
            mother_name=reg.get('mother_name'), mother_occupation=reg.get('mother_occupation'),
            mother_qualification=reg.get('mother_qualification'),
            guardian_different=reg.get('guardian_different', False),
            guardian_name=reg.get('guardian_name'), guardian_occupation=reg.get('guardian_occupation'),
            guardian_mobile=reg.get('guardian_mobile'), guardian_email=reg.get('guardian_email'),
            annual_family_income=income,
            admission_number=reg.get('admission_number'),
            date_of_admission=parse_date(reg.get('date_of_admission')),
            academic_year=reg.get('academic_year'),
            admission_quota=reg.get('admission_quota'),
            admission_status=reg.get('admission_status', 0),
            course_enrolled=reg.get('course_enrolled'),
            department=reg.get('department'), semester=reg.get('semester'),
            batch=reg.get('batch'), register_number=reg.get('register_number'),
            medium_of_instruction=reg.get('medium_of_instruction'),
            previous_school=reg.get('previous_school'),
            tc_number=reg.get('tc_number'),
            tc_issue_date=parse_date(reg.get('tc_issue_date')),
            tc_issued_by=reg.get('tc_issued_by'), tc_reason=reg.get('tc_reason'),
            tc_remarks=reg.get('tc_remarks'),
            medical_conditions=reg.get('medical_conditions'),
            allergies=reg.get('allergies'), disability=reg.get('disability'),
            medical_insurance=reg.get('medical_insurance', False),
            insurance_id=reg.get('insurance_id'),
            special_support=reg.get('special_support'),
            counselling_records=reg.get('counselling_records'),
            requires_hostel=reg.get('requires_hostel', False),
            room_type=reg.get('room_type'), assigned_room_no=reg.get('assigned_room_no'),
            hostel_fee_status=reg.get('hostel_fee_status'),
            student_hostel_status=reg.get('student_hostel_status'),
            hostel_admission_date=parse_date(reg.get('hostel_admission_date')),
            residential_status=reg.get('residential_status'),
            requires_transport=reg.get('requires_transport', False),
            transport_no=reg.get('transport_no'),
            transport_fee_status=reg.get('transport_fee_status'),
            pickup_point=reg.get('pickup_point'), drop_point=reg.get('drop_point'),
            transport_start_date=parse_date(reg.get('transport_start_date')),
            hobbies=reg.get('hobbies'),
            favourite_subjects=reg.get('favourite_subjects'),
            preferred_learning=reg.get('preferred_learning'),
            soft_skills_to_improve=reg.get('soft_skills_to_improve'),
            career_goal=reg.get('career_goal'),
            reason_for_career=reg.get('reason_for_career'),
            interested_entrepreneur=reg.get('interested_entrepreneur', False),
            interested_corporate=reg.get('interested_corporate', False),
        )

        db.session.add(student)
        db.session.flush()

        for doc_type, path in reg.get('documents', {}).items():
            db.session.add(StudentDocument(
                student_id=student.id, doc_type=doc_type, file_path=path))

        db.session.commit()
        session.pop('reg_data', None)
        flash(f'Student "{student.full_name}" registered successfully!', 'success')
        return redirect(url_for('students.index'))

    return render_template('students/register_interests.html', form_data=session['reg_data'])


# ── Detail view ───────────────────────────────────────────────────────────────
@students_bp.route('/<int:student_id>')
def detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/detail.html', student=student)
