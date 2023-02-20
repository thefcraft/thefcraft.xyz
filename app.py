from flask import Flask, url_for, render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random, os, secrets
import base64
os.chdir(os.path.dirname(__file__))
def obfuscate(plainText):
    plainBytes = plainText.encode('ascii')
    encodedBytes = base64.b64encode(plainBytes)
    encodedText = encodedBytes.decode('ascii')
    return encodedText

def deobfuscate(obfuscatedText):
    obfuscatedBytes = obfuscatedText.encode('ascii')
    decodedBytes = base64.b64decode(obfuscatedBytes)
    decodedText = decodedBytes.decode('ascii')
    return decodedText

def debug(error):
    # print(error)
    return 

class User():
    filename = os.path.join('static', 'instance', 'user.db.tc')

    def __init__(self, username=None, password=None, email=None, otp=None, is_registration=False):
        self.username = username
        self.password = password
        self.email = email
        self.otp = otp
        self.is_registration = is_registration
        if username is None and password is None and otp is None and email is None: pass
        else:
            if ', ' in str(username) or ', ' in str(password): raise ValueError('Username and password must not contain ", "')
            self.save()
        
    def make_instance(self=None):
        return 
        filename = os.path.join('static', 'instance', 'user.db.tc')
        if not os.path.exists('instance'): 
            os.makedirs('instance')

            db = '# username, password, email, otp'

            with open(filename, 'w') as f: 
                f.write(obfuscate(db)+'\n')
    
    def filter_by(self=None, email=None, password=None, otp=None, username=None):
        db = User.old_db()
        output = []
        for i in db:
            if email is not None and password is not None:
                if i[1] == password and i[2] == email: 
                    output.append(i)
            
            elif email is not None:
                if i[2] == email: 
                    output.append(i)
        if len(output) == 0: return None
        return output[0]
        
    def old_db(self=None):
        filename = os.path.join('static', 'instance', 'user.db.tc')
        output = []
        with open(filename, 'r') as f: 
            for line in f.readlines():
                line = deobfuscate(line.replace('\n',''))
                if not line.strip().startswith('#'):
                    output.append(line.strip().split(', '))
        return output
        
    def save(self):    
        db = self.old_db()
        
        for i in db:
            if i[2] == self.email:
                if self.is_registration: raise ValueError('email already exists')        
                else:
                    updatedb = obfuscate(f'{self.username}, {self.password}, {self.email}, {self.otp}')+'\n'
                    data = obfuscate('# username, password, email, otp')+'\n'
                    for i in db:
                        if i[2] == self.email: continue
                        data += obfuscate(f'{i[0]}, {i[1]}, {i[2]}, {i[3]}') + '\n'
                    data+=updatedb
                    with open(self.filename, 'w') as f: 
                        f.write(data)
                    return True

        db = obfuscate( f'{self.username}, {self.password}, {self.email}, {self.otp}' )+'\n'
        with open(self.filename, 'a') as f: 
            f.write(db)


MAIL_USERNAME = 'thefcraft.xyz@gmail.com'
MAIL_PASSWORD = 'vxjkzayehnlygqla'

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



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
            User(username=u, password=p, email=e, is_registration = True)
            return otp_verify(email=e)
            # return redirect(url_for('login'))
            # return render_template('index.html', message=f"welcome {u}")    
        
        except Exception as e:
            debug(e)
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
        data = User.filter_by(email=e, password=p)

        if User.filter_by(email=e) is None:
            return redirect(url_for('register'))
        
        if User.filter_by(email=e)[1] is None:
            return redirect(url_for('forgotPassword'))
        
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))

        return render_template('index.html', message="Incorrect Details")

@app.route('/forgot-password/', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        e = request.form['email']
        data = User.filter_by(email=e)
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
            
            User(username = User.filter_by(email=email)[0], email=email, otp=otp, password=User.filter_by(email=email)[1])
            # user = User.filter_by(email=email)
            # user.otp = otp
            return render_template('otp_verify.html', email=email, message='Enter your 5 digit otp')
        
        else:
            return render_template('error.html', message='Something went wrong')
    
    else:
        if request.method == 'POST':
            otp = request.form['otp']
            data = User.filter_by(email=e)
            if data[3] == otp:
                password = request.form['password']
                User(username = User.filter_by(email=e)[0], email=e, otp='None', password = password)
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
    # print(otp)
    # return True
    msg = Message(f"OTP Code :- {otp}", sender=MAIL_USERNAME, recipients=[email])
    with open(os.path.join('static', 'email','otp.html') , 'r', encoding='UTF-8') as file:
        html = file.read().replace('{otp}', str(otp))
    msg.html = html
    mail.send(msg)
    return True

if(__name__ == '__main__'):
    
    # with app.app_context():
        # print(app.name)
        # db.create_all()
    User().make_instance()

    app.run(host='0.0.0.0', debug=True)
