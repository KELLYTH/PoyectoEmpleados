from flask import Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL
import bcrypt
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
#import pymysql.cursors
import re


app = Flask(__name__)
app.secret_key = 'your secret key'


#Se configura la Base de datos
app.config['MYSQL_HOST'] = '185.201.10.73'
app.config['MYSQL_USER'] = 'u830599386_danielc'
app.config['MYSQL_PASSWORD'] = 'Z/IRWty@2D!y'
app.config['MYSQL_DB'] = 'u830599386_ppython_dc'

#Se crea el objeto MySQL
mysql = MySQL(app)

#Se crea una semilla
semilla = bcrypt.gensalt()

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
      # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        password_encode = password.encode("utf-8")
        cur = mysql.connection.cursor()

        #Se prepara el Querry para la consulta
        sQuerry = "select id, nombres , apellidos, cedula, usuario, email, telefono, rol, password from usuarios where usuario = %s"

        #Se ejecuta la sentencia
        cur.execute(sQuerry,[username])

        #Se obtiene el dato
        dato = cur.fetchone()

        #Se cierra la consulta
        cur.close()

        if (dato !=None):
            
            # Se verifica que la contraseña sea correcta
            if (password == dato[8] ): 

              if dato:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = dato[0]
                session['username'] = dato[4]

                #Redirige al index
                return render_template('home.html')
            else:
                #Mensaje
                msg = ("El password es incorrecto", "alert-warning")

                #Redirecciona al ingreso
                return render_template('index.html')
        else:
                msg = ("El usuario es incorrecto o no existe", "alert-warning")
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'nombres' in request.form and 'apellidos' in request.form and 'cedula' in request.form and 'usuario' in request.form and 'email' in request.form and 'telefono' in request.form and 'rol' in request.form and 'password' in request.form:
        # Create variables for easy access
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        cedula = request.form['cedula']
        usuario = request.form['usuario']
        email = request.form['email']
        telefono = request.form['telefono']
        rol = request.form['rol']
        password = request.form['password']

        # Check if account exists using MySQL
        cur = mysql.connection.cursor()

        #Se prepara el Querry para la consulta
        sQuerry = "select * from usuarios where usuario = %s"

        #Se ejecuta la sentencia
        cur.execute(sQuerry,[usuario])

        #Se obtiene el dato
        datos = cur.fetchone()

        #Se cierra la consulta
        cur.close()
        # If account exists show error and validation checks
        if datos:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'Username must contain only characters and numbers!'
        elif not usuario or not password or not email:
            msg = 'Por favor llena el Formulario!'
        else:
        
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            #Se realiza el Querry de Inserción
            sQuery = "insert into usuarios (nombres, apellidos, cedula, usuario, email, telefono,rol,password) values (%s, %s, %s, %s, %s, %s, %s, %s)"

           #Se crea el cursos para la ejecución
            cur = mysql.connection.cursor()

           #Ejecuta la sentencia
            cur.execute(sQuery,(nombres, apellidos, cedula, usuario, email, telefono, rol, password))

           #Ejecuta el Commit
        mysql.connection.commit()
        msg = 'Tu Registro ha sido Exitoso!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Por favor llena el Formulario!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        account=cur.fetchone()
        # Show the profile page with account info
        return render_template('profileEmpleado.html', account=account)
    return redirect(url_for('login'))
@app.route('/pythonlogin/registroHorario')
def registroHorario():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        account=cur.fetchone()
        # Show the profile page with account info
        return render_template('registroHorario.html', account=account)
    return redirect(url_for('login'))
#Verificación Sesión administrador
@app.route('/pythonlogin/registroEntrada', methods=["GET", "POST"])
def administrador():
    pass
#Verificación Sesión administrador
@app.route('/pythonlogin/registroSalida', methods=["GET", "POST"])
def registrar():
    pass
if __name__ == '__main__':
    app.run(debug=True)