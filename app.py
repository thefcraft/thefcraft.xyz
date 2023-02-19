from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random, os

MAIL_USERNAME = 'thefcraft.xyz@gmail.com'
MAIL_PASSWORD = 'vxjkzayehnlygqla'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    otp = db.Column(db.String(100))


    def __init__(self, username, password, email, otp=None):
        self.username = username
        self.password = password
        self.email = email
        self.otp = otp
        


@app.route('/', methods=['GET'])
def index():
    # print(User.query.all())
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('index.html', message="Welcome to ThefCraft Please Login or Sign Up")

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            e = request.form['email']
            u = request.form['username']
            # p = request.form['password']
            p = None
            db.session.add(User(username=u, password=p, email=e))
            db.session.commit()
            return otp_verify(email=e)
            # return redirect(url_for('login'))
            # return render_template('index.html', message=f"welcome {u}")    
        
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        e = request.form['email']
        p = request.form['password']
        data = User.query.filter_by(email=e, password=p).first()

        if User.query.filter_by(email=e).first().password is None:
            return redirect(url_for('forgotPassword'))
        
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))

        return render_template('index.html', message="Incorrect Details")

@app.route('/forgot-password/', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        e = request.form['email']
        data = User.query.filter_by(email=e).first()
        if data is not None:
            return otp_verify(email=e)    
        
        return render_template('index.html', message="User Not Exists")
    else:
        return render_template('forgot-password.html')

@app.route('/otp-verify/<e>', methods=['GET', 'POST'])
def otp_verify(e=None, email=None):
    if email is not None:
        otp = random.randint(10000, 99999)
        if send_otp(otp, email=email):
            user = User.query.filter_by(email=email).first()
            user.otp = otp
            db.session.commit()
            return render_template('otp_verify.html', email=email, message='Enter your 5 digit otp')
        
        else:
            return render_template('error.html', message='Something went wrong')
    
    else:
        if request.method == 'POST':
            otp = request.form['otp']
            data = User.query.filter_by(email=e).first()
            if data.otp == otp:
                user = User.query.filter_by(email=e).first()
                user.otp = None      
                password = request.form['password']
                user.password = password
                db.session.commit()
                session['logged_in'] = True
                return redirect(url_for('index'))
            
            else:
                return render_template('otp_verify.html', email=e, message = 'Enter your 5 digit otp\nWrong Otp')
        else:
            return redirect(url_for('index'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

def send_otp(otp, email):
    msg = Message(f"OTP Code :- {otp}", sender=MAIL_USERNAME, recipients=[email])
    with open(os.path.join('static', 'email','otp.html') , 'r', encoding='UTF-8') as file:
        html = file.read().replace('{otp}', str(otp))
    msg.html = html
    mail.send(msg)
    return True

if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"
    with app.app_context():
        # print(app.name)
        db.create_all()

    app.run(host='0.0.0.0')
