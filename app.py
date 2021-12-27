from flask import Flask #importa flask
from flask import render_template, request,redirect, url_for, flash #importar para renderizar web y mandar datos y redireccionar a pagina
from flaskext.mysql import MySQL #para conexion a mysql
from flask import send_from_directory #permisos para accesar a directorio
from datetime import datetime #para formato de tiempo
import os 

app = Flask(__name__)
app.secret_key="Develoteca"

mysql = MySQL() #Conexion a bse de datos
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
#app.config['MySQL_DATABASE_PORT']='3306'
mysql.init_app(app)

CARPETA=os.path.join('uploads')
app.config['CARPETA']=CARPETA #variable para almacenar la ruta espeficifa de esa carpeta

#para mostrar foto
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto) #se accede a foto buscando su nombre

#rutas de consulta
@app.route('/')
def index():
    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect() #Conectarse  a la base de datos
    cursor = conn.cursor() #almacenare informacion
    cursor.execute(sql) #ejecutar dicha sentencia 

    empleados=cursor.fetchall() # toda la informacion que has obtenido, regresamela /selecciona todos los registros
    print(empleados) #muestrame los registros 
    

    conn.commit() #dar por echo que la sentencia fue exitosa

    return render_template('empleados/index.html', empleados=empleados) #enviar informacion a la vista index

#Ruta de eliminar
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    #Remover foto
    cursor.execute("SELECT foto FROM empleados WHERE id=%s",id) #instruccion de seleccion para seleccionar la foto, de la tabla empleados consultandoe le ID
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    #remover empleado
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id)) #borra los empleados cuando encuentres el ID que se envia en la URL
    conn.commit() 

    #redirecciona pagina principal
    return redirect('/')

#template de consulta de datos 
@app.route('/edit/<int:id>') #recepciona un entero de la variable edit
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `empleados` WHERE id=%s", (id))

    empleados=cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados) #mandar a redner la pagina de editar


@app.route('/update', methods=['POST'])
def update():
    #Recepcionar todos los datos
    _nombre=request.form['txtNombre'] 
    _correo=request.form['txtCorreo']
    _foto= request.files['txtFoto']
    id=request.form['txtID']
    
    #has el update de empleado el nombre le vas a poner el primer valor
    #al siguiente le vas poner el correo y se hara cuando encuentres el ID con el siguiente elemento o numero
    sql = "UPDATE empleados SET nombre=%s,correo=%s WHERE id=%s;"
    datos=(_nombre,_correo,id) #datos a cambiar
    
    conn = mysql.connect() #conectarse
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='': 
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
#consulta el contenido foto del registro
#se busca la foto a cambiar para poder removerla
        cursor.execute("SELECT foto FROM empleados WHERE id=%s",  id) #instruccion de seleccion para seleccionar la foto, de la tabla empleados consultandoe le ID
        fila=cursor.fetchall()

    #
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()


    cursor.execute(sql,datos) #se ejecuta la sentencia declarada 
    conn.commit()


    return redirect('/')


#ruda de crear y mostrar index 
@app.route('/create') #pagina para crear nuevo usuario
def create():
    return render_template('empleados/create.html') #renderiza la pagina de crear nuevo usuario

#ruta de guaradr
@app.route('/store', methods=['POST'])
def storage():
    #declara variable de los campos puestos en create.html
    _nombre=request.form['txtNombre'] 
    _correo=request.form['txtCorreo']
    _foto= request.files['txtFoto']

    if _nombre=='' or _correo=='' or _foto=='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S") #obtener formato del tiempo

    if _foto.filename!='': #si esa fotografia llega concatena el nombre del tiempo + nombre de la foto para evitar sobreescribir
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto) #despues se gurda la fot y se gurda en la carpeta

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s,%s,%s);"
    datos=(_nombre,_correo,nuevoNombreFoto)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/ ')



if __name__ == '__main__':
    app.run(debug=True) 

