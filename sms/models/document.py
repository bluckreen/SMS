from extensions import db
from datetime import datetime


class StudentDocument(db.Model):
    __tablename__ = 'student_documents'

    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # Document type: aadhaar, sslc, plus_two, admit_card, birth_cert,
    #                bona_fide, caste_cert, disability_cert, income_cert, tc
    doc_type    = db.Column(db.String(50), nullable=False)
    file_path   = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.doc_type} for student {self.student_id}>'
