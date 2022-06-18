from flask import Flask, render_template, request, redirect, url_for, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from flask_mysqldb import MySQL
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'disease'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@12345'
app.config['MYSQL_DB'] = 'diabetic_prj'

mysql = MySQL(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'keerthana.ravi.dsu@gmail.com'
app.config['MAIL_PASSWORD'] = 'yxfsvzasykohcowt'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# MAIL_ASCII_ATTACHMENTS
mail = Mail(app)

dic = {0: "Normal", 1: "Mild_NPDR", 2: "Moderate_NPDR", 3: "Severe_NPDR", 4: "PDR"}

cnn_model = load_model('models/CNN_model.h5')
vgg_model = load_model('models/VGG16_model.h5')
resnet_model = load_model('models/Resnet152V2_model.h5')


def predict_cnn(img_path):
    img = image.load_img(img_path, target_size=(256, 256))
    x = image.img_to_array(img)
    x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)
    p = cnn_model.predict(x)
    x = np.argmax(p)
    return dic[x], p


def predict_vgg(img_path):
    img = image.load_img(img_path, target_size=(256, 256))
    x = image.img_to_array(img)
    x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)
    p = vgg_model.predict(x)
    x = np.argmax(p)
    return dic[x], p


def predict_resnet(img_path):
    img = image.load_img(img_path, target_size=(256, 256))
    x = image.img_to_array(img)
    x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)
    p = resnet_model.predict(x)
    x = np.argmax(p)
    return dic[x], p

# routes


user_mail = []
user_name = []


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("select * from users where email=%s and password=%s", (email, pwd))
        user = cur.fetchone()
        if user:
            session['logged_in'] = True
            print(user)
            name = user[1]
            user_mail.append(email)
            user_name.append(name)
            return render_template('home.html')
        else:
            msg = 'Invalid Login Details Try Again'
            return render_template('login.html', msg=msg, email=email)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['Last_name']
        sex = request.form['gender']
        email = request.form['Email']
        city = request.form['city']
        country = request.form['country']
        Password = request.form['Password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        mail_user = cursor.fetchone()
        if not mail_user:
            cursor.execute('INSERT INTO users(name,last_name,gender,email,password,city,country)'
                           ' VALUES(%s,%s,%s,%s,%s,%s,%s)', (name, last_name, sex, email, Password, city, country))
            mysql.connection.commit()
            cursor.close()
            print("Records created successfully")

            if sex == 'Male':
                msg1 = " Hello mr." + name + " !! U Can login Here !!!"
                return render_template('login.html', msg=msg1, email=email)
            else:
                msg1 = " Hello ms." + name + " !! U Can login Here !!!"
                return render_template('login.html', msg=msg1, email=email)

        msg2 = "This Email Id is already Registered"
        return render_template('register.html', msg1=msg2)

    return render_template('register.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route("/cnn_form", methods=['GET', 'POST'])
def cnn_form():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/" + img.filename
        img.save(img_path)
        p = predict_cnn(img_path)
        acc = p[1][0]
        m = max(acc) * 100
        email = user_mail[0]
        name = user_name[0]
        print(name)
        prediction = p[0]
        accuracy = str(m)
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET output = %s WHERE email=%s", (prediction, email))
        mysql.connection.commit()
        cursor.close()

        try:
            subject = 'Project output '
            msg = Message(subject, sender='smtp.gmail.com', recipients=[email])
            msg.body = "Hi {},\n Your Test Result: {} \n Accuracy: {} \n Please visit the doctor for further details \n Thank you.".format(name, prediction, accuracy)
            mail.send(msg)
            print("Email sent successfully")
        except Exception as e:
            print("Email sending failed")
            print(e)

        return render_template("cnn.html", prediction=p[0], acc=m, img_path=img_path)


@app.route("/vgg_form", methods=['GET', 'POST'])
def vgg_form():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/" + img.filename
        img.save(img_path)
        p = predict_vgg(img_path)
        acc = p[1][0]
        print(acc)
        m = max(acc) * 100
        email = user_mail[0]
        name = user_name[0]
        prediction = p[0]
        # recipient = email
        accuracy = str(m)
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET output = %s WHERE email=%s", (prediction, email))
        mysql.connection.commit()
        cursor.close()

        try:
            subject = 'Project output '
            msg = Message(subject, sender='smtp.gmail.com', recipients=[email])
            # msg.body = "Prediction : " + prediction, '<br>', " Accuracy : " + accuracy
            msg.body = "Hi  {},\r\n Your Test Result:{} \r\n \r\n Accuracy:{} \r\n \r\n Please visit the doctor for further details \r\n Thank you.".format(name, prediction, accuracy)
            mail.send(msg)
            print("Email sent successfully")
        except Exception as e:
            print("Email sending failed")
            print(e)

        return render_template("vgg.html", prediction=p[0], acc=m, img_path=img_path)


@app.route("/resnet_form", methods=['GET', 'POST'])
def resnet_form():
    if request.method == 'POST':
        img = request.files['my_image']
        img_path = "static/" + img.filename
        img.save(img_path)
        p = predict_resnet(img_path)
        acc = p[1][0]
        print(acc)
        m = max(acc) * 100
        email = user_mail[0]
        prediction = p[0]
        name = user_name[0]
        # recipient = email
        accuracy = str(m)
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET output = %s WHERE email=%s", (prediction, email))
        mysql.connection.commit()
        cursor.close()
        try:
            subject = 'Project output '
            msg = Message(subject, sender='smtp.gmail.com', recipients=[email])
            msg.body = "Hi {},\n Your Test Result: {} \n Accuracy: {} \n Please visit the doctor for further details \n Thank you.".format(name, prediction, accuracy)
            # msg.html = render_template('resnet.html')
            mail.send(msg)
            print("Email sent successfully")
        except Exception as e:
            print("Email sending failed")
            print(e)
        return render_template("resnet.html", prediction=p[0], acc=m, img_path=img_path)


@app.route('/password', methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        current_pass = request.form['current']
        new_pass = request.form['new']
        verify_pass = request.form['verify']
        email = user_mail[0]
        cur = mysql.connection.cursor()
        cur.execute("select password from users where email=%s", (email,))
        user = cur.fetchone()
        if user:
            print(user)
            if user == current_pass:
                if new_pass == verify_pass:
                    msg1 = 'Password changed successfully'
                    cur.execute("UPDATE users SET password = %s WHERE password=%s", (new_pass, current_pass))
                    mysql.connection.commit()
                    return render_template('password_change.html', msg1=msg1)
                else:
                    msg2 = 'Re-entered password is not matched'
                    return render_template('password_change.html', msg2=msg2)
            else:
                msg3 = 'Incorrect password'
                return render_template('password_change.html', msg3=msg3)
        else:
            msg3 = 'Incorrect password'
            return render_template('password_change.html', msg3=msg3)
    return render_template('password_change.html')


@app.route('/graphs', methods=['POST', 'GET'])
def graphs():
    return render_template('graphs.html')


@app.route('/cnn')
def cnn():
    return render_template('cnn.html')


@app.route('/vgg')
def vgg():
    return render_template('vgg.html')


@app.route('/resnet')
def resnet():
    return render_template('resnet.html')


@app.route('/logout')
def logout():
    session.clear()
    msg = 'You are now logged out', 'success'
    return redirect(url_for('login', msg=msg))


if __name__ == '__main__':
    app.run(debug=True)
