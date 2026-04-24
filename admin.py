import streamlit as st
from bs4 import BeautifulSoup
import sqlite3
import os
import hashlib
import json
from streamlit_lottie import st_lottie
import git 

# --- FUNCIÓN PARA SINCRONIZAR CON GITHUB ---
def subir_a_github():
    try:
        # 1. Configurar la llave SSH en el servidor de Streamlit
        ssh_path = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_path):
            os.makedirs(ssh_path)
            
        key_file = os.path.join(ssh_path, "id_ed25519")
        
        # Leemos la llave desde los Secrets que configuramos
        with open(key_file, "w") as f:
            f.write(st.secrets["git"]["ssh_key"])
        
        # Permisos necesarios para que Git acepte la llave
        os.chmod(key_file, 0o600)

        # 2. Inicializar el repositorio y cambiar a URL de SSH
        repo = git.Repo(".")
        url_ssh = "git@github.com:sergiovalverdee/colibri-sitio.git"
        
        if 'origin' in repo.remotes:
            origin = repo.remote(name='origin')
            origin.set_url(url_ssh)
        else:
            origin = repo.create_remote('origin', url_ssh)

        # 3. Configurar tu identidad para el commit
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "sergiovalverdee")
            cw.set_value("user", "email", "sergiovalverde171206@gmail.com")

        # 4. Preparar y subir los cambios
        repo.git.add("index.html")
        repo.git.add("colibri_cafe.db")
        repo.git.add("static/assets/images/*")
        
        # Verificamos si hay algo que commitear para evitar errores
        if repo.is_dirty(untracked_files=True):
            repo.index.commit("Actualización profesional vía SSH ☕")
            
            # El comando 'ssh -o StrictHostKeyChecking=no' es para que no 
            # se detenga preguntando si confía en GitHub
            with repo.git.custom_environment(GIT_SSH_COMMAND=f'ssh -i {key_file} -o StrictHostKeyChecking=no'):
                origin.push()
        
        return True
    except Exception as e:
        st.error(f"Error de conexión SSH: {e}")
        return False
# Configuración básica
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
    except sqlite3.IntegrityError:
        return False 

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

# --- LÓGICA DE LA INTERFAZ ---
st.set_page_config(page_title="Admin Colibrí", page_icon="☕", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        [data-testid="stForm"] {
            width: 90%; max-width: 400px; margin: 80px auto; padding: 40px;
            border-radius: 20px; border: 1px solid #333; background-color: #111;
            box-shadow: 0px 15px 40px rgba(0,0,0,0.8);
        }
        h1 { text-align: center; color: #d4af37; font-size: 2rem !important; }
        .stButton > button {
            width: 100%; background-color: #d4af37; color: black !important;
            font-weight: bold; border-radius: 10px; height: 3.5em; border: none;
        }
        #MainMenu, header, footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.title("☕ Colibrí Café Admin")
    with st.form("login_form"):
        user_input = st.text_input("Usuario", placeholder="Tu usuario...")
        pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
        if st.form_submit_button("Entrar al Panel"):
            if verificar_login(user_input, pass_input):
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- PANEL DE ADMINISTRACIÓN ---
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Ir a:", ["Ver Sitio Web", "Actualizar Menú", "Gestionar Usuarios"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    if menu == "Ver Sitio Web":
        st.title("Vista Previa del Sitio")
        
        # Usamos la URL real de tu sitio en GitHub Pages
        url_real = "https://sergiovalverdee.github.io/colibri-sitio/"
        
        # Esto inserta tu página web real dentro del panel
        st.components.v1.iframe(url_real, height=900, scrolling=True)
        
        st.info("💡 Esta es la versión en vivo de tu sitio. Los cambios pueden tardar 1-2 minutos en aparecer tras actualizar.")
    elif menu == "Actualizar Menú":
        st.title("Gestión de Contenido")
        col1, col2 = st.columns([2, 1]) 

        with col1:
            opciones = {"Plato Fuerte": "plato", "Bebida": "bebida", "Postre": "postre"}
            seleccion = st.selectbox("Sección a editar:", list(opciones.keys()))
            cat_key = opciones[seleccion]

            with st.form(key=f"form_{cat_key}"):
                st.subheader(f"Editando: {seleccion}")
                nom = st.text_input("Nombre del Producto")
                desc = st.text_area("Descripción")
                pre = st.number_input("Precio", min_value=0.0)
                foto = st.file_uploader("Imagen", type=['jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("¡Actualizar Todo!"):
                    if foto:
                        if not os.path.exists(CARPETA_IMAGENES):
                            os.makedirs(CARPETA_IMAGENES)
                        with open(os.path.join(CARPETA_IMAGENES, foto.name), "wb") as f:
                            f.write(foto.getbuffer())
                        
                        # 1. Guardar en DB
                        guardar_en_db(cat_key, nom, desc, pre, foto.name)
                        
                        # 2. Actualizar el HTML local
                        if actualizar_html(cat_key, nom, desc, pre, foto.name):
                            # 3. SINCRONIZAR CON GITHUB (Para que el link cambie)
                            with st.spinner('Sincronizando cambios con el servidor...'):
                                if subir_a_github():
                                    st.session_state['mostrar_animacion'] = True
                                    st.rerun()
                        else:
                            st.error("Error al actualizar HTML.")
                    else:
                        st.warning("Sube una foto.")
        
        with col2:
            if 'mostrar_animacion' in st.session_state and st.session_state['mostrar_animacion']:
                # Intentamos cargar la animación de Lottie
                try:
                    lottie_url = "https://assets1.lottiefiles.com/packages/lf20_at45id.json"
                    st_lottie(lottie_url, height=250, key="success_anim", loop=False)
                except Exception:
                    # Si falla Lottie, lanzamos globos para que no se vea vacío
                    st.balloons()
                
                # Mensaje de éxito siempre visible
                st.success("¡Sincronizado con GitHub con éxito! ☕")
                st.session_state['mostrar_animacion'] = False

    elif menu == "Gestionar Usuarios":
        st.title("Registrar Nuevo Administrador")
        with st.form("registro_form"):
            nuevo_user = st.text_input("Nuevo Nombre de Usuario")
            nuevo_pass = st.text_input("Nueva Contraseña", type="password")
            confirm_pass = st.text_input("Confirmar Contraseña", type="password")
            if st.form_submit_button("Crear Superusuario"):
                if nuevo_pass != confirm_pass:
                    st.error("Las contraseñas no coinciden")
                else:
                    if registrar_nuevo_usuario(nuevo_user, nuevo_pass):
                        st.success(f"¡Usuario '{nuevo_user}' creado!")
                        subir_a_github() # Guardamos la nueva DB en GitHub
                    else:
                        st.error("Ese usuario ya existe.")