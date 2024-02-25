import sqlite3
from datetime import datetime

def add_usuario(nombre_usuario, contraseña, rol, status='activo'):
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    INSERT INTO usuarios (nombre_usuario, contraseña, rol, status, fecha_creacion) 
    VALUES (?, ?, ?, ?, ?)
    ''', (nombre_usuario, contraseña, rol, status, fecha_creacion))
    conexión.commit()
    conexión.close()

def add_privilegio(descripcion):
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    INSERT INTO privilegios (descripcion) VALUES (?)
    ''', (descripcion,))
    conexión.commit()
    conexión.close()

def add_usuario_privilegio(nombre_usuario, descripcion_privilegio):
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    
    # Obtener el ID del usuario
    cur.execute('SELECT id_usuario FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
    id_usuario = cur.fetchone()[0]
    
    # Obtener el ID del privilegio
    cur.execute('SELECT id_privilegio FROM privilegios WHERE descripcion = ?', (descripcion_privilegio,))
    id_privilegio = cur.fetchone()[0]
    
    # Asociar usuario con privilegio
    cur.execute('''
    INSERT INTO usuario_privilegios (id_usuario, id_privilegio) VALUES (?, ?)
    ''', (id_usuario, id_privilegio))
    conexión.commit()
    conexión.close()

def add_producto(nombre_usuario, nombre, descripcion, precio):
    try:
        conexion = sqlite3.connect('db/privilegios.db')
        cur = conexion.cursor()
        
        # Verificar si el usuario tiene el privilegio para añadir productos y si está activo
        cur.execute('''
        SELECT p.descripcion FROM usuario_privilegios UP
        JOIN usuarios U ON U.id_usuario = UP.id_usuario
        JOIN privilegios P ON P.id_privilegio = UP.id_privilegio
        WHERE U.nombre_usuario = ? AND P.descripcion = 'insertar' AND U.status = 'activo'
        ''', (nombre_usuario,))
        
        if cur.fetchone():
            # El usuario tiene el privilegio y está activo, proceder a añadir el producto
            cur.execute('''
            INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?)
            ''', (nombre, descripcion, precio))
            conexion.commit()
            print("Producto añadido correctamente.")
        else:
            print("El usuario no tiene el privilegio para añadir productos o está inactivo.")
    except sqlite3.Error as e:
        print(f"Se produjo un error de base de datos: {e}")
    finally:
        # Asegurarse de que la conexión se cierre siempre
        if conexion:
            conexion.close()

def update_producto(nombre_usuario, id_producto, nuevo_nombre, nueva_descripcion, nuevo_precio):
    try:
        conexion = sqlite3.connect('db/privilegios.db')
        cur = conexion.cursor()

        # Verificar privilegios y estado del usuario
        cur.execute('''
        SELECT 1 FROM usuario_privilegios UP
        JOIN usuarios U ON U.id_usuario = UP.id_usuario
        JOIN privilegios P ON P.id_privilegio = UP.id_privilegio
        WHERE U.nombre_usuario = ? AND P.descripcion = 'actualizar' AND U.status = 'activo'
        ''', (nombre_usuario,))

        if cur.fetchone():
            # Actualizar producto
            cur.execute('''
            UPDATE productos SET nombre = ?, descripcion = ?, precio = ? WHERE id_producto = ?
            ''', (nuevo_nombre, nueva_descripcion, nuevo_precio, id_producto))
            conexion.commit()
            print("Producto actualizado correctamente.")
        else:
            print("El usuario no tiene el privilegio para actualizar productos o está inactivo.")
    except sqlite3.Error as e:
        print(f"Se produjo un error de base de datos: {e}")
    finally:
        if conexion:
            conexion.close()


def select_productos(nombre_usuario):
    try:
        conexion = sqlite3.connect('db/privilegios.db')
        cur = conexion.cursor()

        # Verificar privilegios y estado del usuario
        cur.execute('''
        SELECT 1 FROM usuario_privilegios UP
        JOIN usuarios U ON U.id_usuario = UP.id_usuario
        JOIN privilegios P ON P.id_privilegio = UP.id_privilegio
        WHERE U.nombre_usuario = ? AND P.descripcion = 'select' AND U.status = 'activo'
        ''', (nombre_usuario,))

        if cur.fetchone():
            # Seleccionar productos
            cur.execute('SELECT * FROM productos')
            productos = cur.fetchall()
            for producto in productos:
                print(producto)
        else:
            print("El usuario no tiene el privilegio para seleccionar productos o está inactivo.")
    except sqlite3.Error as e:
        print(f"Se produjo un error de base de datos: {e}")
    finally:
        if conexion:
            conexion.close()


def delete_producto(nombre_usuario, id_producto):
    try:
        conexion = sqlite3.connect('db/privilegios.db')
        cur = conexion.cursor()

        # Verificar privilegios y estado del usuario
        cur.execute('''
        SELECT 1 FROM usuario_privilegios UP
        JOIN usuarios U ON U.id_usuario = UP.id_usuario
        JOIN privilegios P ON P.id_privilegio = UP.id_privilegio
        WHERE U.nombre_usuario = ? AND P.descripcion = 'eliminar' AND U.status = 'activo'
        ''', (nombre_usuario,))

        if cur.fetchone():
            # Eliminar producto
            cur.execute('DELETE FROM productos WHERE id_producto = ?', (id_producto,))
            conexion.commit()
            print("Producto eliminado correctamente.")
        else:
            print("El usuario no tiene el privilegio para eliminar productos o está inactivo.")
    except sqlite3.Error as e:
        print(f"Se produjo un error de base de datos: {e}")
    finally:
        if conexion:
            conexion.close()


# Ejemplo de uso
add_privilegio('insert')
add_privilegio('select')
add_privilegio('update')
add_privilegio('delete')
