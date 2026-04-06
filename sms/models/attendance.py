from extensions import db
from datetime import datetime


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    semester         = db.Column(db.String(20), nullable=False)
    course           = db.Column(db.String(100), nullable=False)
    total_classes    = db.Column(db.Integer, default=0)
    classes_attended = db.Column(db.Integer, default=0)
    # Status: Satisfactory / Shortage / Excellent
    status           = db.Column(db.String(20))

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0.0
        return round((self.classes_attended / self.total_classes) * 100, 2)

    @property
    def computed_status(self):
        p = self.percentage
        if p >= 90:
            return 'Excellent'
        elif p >= 75:
            return 'Satisfactory'
        else:
            return 'Shortage'

    def __repr__(self):
        return f'<Attendance {self.course} - {self.percentage}%>'


class Mark(db.Model):
    __tablename__ = 'marks'

    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    semester       = db.Column(db.String(20), nullable=False)
    course         = db.Column(db.String(100), nullable=False)
    marks_obtained = db.Column(db.Float, default=0)
    maximum_marks  = db.Column(db.Float, default=100)
    grade          = db.Column(db.String(5))
    # Status: Pass / Fail / Absent
    status         = db.Column(db.String(10))
    sgpa           = db.Column(db.Float)

    @property
    def percentage(self):
        if self.maximum_marks == 0:
            return 0.0
        return round((self.marks_obtained / self.maximum_marks) * 100, 2)

    def __repr__(self):
        return f'<Mark {self.course} - {self.grade}>'
