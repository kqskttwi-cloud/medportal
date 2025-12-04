from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medcenter.db'
db = SQLAlchemy(app)

# ------------------ Моделі ------------------
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    date = db.Column(db.String(50))

    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)

# ------------------ Головна сторінка з пошуком ------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.form.get('query')
    results = None
    if query:
        results = {
            'patients': Patient.query.filter(Patient.name.contains(query)).all(),
            'doctors': Doctor.query.filter(Doctor.name.contains(query)).all(),
            'appointments': Appointment.query.filter(Appointment.date.contains(query)).all(),
            'services': Service.query.filter(Service.name.contains(query)).all()
        }
    return render_template('index.html', results=results)

# ------------------ Розділи ------------------
@app.route('/patients')
def patients():
    return render_template('patients.html', patients=Patient.query.all())

@app.route('/doctors')
def doctors():
    return render_template('doctors.html', doctors=Doctor.query.all())

@app.route('/appointments')
def appointments():
    return render_template('appointments.html',
                           appointments=Appointment.query.all(),
                           patients=Patient.query.all(),
                           doctors=Doctor.query.all())

@app.route('/services')
def services():
    return render_template('services.html', services=Service.query.all())

# ------------------ Додавання ------------------
@app.route('/add_patient', methods=['POST'])
def add_patient():
    p = Patient(name=request.form['name'], age=request.form['age'])
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('patients'))

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    d = Doctor(name=request.form['name'], specialty=request.form['specialty'])
    db.session.add(d)
    db.session.commit()
    return redirect(url_for('doctors'))

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    a = Appointment(patient_id=request.form['patient_id'],
                    doctor_id=request.form['doctor_id'],
                    date=request.form['date'])
    db.session.add(a)
    db.session.commit()
    return redirect(url_for('appointments'))

@app.route('/add_service', methods=['POST'])
def add_service():
    s = Service(name=request.form['name'],
                description=request.form.get('description', ''),
                price=request.form.get('price', 0))
    db.session.add(s)
    db.session.commit()
    return redirect(url_for('services'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)