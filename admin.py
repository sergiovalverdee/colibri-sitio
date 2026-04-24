import streamlit as st
from bs4 import BeautifulSoup
import sqlite3
import os
import hashlib
import json
import pandas as pd # Añadimos esta para manejar la lista de usuarios
from streamlit_lottie import st_lottie
import git 

# --- FUNCIONES DE BASE DE DATOS ---

def eliminar_usuario(usuario_a_borrar):
    try:
        conn = sqlite3.connect('colibri_cafe.db')
        curr = conn.cursor()
        curr.execute("DELETE FROM usuarios WHERE usuario=?", (usuario_a_borrar,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False

# (Mantenemos tus funciones anteriores igual...)
def subir_a_github():
    try:
        ssh_path = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_path): os.makedirs(ssh_path)
        key_file = os.path.join(ssh_path, "id_ed25519")
        with open(key_file, "w") as f: f.write(st.secrets["git"]["ssh_key"])
        os.chmod(key_file, 0o600)
        repo = git.Repo(".")
        url_ssh = "git@github.com:sergiovalverdee/colibri-sitio.git"
        if 'origin' in repo.remotes:
            origin = repo.remote(name='origin')
            origin.set_url(url_ssh)
        else: origin = repo.create_remote('origin', url_ssh)
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "sergiovalverdee")
            cw.set_value("user", "email", "sergiovalverde171206@gmail.com")
        repo.git.add("index.html")
        repo.git.add("colibri_cafe.db")
        repo.git.add("static/assets/images/*")
        if repo.is_dirty(untracked_files=True):
            repo.index.commit("Actualización profesional vía SSH ☕")
            with repo.git.custom_environment(GIT_SSH_COMMAND=f'ssh -i {key_file} -o StrictHostKeyChecking=no'):
                origin.push()
        return True
    except Exception as e:
        st.error(f"Error de conexión SSH: {e}")
        return False

CARPETA_IMAGENES = "static/assets/images/"

def verificar_login(usuario, password):
    conn = sqlite3.connect('colibri_cafe.db')
    curr = conn.cursor()
    pw_encriptada = hashlib.sha256(password.encode()).hexdigest()
    curr.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (usuario, pw_encriptada))
    resultado = curr.fetchone()
    conn.close()
    return resultado

def registrar_nuevo_usuario(nuevo_usuario, nueva_password):
    try:
        conn = sqlite3.connect('colibri_cafe.db')
        curr = conn.cursor()
        pw_encriptada = hashlib.sha256(nueva_password.encode()).hexdigest()
        curr.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (nuevo_usuario, pw_encriptada))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError: return False 

def guardar_en_db(cat, nom, desc, pre, img):
    conn = sqlite3.connect('colibri_cafe.db')
    curr = conn.cursor()
    curr.execute('UPDATE recomendaciones SET nombre=?, descripcion=?, precio=?, imagen_url=? WHERE categoria=?', (nom, desc, pre, img, cat))
    conn.commit()
    conn.close()

def actualizar_html(cat, nom, desc, pre, img):
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    if soup.find(id=f"nombre-{cat}"):
        soup.find(id=f"nombre-{cat}").string = nom
        soup.find(id=f"desc-{cat}").string = desc
        soup.find(id=f"precio-{cat}").string = f"${pre}"
        soup.find(id=f"img-{cat}")['src'] = f"static/assets/images/{img}"
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(soup.encode(formatter=None).decode("utf-8"))
        return True
    return False

# --- LÓGICA DE INTERFAZ ---
st.set_page_config(page_title="Admin Colibrí", page_icon="☕", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    # (Tu CSS de login se queda igual...)
    st.markdown("""<style>.stApp { background-color: #0e1117; } [data-testid="stForm"] { width: 90%; max-width: 400px; margin: 80px auto; padding: 40px; border-radius: 20px; border: 1px solid #333; background-color: #111; box-shadow: 0px 15px 40px rgba(0,0,0,0.8); } h1 { text-align: center; color: #d4af37; font-size: 2rem !important; } .stButton > button { width: 100%; background-color: #d4af37; color: black !important; font-weight: bold; border-radius: 10px; height: 3.5em; border: none; } #MainMenu, header, footer { visibility: hidden; }</style>""", unsafe_allow_html=True)
    st.title("☕ Colibrí Café Admin")
    with st.form("login_form"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if verificar_login(user_input, pass_input):
                st.session_state['autenticado'] = True
                st.session_state['usuario_actual'] = user_input # Guardamos quién entró
                st.rerun()
            else: st.error("Error")
else:
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Ir a:", ["Ver Sitio Web", "Actualizar Menú", "Gestionar Usuarios"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    if menu == "Ver Sitio Web":
        st.title("Vista Previa del Sitio")
        url_real = "https://sergiovalverdee.github.io/colibri-sitio/"
        st.components.v1.iframe(url_real, height=900, scrolling=True)

    elif menu == "Actualizar Menú":
        st.title("Gestión de Contenido")
        col1, col2 = st.columns([2, 1]) 
        with col1:
            opciones = {"Plato Fuerte": "plato", "Bebida": "bebida", "Postre": "postre"}
            seleccion = st.selectbox("Sección:", list(opciones.keys()))
            cat_key = opciones[seleccion]
            with st.form(key=f"form_{cat_key}"):
                nom = st.text_input("Nombre")
                desc = st.text_area("Descripción")
                pre = st.number_input("Precio", min_value=0.0)
                foto = st.file_uploader("Imagen", type=['jpg', 'png', 'jpeg'])
                if st.form_submit_button("¡Actualizar Todo!"):
                    if foto:
                        if not os.path.exists(CARPETA_IMAGENES): os.makedirs(CARPETA_IMAGENES)
                        with open(os.path.join(CARPETA_IMAGENES, foto.name), "wb") as f: f.write(foto.getbuffer())
                        guardar_en_db(cat_key, nom, desc, pre, foto.name)
                        if actualizar_html(cat_key, nom, desc, pre, foto.name):
                            with st.spinner('Sincronizando...'):
                                if subir_a_github():
                                    st.session_state['mostrar_animacion'] = True
                                    st.rerun()

        with col2:
            if 'mostrar_animacion' in st.session_state and st.session_state['mostrar_animacion']:
                try:
                    lottie_url = "https://assets1.lottiefiles.com/packages/lf20_at45id.json"
                    st_lottie(lottie_url, height=250, key="success_anim", loop=False)
                except: st.balloons()
                st.success("¡Éxito! ☕")
                st.session_state['mostrar_animacion'] = False

    elif menu == "Gestionar Usuarios":
        st.title("Gestión de Administradores")
        
        # --- PARTE 1: REGISTRO ---
        with st.expander("➕ Crear Nuevo Usuario"):
            with st.form("registro_form"):
                nuevo_user = st.text_input("Usuario")
                nuevo_pass = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Registrar"):
                    if registrar_nuevo_usuario(nuevo_user, nuevo_pass):
                        st.success("¡Creado!")
                        subir_a_github()
                        st.rerun()
        
        st.divider()

        # --- PARTE 2: ELIMINACIÓN (Diseño Alineado) ---
        st.subheader("Usuarios con acceso al sistema")
        
        conn = sqlite3.connect('colibri_cafe.db')
        df_users = pd.read_sql_query("SELECT usuario FROM usuarios", conn)
        conn.close()

        # Usamos un contenedor para mejor organización visual
        with st.container():
            for u in df_users['usuario']:
                # Ajustamos columnas: Nombre (6), Espacio (2), Botón (2)
                col_info, col_vacia, col_accion = st.columns([6, 2, 2])
                
                with col_info:
                    st.markdown(f"### 👤 {u}")
                
                with col_accion:
                    if u == st.session_state.get('usuario_actual'):
                        st.info("Tu sesión")
                    else:
                        # use_container_width=True hace que el botón llene su columna y se vea alineado
                        if st.button("Eliminar", key=f"btn_{u}", use_container_width=True):
                            if eliminar_usuario(u):
                                with st.spinner('Sincronizando cambios...'):
                                    subir_a_github()
                                st.rerun()
                st.divider() # Línea de separación entre cada fila de usuario