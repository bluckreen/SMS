from extensions import db
from datetime import datetime, date


class LibraryRecord(db.Model):
    __tablename__ = 'library_records'

    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id     = db.Column(db.String(50), nullable=False)
    issue_date  = db.Column(db.Date, nullable=False, default=date.today)
    due_date    = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    # Status: Issued / Returned / Overdue
    status      = db.Column(db.String(20), default='Issued')
    fine        = db.Column(db.Float, default=0.0)

    FINE_PER_DAY = 2  # Rs. 2 per day as per your sketch

    @property
    def computed_fine(self):
        if self.status == 'Returned' or self.return_date:
            check_date = self.return_date
        else:
            check_date = date.today()
        if check_date > self.due_date:
            overdue_days = (check_date - self.due_date).days
            return overdue_days * self.FINE_PER_DAY
        return 0.0

    @property
    def is_overdue(self):
        if self.status == 'Returned':
            return False
        return date.today() > self.due_date

    def __repr__(self):
        return f'<LibraryRecord Book:{self.book_id} Student:{self.student_id}>'
