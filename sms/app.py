from flask import Flask, render_template
from extensions import db
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.library import library_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sms-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    db.init_app(app)

    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(library_bp, url_prefix='/library')

    @app.route('/')
    def index():
        from models.student import Student
        total = Student.query.count()
        active = Student.query.filter_by(admission_status=0).count()
        return render_template('dashboard.html', total=total, active=active)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
