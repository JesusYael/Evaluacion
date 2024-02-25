import sqlite3

def creatablaUsuarios():
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL,
    rol TEXT NOT NULL,
    status TEXT NOT NULL,
    fecha_creacion DATE NOT NULL
    );
    ''')
    conexión.commit()
    result = cur.fetchall()
    conexión.close()
    return result

def creatablaPrivilegios():
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    CREATE TABLE privilegios (
    id_privilegio INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL
    );
    ''')
    conexión.commit()
    result = cur.fetchall()
    conexión.close()
    return result

def creatablaUsuarios_Privilegios():
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    CREATE TABLE usuario_privilegios (
    id_usuario INTEGER,
    id_privilegio INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario),
    FOREIGN KEY (id_privilegio) REFERENCES privilegios (id_privilegio),
    PRIMARY KEY (id_usuario, id_privilegio)
    );
    ''')
    conexión.commit()
    result = cur.fetchall()
    conexión.close()
    return result

def creatablaProductos():
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL
    );
    ''')
    conexión.commit()
    result = cur.fetchall()
    conexión.close()
    return result

def creatablaPedidos():
    conexión = sqlite3.connect('db/privilegios.db')
    cur = conexión.cursor()
    cur.execute('''
    CREATE TABLE pedidos (
    id_pedidos INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    direccion TEXT NOT NULL
    );
    ''')
    conexión.commit()
    result = cur.fetchall()
    conexión.close()
    return result


'insertar_privilegios()'
'creatablaUsuarios()'
'creatablaPrivilegios()'
'creatablaUsuarios_Privilegios()'
'creatablaProductos()'
'creatablaPedidos()'




