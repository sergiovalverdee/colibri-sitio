import sqlite3
import hashlib # Para proteger las contraseñas

def crear_tabla_usuarios():
    conn = sqlite3.connect('colibri_cafe.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # Creamos un superusuario por defecto si no existe (Usuario: admin, Clave: colibri123)
    # Encriptamos la clave por seguridad
    pw_encriptada = hashlib.sha256("colibri123".encode()).hexdigest()
    cursor.execute('INSERT OR IGNORE INTO usuarios VALUES (?, ?)', ("admin", pw_encriptada))
    
    conn.commit()
    conn.close()

crear_tabla_usuarios()
print("Tabla de usuarios lista.")

def inicializar_db():
    conn = sqlite3.connect('colibri_cafe.db')
    cursor = conn.cursor()
    # Creamos la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recomendaciones (
            categoria TEXT PRIMARY KEY, 
            nombre TEXT,
            descripcion TEXT,
            precio REAL,
            imagen_url TEXT
        )
    ''')
    # Insertamos los 3 espacios vacíos iniciales para evitar errores
    categorias = [('plato',), ('bebida',), ('postre',)]
    cursor.executemany('INSERT OR IGNORE INTO recomendaciones (categoria) VALUES (?)', categorias)
    
    conn.commit()
    conn.close()
    print("Base de datos 'colibri_cafe.db' creada y lista.")

if __name__ == "__main__":
    inicializar_db()