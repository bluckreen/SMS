from extensions import db
from datetime import datetime


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)

    # --- Personal Information ---
    aadhaar_id        = db.Column(db.String(14), unique=True, nullable=False)
    full_name         = db.Column(db.String(150), nullable=False)
    date_of_birth     = db.Column(db.Date, nullable=False)
    gender            = db.Column(db.String(20))
    nationality       = db.Column(db.String(50))
    blood_group       = db.Column(db.String(5))
    native_language   = db.Column(db.String(50))
    religion          = db.Column(db.String(50))
    caste             = db.Column(db.String(50))
    photo_path        = db.Column(db.String(255))

    # --- Contact Information (Present Address) ---
    present_premises  = db.Column(db.String(150))
    present_locality  = db.Column(db.String(100))
    present_sub_locality = db.Column(db.String(100))
    present_country   = db.Column(db.String(50))
    present_state     = db.Column(db.String(50))
    present_district  = db.Column(db.String(50))
    present_pincode   = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(15))
    student_mobile    = db.Column(db.String(15))
    student_email     = db.Column(db.String(100))
    parent_mobile     = db.Column(db.String(15))
    parent_email      = db.Column(db.String(100))

    # --- Permanent Address ---
    same_as_present       = db.Column(db.Boolean, default=False)
    permanent_premises    = db.Column(db.String(150))
    permanent_locality    = db.Column(db.String(100))
    permanent_sub_locality = db.Column(db.String(100))
    permanent_country     = db.Column(db.String(50))
    permanent_state       = db.Column(db.String(50))
    permanent_district    = db.Column(db.String(50))
    permanent_pincode     = db.Column(db.String(10))

    # --- Family Details ---
    father_name           = db.Column(db.String(150))
    father_occupation     = db.Column(db.String(100))
    father_qualification  = db.Column(db.String(100))
    mother_name           = db.Column(db.String(150))
    mother_occupation     = db.Column(db.String(100))
    mother_qualification  = db.Column(db.String(100))
    guardian_different    = db.Column(db.Boolean, default=False)
    guardian_name         = db.Column(db.String(150))
    guardian_occupation   = db.Column(db.String(100))
    guardian_mobile       = db.Column(db.String(15))
    guardian_email        = db.Column(db.String(100))
    annual_family_income  = db.Column(db.Float)

    # --- Admission Details ---
    admission_number  = db.Column(db.String(50), unique=True)
    date_of_admission = db.Column(db.Date)
    academic_year     = db.Column(db.String(10))
    admission_quota   = db.Column(db.String(50))
    # 0=Active, 1=Dropped, 2=Alumni, 3=Maternity leave/Re-admission
    admission_status  = db.Column(db.Integer, default=0)

    # --- Academic Information ---
    course_enrolled       = db.Column(db.String(100))
    department            = db.Column(db.String(100))
    semester              = db.Column(db.String(20))
    batch                 = db.Column(db.String(20))
    medium_of_instruction = db.Column(db.String(50))
    previous_school       = db.Column(db.String(150))
    register_number       = db.Column(db.String(50))

    # --- TC Details ---
    tc_number    = db.Column(db.String(50))
    tc_issue_date = db.Column(db.Date)
    tc_issued_by = db.Column(db.String(100))
    tc_reason    = db.Column(db.String(200))
    tc_remarks   = db.Column(db.Text)

    # --- Health & Special Info ---
    medical_conditions  = db.Column(db.Text)
    allergies           = db.Column(db.Text)
    disability          = db.Column(db.String(50))       # None/Physical/Visual/Hearing/Learning
    disability_cert_path = db.Column(db.String(255))
    medical_insurance   = db.Column(db.Boolean, default=False)
    insurance_id        = db.Column(db.String(50))
    counselling_records = db.Column(db.Text)
    special_support     = db.Column(db.Text)

    # --- Hostel & Transport ---
    requires_hostel       = db.Column(db.Boolean, default=False)
    room_type             = db.Column(db.String(20))     # Single/Double/Dormitory
    assigned_room_no      = db.Column(db.String(20))
    hostel_fee_status     = db.Column(db.String(20))     # Paid/Unpaid/Partial
    student_hostel_status = db.Column(db.String(20))     # In hostel/Not in hostel
    hostel_admission_date = db.Column(db.Date)
    residential_status    = db.Column(db.String(20))     # Day scholar/Hosteller

    requires_transport    = db.Column(db.Boolean, default=False)
    transport_no          = db.Column(db.String(20))
    transport_fee_status  = db.Column(db.String(20))     # Paid/Unpaid/Partial
    pickup_point          = db.Column(db.String(100))
    drop_point            = db.Column(db.String(100))
    transport_start_date  = db.Column(db.Date)

    # --- Student Interests & Career ---
    hobbies               = db.Column(db.Text)
    favourite_subjects    = db.Column(db.Text)
    preferred_learning    = db.Column(db.String(50))     # Auditory/Visual/etc.
    career_goal           = db.Column(db.Text)
    reason_for_career     = db.Column(db.Text)
    interested_entrepreneur = db.Column(db.Boolean, default=False)
    interested_corporate  = db.Column(db.Boolean, default=False)
    soft_skills_to_improve = db.Column(db.Text)

    # --- Timestamps ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    documents  = db.relationship('StudentDocument', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    marks      = db.relationship('Mark', backref='student', lazy=True, cascade='all, delete-orphan')
    library    = db.relationship('LibraryRecord', backref='student', lazy=True, cascade='all, delete-orphan')

    @property
    def admission_status_label(self):
        labels = {0: 'Active', 1: 'Dropped', 2: 'Alumni', 3: 'Re-admission'}
        return labels.get(self.admission_status, 'Unknown')

    def __repr__(self):
        return f'<Student {self.admission_number} - {self.full_name}>'
