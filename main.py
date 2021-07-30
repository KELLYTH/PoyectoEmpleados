from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify,Response
from flask_mysqldb import MySQL
import time
import re
from datetime import datetime ,timedelta
import cv2
from camara import Video
from flask_mysqldb import MySQL
import numpy as np
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
from camara import Video
import MySQLdb.cursors
import io
import xlwt
import pymysql

##Inicia
mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'your secret key'


#Se configura la Base de datos
app.config['MYSQL_HOST'] = '185.201.10.73'
app.config['MYSQL_USER'] = 'u830599386_danielc'
app.config['MYSQL_PASSWORD'] = 'Z/IRWty@2D!y'
app.config['MYSQL_DB'] = 'u830599386_ppython_dc'

#Se crea el objeto MySQL
mysql.init_app(app)

##Metodo Principal
@app.route('/', methods=['GET', 'POST'])
def login():
    
    msg = ''
      # valida si  "username" y "password" POST existen 
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
                return redirect(url_for('home'))
            else:
                #Mensaje
                flash("El password es incorrecto", "alert-warning")

                #Redirecciona al ingreso
                return render_template('index.html')
        else:
                msg = ("El usuario es incorrecto o no existe")
    return render_template('index.html', msg=msg)

##Metodo cerrar sesion
@app.route('/pythonlogin/logout')
def logout():
  # Elimina sesion si el logueo genera error 
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # redirecciona a funcion login
   return redirect(url_for('login'))

##Metodo registrar 
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # variable mensaje
    msg = ''
    # valida si "username", "password" y "email" POST existe 
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

        # definir cursor 
        cur = mysql.connection.cursor()

        #Se prepara el Querry para la consulta
        sQuerry = "select * from usuarios where usuario = %s"

        #Se ejecuta la sentencia
        cur.execute(sQuerry,[usuario])

        #Se obtiene el dato
        datos = cur.fetchone()

        #Se cierra la consulta
        cur.close()
        # valida si hay error en los campos 
        if datos:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'Username must contain only characters and numbers!'
        elif not usuario or not password or not email:
            msg = 'Por favor llena el Formulario!'
        else:
        
            
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
        msg = 'Por favor llena el Formulario!'
    
    return render_template('register.html', msg=msg)
##Metodo inicial de perfil 
@app.route('/pythonlogin/home')
def home():
    # valida si el usuario esta logueado 
    if 'loggedin' in session:
        ##Consulta base 
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        nombre=cur.fetchone()
        ##Consulta base empleados 
        cur = mysql.connection.cursor()
        cur.execute('SELECT id,fecha,hora_ingreso,hora_salida,horas_extras,horas_totales FROM horario_empleados WHERE id = %s', (session['id'],))
        empleados=cur.fetchall()
        
        return render_template('home.html', nombre=nombre,empleados =empleados)
    
    return redirect(url_for('login'))

##Metodo principal de perfil 
@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        account=cur.fetchone()

        return render_template('profileEmpleado.html', account = account)
    return redirect(url_for('login'))

##Metodo registra horas
@app.route('/pythonlogin/registroHorario')
def registroHorario():
    # Check if user is loggedin
    if 'loggedin' in session:

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
        account=cur.fetchone()

        return render_template('registroHorario.html', account=account)
    return redirect(url_for('login'))

##Metodo registra entrada 
@app.route('/pythonlogin/entrada')
def entrada():
    ##Valida session
    if 'loggedin' in session:

     ## variable fecha
     fecha = time.strftime("%Y-%m-%d")
     ## variable de la hora
     Hora = time.strftime("%X")
     
     #Se realiza el Querry de Inserción
     sQuery = "insert into horario_empleados (id, fecha, hora_ingreso) values (%s, %s, %s)"

     #Se crea el cursos para la ejecución
     cur = mysql.connection.cursor()

     #Ejecuta la sentencia
     cur.execute(sQuery,(session['id'], fecha, Hora))
     account =cur.fetchall()
     #Ejecuta el Commit
     mysql.connection.commit()
     flash('Registro Hora Ingreso Correctamente')
     return redirect(url_for('registroHorario'))

##Metdo registra salida
@app.route('/pythonlogin/salida')
def salida():
        
    ##Valida session
    if 'loggedin' in session:
     fecha = time.strftime("%Y-%m-%d")
     Hora = time.strftime("%X")
     cursor = mysql.connection.cursor()
     
     cursor.callproc('sp_horario_empleados',(session['id'],Hora,fecha))
     data = cursor.fetchall()

     if len(data) is 0:
        mysql.connection.commit()
     
     
     flash('Registro Hora Salida Correctamente')
     return redirect(url_for('registroHorario'))

##Filtro fecha 
@app.route("/range",methods=["POST","GET"])
def range():

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        From = request.form['From']
        to = request.form['to']
        print(From)
        print(to)
        query = "SELECT * from horario_empleados WHERE fecha BETWEEN '{}' AND '{}'".format(From,to)
        cur.execute(query)
        ordersrange = cur.fetchall()
        return jsonify({'htmlresponse': render_template('response.html', ordersrange=ordersrange)})

##Descarga Reporte
@app.route('/download/report/excel')
def download_report():

    cur = mysql.connection.cursor()
    cur.execute('SELECT id,fecha,hora_ingreso,hora_salida,horas_extras,horas_totales FROM horario_empleados WHERE id = %s', (session['id'],))
    result=cur.fetchall()

    #output en bytes
    output = io.BytesIO()
    #create WorkBook object
    workbook = xlwt.Workbook()
    #agrega nombre
    sh = workbook.add_sheet('Horas Report')

     #agrega emcabezado 
    sh.write(0, 0, 'Id')
    sh.write(0, 1, 'Fecha')
    sh.write(0, 2, 'Hora Ingreso')
    sh.write(0, 3, 'Hora Salida')
    sh.write(0, 4, 'Horas Extras')
    sh.write(0, 5, 'Horas Totales')
  
    idx = 0
    for row in result:
     sh.write(idx+1, 0, str(row[0]))
     sh.write(idx+1, 1, str(row[1]))
     sh.write(idx+1, 2, str(row[2]))
     sh.write(idx+1, 3, str(row[3]))
     sh.write(idx+1, 4, str(row[4]))
     sh.write(idx+1, 5, str(row[5]))
     idx += 1
  
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=horas_report.xls"})

#Activación De camara 
camara = cv2.VideoCapture(0)
def generador_frames(camara):
    while True:
        frame=camara.get_frame()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')     
##Metodo inicia camara
@app.route('/inicioCamara')
def inicio_camara():
    return Response(generador_frames(Video()),mimetype='multipart/x-mixed-replace; boundary=frame')

##Metodo edision datos
@app.route('/pythonlogin/profile/editar', methods=['GET', 'POST'])
def editar():
    msg = '' 
    if 'loggedin' in session: 
        if request.method == 'POST'  and 'nombres' in request.form and 'apellidos' in request.form and 'cedula' in request.form  and 'email' in request.form and 'telefono' in request.form and 'password' in request.form: 
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            cedula = request.form['cedula']
            email = request.form['email']
            telefono = request.form['telefono']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
            cursor.execute('SELECT * FROM usuarios WHERE id = % s',(id, )) 
            account = cursor.fetchone() 
            if account: 
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
                msg = 'Invalid email address !'
            else: 
                cursor.execute('update usuarios SET nombres =%s, apellidos =%s, cedula =%s, email =%s,  telefono =%s,  password =%s WHERE id =%s',(nombres,apellidos,cedula, email, telefono, password,(session["id"], ), )) 
                mysql.connection.commit() 
                msg = 'Sus datos han sido actualizados !'
        elif request.method == 'POST': 
            msg = 'Please fill out the form !'
        return render_template("editar.html", msg = msg) 
    return redirect(url_for('home')) 

if __name__ == '__main__':
    app.run(debug=True)