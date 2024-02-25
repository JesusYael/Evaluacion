import hashlib
import sqlite3
import web
from web import form
from datetime import datetime



urls = (
    '/', 'Index',
    '/add_user', 'AddUser',
    '/assign_privilege', 'AssignPrivilege',
    '/view_privilegios', 'ViewPrivileges',  
    '/edit_user/(.*)', 'EditPrivileges',
    '/delete_user/(.*)', 'DeleteUser',
    '/consult','Consults',
)

# Conexión a la base de datos
db_path = 'db/privilegios.db'


render = web.template.render('templates/')

# Formularios
add_user_form = form.Form(
    form.Textbox('nombre_usuario', form.notnull, description="Nombre de Usuario:"),
    form.Password('contraseña', form.notnull, description="Contraseña:"),
    form.Dropdown('rol', [('usuario', 'Usuario'), ('administrador', 'Administrador')], description="Rol:"),
    form.Dropdown('status', [('activo', 'Activo'), ('inactivo', 'Inactivo')], description="Estado:"),
)

assign_privilege_form = form.Form(
    form.Dropdown('nombre_usuario', [],form.notnull, description="Nombre de Usuario:"),
    form.Dropdown('privilegio', [],form.notnull, description="Privilegio:"),
    form.Dropdown('tablas', [],form.notnull, description="Tablas:"),
)

edit_user_form = form.Form(
    form.Textbox('nombre_usuario', form.notnull, description="Nombre de Usuario:"),
    form.Dropdown('rol', [('usuario', 'Usuario'), ('administrador', 'Administrador')], description="Rol:"),
    form.Dropdown('status', [('activo', 'Activo'), ('inactivo', 'Inactivo')], description="Estado:"),
)

delete_user_form = form.Form(
    form.Password("password", form.notnull, description="Contraseña"),
    form.Checkbox("confirm", value="confirm", description="Confirmar eliminación"),
    validators=[form.Validator("Debe confirmar la eliminación.", lambda i: i.confirm == "confirm")]
    
)

consults_form = form.Form(
    form.Textbox('nombre_usuario', form.notnull, description="Nombre de Usuario:"),
    form.Password('contraseña', form.notnull, description="Contraseña:"),
    form.Textarea('consulta', form.notnull, description="Consulta"),
    form.Button('Ejecutar', type='submit'),
    form.Textarea('resultado',rows=10, cols=50, description="Resultado"),
)




class Index:
    def GET(self):
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("SELECT id_usuario,nombre_usuario, rol, status FROM usuarios")
        usuarios = cursor.fetchall()
        db.close()
        return render.index(usuarios)


class AddUser:
    def GET(self):
        form = add_user_form()
        return render.add_user(form)

    def POST(self):
        form = add_user_form()
        if not form.validates():
            return render.add_user(form)
        else:
            nombre_usuario = form.d.nombre_usuario
            contraseña = form.d.contraseña
            
            contraseña_hash = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
            rol = form.d.rol
            status = form.d.status
            fecha_creacion = datetime.now().strftime('%Y-%m-%d')
            
            
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            
            
            try:
                cur.execute("INSERT INTO usuarios (nombre_usuario, contraseña, rol, status, fecha_creacion) VALUES (?, ?, ?, ?, ?)", (nombre_usuario, contraseña_hash, rol, status, fecha_creacion))
                con.commit()
                mensaje = "Usuario agregado exitosamente."
            except sqlite3.IntegrityError:
                mensaje = "Error: No se pudo agregar el usuario. Es posible que el nombre de usuario ya exista."
            finally:
                con.close()

            raise web.seeother('/')

class AssignPrivilege:
    def GET(self):
        form = assign_privilege_form()
        
        db = sqlite3.connect(db_path)
        cursor = db.cursor()

        
        cursor.execute("SELECT id_usuario, nombre_usuario FROM usuarios")
        usuarios = [(str(row[0]), row[1]) for row in cursor.fetchall()]
        form.nombre_usuario.args = usuarios

        
        cursor.execute("SELECT id_privilegio, descripcion FROM privilegios")
        privilegios = [(str(row[0]), row[1]) for row in cursor.fetchall()]
        form.privilegio.args = privilegios

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'  AND name NOT IN ('sqlite_sequence', 'usuarios', 'privilegios', 'usuario_privilegios')")
        tables = [row[0] for row in cursor.fetchall()]
        form.tablas.args = tables

        db.close()  
        return render.assign_privilege(form)

    def POST(self):
        form = assign_privilege_form()
        if not form.validates():
            return render.assign_privilege(form)
        else:
            nombre_usuario = form.d.nombre_usuario
            privilegio = form.d.privilegio
            tabla = form.d.tablas
            

            db = sqlite3.connect(db_path)
            cursor = db.cursor()
            
            cursor.execute("INSERT INTO usuario_privilegios (id_usuario, id_privilegio, tabla) VALUES (?, ?, ?)", (nombre_usuario, privilegio,tabla,))
            db.commit()
            db.close()

            raise web.seeother('/')

class ViewPrivileges:
    def GET(self):
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row  
        cursor = db.cursor()

        cursor.execute('''
            SELECT u.nombre_usuario, p.descripcion, up.tabla
            FROM usuario_privilegios up
            JOIN usuarios u ON up.id_usuario = u.id_usuario
            JOIN privilegios p ON up.id_privilegio = p.id_privilegio
            ORDER BY u.nombre_usuario
        ''')
        
        usuarios_privilegios = cursor.fetchall()
        db.close()

        return render.view_privilegios(usuarios_privilegios)

class DeleteUser:
    def GET(self, id_usuario):
        form = delete_user_form()
        return render.delete_user(form, id_usuario) 

    def POST(self, id_usuario):
        form = delete_user_form()
        if not form.validates():
            return render.delete_user(form, id_usuario)
        
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        
        cursor.execute("SELECT contraseña FROM usuarios WHERE id_usuario=?", (id_usuario,))
        user_data = cursor.fetchone()
        print("Confirm:", form.d.confirm)
        
        if user_data and hashlib.sha256(form.d.password.encode('utf-8')).hexdigest() == user_data[0]:
            
            if 'confirm' in form.d and form.d.confirm:
                cursor.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
                cursor.execute("DELETE FROM usuario_privilegios WHERE id_usuario=?", (id_usuario,))
                db.commit()
                mensaje = "Usuario eliminado exitosamente."
            else:
                mensaje = "Debes confirmar la eliminación."
        else:
            mensaje = "Contraseña incorrecta o el usuario no existe."
        
        db.close()
        raise web.seeother('/')


class EditPrivileges:
    def GET(self, user_id):
        
        db = sqlite3.connect('db/privilegios.db')
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (user_id,))
        usuario = cur.fetchone()
        db.close()

        if usuario:
            
            edit_user_form = form.Form(
                form.Textbox('nombre_usuario', form.notnull, value=usuario['nombre_usuario'], description="Nombre de Usuario:"),
                form.Dropdown('rol', [('usuario', 'Usuario'), ('administrador', 'Administrador')], value=usuario['rol'], description="Rol:"),
                form.Dropdown('status', [('activo', 'Activo'), ('inactivo', 'Inactivo')], value=usuario['status'], description="Estado:"),
            )()

            
            return render.edit_user(edit_user_form, usuario)
        else:
            return "Usuario no encontrado"
    
    def POST(self, id_usuario):
        form = add_user_form()
        if not form.validates():
            return render.edit_user(form, id_usuario)
        else:
            nombre_usuario = form.d.nombre_usuario
           
            rol = form.d.rol
            status = form.d.status
            db = sqlite3.connect(db_path)
            cursor = db.cursor()
            cursor.execute("UPDATE usuarios SET nombre_usuario=?, rol=?, status=? WHERE id_usuario=?", 
                           (nombre_usuario, rol, status, id_usuario))
            db.commit()
            db.close()
            raise web.seeother('/')

class Consults:
    def __init__(self, usuario=None, contraseña=None, consulta=None, resultado=None):
        self.usuario = usuario
        self.contraseña = contraseña
        self.consulta = consulta
        self.resultado = resultado
    def GET(self):
        form = consults_form()
        return render.consults(form)
    def POST(self):
        a = consults_form()
        if not a.validates():
            return render.consults(a)
        else:
            contraseña = hashlib.sha256(a.d.contraseña.encode('utf-8')).hexdigest()
            consulta = Consults(a.d.nombre_usuario,contraseña, a.d.consulta, a.d.resultado)
            lista = []
            try: 
                db = sqlite3.connect(db_path)
                cursor = db.cursor()
                cursor.execute('''
                SELECT id_usuario,status FROM usuarios WHERE nombre_usuario = ?
                ''', (consulta.usuario,))
                user_data = cursor.fetchone()
                id_usuario = user_data[0]
                cursor.execute('''
                SELECT tabla FROM usuario_privilegios WHERE id_usuario = ?
                ''', (id_usuario,))
                tablas = cursor.fetchone()
                privilegio = a.d.consulta.split()[0].lower()
                cursor.execute('''
                SELECT 1 FROM usuario_privilegios UP
                JOIN usuarios U ON U.id_usuario = UP.id_usuario
                JOIN privilegios P ON P.id_privilegio = UP.id_privilegio
                WHERE U.nombre_usuario = ? AND U.contraseña = ? AND P.descripcion = ? AND U.status = 'activo' AND UP.tabla = ?
                ''', (consulta.usuario, consulta.contraseña,privilegio,tablas[0]))
                fetch_result = cursor.fetchone()
                print(fetch_result)
                consulta_lower = a.d.consulta.lower()
                if fetch_result == None:
                    consulta.resultado = "El usuario no tiene el privilegio para seleccionar productos o está inactivo."
                else:
                    try:
                        if consulta_lower.startswith("select"):
                            cursor.execute(a.d.consulta)
                            productos = cursor.fetchall()
                            if productos == []:
                                consulta.resultado = "No hay productos."
                            else:
                                for producto in productos:
                                    lista.append(producto)
                                consulta.resultado = lista
                        elif consulta_lower.startswith("update") or consulta_lower.startswith("insert") or consulta_lower.startswith("delete"):
                            cursor.execute(a.d.consulta)
                            db.commit()
                            consulta.resultado = "Consulta ejecutada correctamente."
                        else:
                            consulta.resultado = "Consulta no válida."
                    except Exception as e:
                        consulta.resultado = "Error al ejecutar la consulta: " + str(e)

                        
            except sqlite3.Error as e:
                print(f"Se produjo un error de base de datos: {e}")
            finally:
                if db:
                    db.close()

            results_form = form.Form(
                form.Textbox('nombre_usuario', form.notnull,value=consulta.usuario, description="Nombre de Usuario:"),
                form.Password('contraseña', form.notnull,value=a.d.contraseña, description="Contraseña:"),
                form.Textarea('consulta', form.notnull,value=consulta.consulta, description="Consulta"),
                form.Button('Ejecutar', type='submit'),
                form.Textarea('resultado',value=consulta.resultado,rows=10, cols=50, description="Resultado"),
            )
            return render.consults(results_form)
                    
        






if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
