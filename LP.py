# #=========================================================
#IMPORTACIONES
#=========================================================

import flet as ft
import sqlite3
import requests


# =========================================
# RETROALIMENTACIÓN POR NIVEL
# =========================================

def obtener_retroalimentacion(materia, nivel, puntaje):

    mensajes = {
        "Matemáticas": {
            "Fácil": "Debes practicar más operaciones básicas y leer cuidadosamente cada ejercicio antes de responder.",

            "Medio": "Necesitas reforzar resolución de problemas y aplicar fórmulas con más precisión.",

            "Difícil": "Te conviene practicar ejercicios avanzados y mejorar tu razonamiento lógico paso a paso."
        },

        "Ciencias": {
            "Fácil": "Debes reforzar conceptos básicos y leer más teoría.",

            "Medio": "Necesitas practicar análisis y comprensión de procesos científicos.",

            "Difícil": "Debes mejorar tu razonamiento crítico y resolución avanzada."
        }
    }

    if materia in mensajes and nivel in mensajes[materia]:
        return mensajes[materia][nivel]

    return "Sigue practicando y revisa los temas donde cometiste más errores."


# =========================================
# CERRAR DIÁLOGO
# =========================================

def cerrar_dialogo(page, dialogo):

    dialogo.open = False
    page.update()


# =========================================
# MOSTRAR RETROALIMENTACIÓN
# =========================================

def mostrar_retroalimentacion(page, materia, nivel, puntaje):

    mensaje = obtener_retroalimentacion(
        materia,
        nivel,
        puntaje
    )

    dialogo = ft.AlertDialog(

        modal=True,

        title=ft.Text(
            "¿Qué debes mejorar?",
            size=22,
            weight="bold"
        ),

        content=ft.Text(
            mensaje,
            size=16
        ),

        actions=[

            ft.TextButton(

                "Entendido",

                on_click=lambda e: cerrar_dialogo(
                    page,
                    dialogo
                )
            )

        ]
    )

    page.dialog = dialogo

    dialogo.open = True

    page.update()


# =========================================================
# BASE DE DATOS SQLITE
# =========================================================

conexion = sqlite3.connect(
    "learning.db",
    check_same_thread=False
)

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    password TEXT

)
""")

conexion.commit()


# =========================================================
# CLASE PRINCIPAL
# =========================================================

class LandingPage:

    def __init__(self, page: ft.Page):

        self.page = page

        # =================================================
        # CONFIGURACIÓN
        # =================================================

        self.page.title = "Learning To Fly"
        self.page.bgcolor = "#f1f5f2"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.primary = "#1B5E20"
        self.section_bg = "#E8F5E9"
        self.card_color = "#FFFFFF"
        self.text_dark = "#1c1c1c"
        self.text_soft = "#4b5563"

        # =================================================
        # VARIABLE UPDATE
        # =================================================

        self.usuario_editar = None

        # =================================================
        # CAMPOS LOGIN
        # =================================================

        self.login_correo = ft.TextField(
            label="Correo",
            width=320,
            on_submit=None
        )

        self.login_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            on_submit=None
        )

        # =================================================
        # CAMPOS REGISTRO
        # =================================================

        self.reg_nombre = ft.TextField(
            label="Nombre",
            width=320,
            on_submit=None
        )

        self.reg_correo = ft.TextField(
            label="Correo",
            width=320,
            on_submit=None
        )

        self.reg_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=320,
            on_submit=None
        )

        # =================================================
        # LISTA USUARIOS
        # =================================================

        self.lista_usuarios = ft.Column()

        self.build()

    # =====================================================
    # MENSAJES
    # =====================================================

    def mensaje(self, texto):

        self.page.snack_bar = ft.SnackBar(
            ft.Text(texto)
        )

        self.page.snack_bar.open = True

        self.page.update()

    # =====================================================
    # CREATE
    # =====================================================

    def registrar_usuario(self, e):

        nombre = self.reg_nombre.value
        correo = self.reg_correo.value
        password = self.reg_password.value

        if nombre == "" or correo == "" or password == "":

            self.mensaje("Completa todos los campos")
            return

        cursor.execute(
            "INSERT INTO usuarios(nombre, correo, password) VALUES(?,?,?)",
            (nombre, correo, password)
        )

        conexion.commit()

        self.reg_nombre.value = ""
        self.reg_correo.value = ""
        self.reg_password.value = ""

        self.mensaje("Usuario registrado correctamente")

        self.mostrar_usuarios()

    # =====================================================
    # READ
    # =====================================================

    def mostrar_usuarios(self):

        self.lista_usuarios.controls.clear()

        cursor.execute("SELECT * FROM usuarios")

        usuarios = cursor.fetchall()

        for usuario in usuarios:

            self.lista_usuarios.controls.append(

                ft.Container(

                    bgcolor="white",
                    padding=15,
                    border_radius=10,
                    margin=5,

                    content=ft.Row(

                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                        controls=[

                            ft.Column(

                                spacing=2,

                                controls=[

                                    ft.Text(
                                        f"Nombre: {usuario[1]}",
                                        color="black",
                                        weight="bold"
                                    ),

                                    ft.Text(
                                        f"Correo: {usuario[2]}",
                                        color="black"
                                    )
                                ]
                            ),

                            ft.Row(

                                controls=[

                                    # EDITAR

                                    ft.IconButton(

                                        icon=ft.Icons.EDIT,
                                        icon_color="blue",

                                        on_click=lambda e,
                                        id_usuario=usuario[0],
                                        nombre=usuario[1],
                                        correo=usuario[2],
                                        password=usuario[3]:

                                        self.cargar_usuario(
                                            id_usuario,
                                            nombre,
                                            correo,
                                            password
                                        )
                                    ),

                                    # ELIMINAR

                                    ft.IconButton(

                                        icon=ft.Icons.DELETE,
                                        icon_color="red",

                                        on_click=lambda e,
                                        id_usuario=usuario[0]:

                                        self.eliminar_usuario(
                                            id_usuario
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
            )

        self.page.update()

    # =====================================================
    # CARGAR DATOS PARA EDITAR
    # =====================================================

    def cargar_usuario(self, id_usuario, nombre, correo, password):

        self.usuario_editar = id_usuario

        self.reg_nombre.value = nombre
        self.reg_correo.value = correo
        self.reg_password.value = password

        self.page.update()

    # =====================================================
    # UPDATE
    # =====================================================

    def actualizar_usuario(self, e):

        if self.usuario_editar is None:

            self.mensaje("Selecciona un usuario")
            return

        nombre = self.reg_nombre.value
        correo = self.reg_correo.value
        password = self.reg_password.value

        cursor.execute(
            """
            UPDATE usuarios
            SET nombre=?, correo=?, password=?
            WHERE id=?
            """,
            (
                nombre,
                correo,
                password,
                self.usuario_editar
            )
        )

        conexion.commit()

        self.usuario_editar = None

        self.reg_nombre.value = ""
        self.reg_correo.value = ""
        self.reg_password.value = ""

        self.mensaje("Usuario actualizado")

        self.mostrar_usuarios()

    # =====================================================
    # DELETE
    # =====================================================

    def eliminar_usuario(self, id_usuario):

        cursor.execute(
            "DELETE FROM usuarios WHERE id=?",
            (id_usuario,)
        )

        conexion.commit()

        self.mensaje("Usuario eliminado")

        self.mostrar_usuarios()

    # =====================================================
    # LOGIN
    # =====================================================

    def login(self, e):

        correo = self.login_correo.value
        password = self.login_password.value

        cursor.execute(
            "SELECT * FROM usuarios WHERE correo=? AND password=?",
            (correo, password)
        )

        usuario = cursor.fetchone()

        if usuario:
            
            self.page.clean()


            self.abrir_dashboard(usuario[1])

        else:

            self.mensaje("Datos incorrectos")


    # =====================================================
    # ABRIR PREGUNTAS
    # =====================================================

    def abrir_preguntas(self, materia, nivel, nombre_usuario="Usuario"):

        if nivel is None:

            self.mensaje("Selecciona un nivel")
            return

        materia_api = materia.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace(" ","_")

        nivel_api = nivel.lower().replace(" ","_")

        url = f"http://127.0.0.1:5000/{materia_api}/{nivel_api}"

        respuesta = requests.get(url)

        datos = respuesta.json()

        preguntas = datos["preguntas"]

        # Activar scroll en la página
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20
        self.page.clean()

        campos_respuesta = []

        resultado_texto = ft.Text(
            "",
            size=20,
            weight="bold",
            text_align=ft.TextAlign.CENTER,
            color="white"
        )

        resultado_container = ft.Container(
            visible=False,
            width=600,
            padding=20,
            border_radius=12,
            margin=10,
            content=resultado_texto
        )

        def verificar_respuestas(e):

            correctas = 0
            total = len(campos_respuesta)

            for item in campos_respuesta:

                respuesta_usuario = item["campo"].value.strip().lower()
                respuesta_correcta = item["correcta"].strip().lower()

                if respuesta_usuario == respuesta_correcta:
                    correctas += 1

            # =========================================
            # SI GANA
            # =========================================

            if correctas > 2:

                resultado_container.bgcolor = "#1B5E20"

                resultado_container.content = ft.Text(

                    f"¡Felicidades! Respondiste {correctas} de {total} correctamente.\n"
                    f"¡PASAS al siguiente nivel!",

                    size=20,
                    weight="bold",
                    text_align=ft.TextAlign.CENTER,
                    color="white"
                )

            # =========================================
            # SI PIERDE
            # =========================================

            else:

                recomendacion = ""

                if nivel == "Nivel 1":

                    recomendacion = (
                        "Debes mejorar operaciones básicas, "
                        "sumas, restas y multiplicaciones."
                    )

                elif nivel == "Nivel 2":

                    recomendacion = (
                        "Debes practicar fracciones, "
                        "problemas matemáticos y análisis."
                    )

                elif nivel == "Nivel 3":

                    recomendacion = (
                        "Necesitas reforzar álgebra, "
                        "lógica matemática y razonamiento."
                    )

                else:

                    recomendacion = (
                        "Debes seguir practicando."
                    )

                resultado_container.bgcolor = "#B71C1C"

                resultado_container.content = ft.Column(

                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                    controls=[

                        ft.Text(

                            f"Respondiste {correctas} de {total} correctamente.\n"
                            f"No pasas al siguiente nivel.",

                            size=20,
                            weight="bold",
                            text_align=ft.TextAlign.CENTER,
                            color="white"
                        ),

                        ft.Container(height=10),

                        ft.Text(

                            f"Retroalimentación:\n{recomendacion}",

                            size=16,
                            text_align=ft.TextAlign.CENTER,
                            color="white"
                        )
                    ]
                )

            resultado_container.visible = True

            self.page.update()

        # Título
        self.page.add(

            ft.Container(
                alignment=ft.alignment.Alignment(0, 0),
                padding=10,
                content=ft.Text(
                    f"{materia} - {nivel}",
                    size=30,
                    weight="bold",
                    color="black",
                    text_align=ft.TextAlign.CENTER
                )
            )
        )

        # Preguntas una por una
        for i, pregunta in enumerate(preguntas):

            campo = ft.TextField(
                label="Tu respuesta",
                width=500,
                on_submit=None
            )

            campos_respuesta.append({
                "campo": campo,
                "correcta": pregunta["respuesta"]
            })

            self.page.add(

                ft.Container(
                    alignment=ft.alignment.Alignment(0, 0),
                    content=ft.Container(
                        bgcolor="white",
                        padding=25,
                        border_radius=12,
                        margin=10,
                        width=600,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    f"Pregunta {i + 1}: {pregunta['pregunta']}",
                                    size=20,
                                    weight="bold",
                                    color="black",
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Container(height=10),
                                campo
                            ]
                        )
                    )
                )
            )

        # Botón ver resultados
        self.page.add(

            ft.Container(
                alignment=ft.alignment.Alignment(0, 0),
                margin=10,
                content=ft.ElevatedButton(
                    "Ver resultados",
                    bgcolor="#1B5E20",
                    color="white",
                    width=300,
                    height=50,
                    on_click=verificar_respuestas
                )
            )
        )

        # Contenedor resultado
        self.page.add(

            ft.Container(
                alignment=ft.alignment.Alignment(0, 0),
                content=resultado_container
            )
        )

        # Botón volver
        self.page.add(

            ft.Container(
                alignment=ft.alignment.Alignment(0, 0),
                margin=10,
                content=ft.ElevatedButton(
                    "Volver al dashboard",
                    width=300,
                    height=45,
                    on_click=lambda e, n=nombre_usuario:
                        self.abrir_dashboard(n)
                )
            )
        )

        self.page.add(ft.Container(height=40))

        self.page.update()

    

    # =====================================================
    # DASHBOARD
    # =====================================================

    def abrir_dashboard(self, nombre_usuario):

        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0
        self.page.clean()

        self.page.add(

            ft.Container(

                expand=True,

                bgcolor="#f1f5f2",

                padding=40,

                content=ft.Column(

                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                    controls=[

                        ft.Text(
                            f"Bienvenido {nombre_usuario}",
                            size=35,
                            weight="bold",
                            color="black"
                        ),

                        ft.Text(
                            "Selecciona una materia",
                            size=18,
                            color="#4b5563"
                        ),

                        ft.Container(height=20),

                        ft.Row(

                            alignment=ft.MainAxisAlignment.CENTER,

                            controls=[

                                self.dashboard_card(
                                    "Matemáticas",
                                    "Ejercicios matemáticos y cuestionarios",
                                    nombre_usuario
                                )
                            ]
                        ),

                        ft.Container(height=30),

                        ft.ElevatedButton(
                            "Cerrar sesión",
                            bgcolor="red",
                            color="white",
                            on_click=self.volver_menu
                        )
                    ]
                )
            )
        )

    # =====================================================
    # LOGIN VIEW
    # =====================================================

    def abrir_login(self, e):

        self.page.scroll = None
        self.page.padding = 0
        self.page.clean()

        self.page.add(

            ft.Container(

                expand=True,

                alignment=ft.Alignment(0, 0),

                content=ft.Column(

                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                    tight=True,

                    controls=[

                        ft.Text(
                            "LOGIN",
                            size=35,
                            weight="bold",
                            color="black"
                        ),

                        self.login_correo,

                        self.login_password,

                        ft.ElevatedButton(
                            "Ingresar",
                            bgcolor=self.primary,
                            color="white",
                            width=320,
                            on_click=self.login
                        ),

                        ft.TextButton(
                            "Volver al menú",
                            on_click=self.volver_menu
                        )
                    ]
                )
            )
        )

    # =====================================================
    # REGISTRO VIEW
    # =====================================================

    def abrir_registro(self, e):

        self.mostrar_usuarios()

        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20
        self.page.clean()

        self.page.add(

            ft.Column(

                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[

                    ft.Text(
                        "REGISTRATE",
                        size=35,
                        weight="bold",
                        color="black"
                    ),

                    self.reg_nombre,

                    self.reg_correo,

                    self.reg_password,

                    # REGISTRAR

                    ft.ElevatedButton(
                        "Registrar",
                        bgcolor=self.primary,
                        color="white",
                        width=320,
                        on_click=self.registrar_usuario
                    ),

                    # ACTUALIZAR

                    ft.ElevatedButton(
                        "Actualizar Usuario",
                        bgcolor="blue",
                        color="white",
                        width=320,
                        on_click=self.actualizar_usuario
                    ),

                    ft.TextButton(
                        "Volver al menú",
                        on_click=self.volver_menu
                    ),

                    ft.Divider(),

                    ft.Text(
                        "Usuarios registrados",
                        size=22,
                        weight="bold",
                        color="black"
                    ),

                    self.lista_usuarios
                ]
            )
        )

    # =====================================================
    # VOLVER AL MENÚ
    # =====================================================

    def volver_menu(self, e):

        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0
        self.page.clean()

        self.build()

    # =====================================================
    # SECTION
    # =====================================================

    def section(self, content, bg=None):

        return ft.Container(

            bgcolor=bg,

            padding=50,

            alignment=ft.Alignment(0, 0),

            content=ft.Container(
                width=1100,
                content=content
            )
        )

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        self.page.add(

            ft.Column(

                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=0,

                controls=[

                    # NAVBAR

                    ft.Container(

                        bgcolor=self.primary,

                        padding=20,

                        content=ft.Row(

                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                            controls=[

                                ft.Text(
                                    "Learning To Fly",
                                    size=24,
                                    weight="bold",
                                    color="white"
                                ),

                                ft.Row(

                                    spacing=10,

                                    controls=[

                                        ft.ElevatedButton(
                                            "Ingresar",
                                            bgcolor="white",
                                            color=self.primary,
                                            on_click=self.abrir_login
                                        ),

                                        ft.ElevatedButton(
                                            "Crear usuario",
                                            bgcolor="white",
                                            color=self.primary,
                                            on_click=self.abrir_registro
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    # INICIO

                    self.section(

                        ft.Row(

                            alignment=ft.MainAxisAlignment.CENTER,

                            vertical_alignment=ft.CrossAxisAlignment.CENTER,

                            controls=[

                                ft.Column(

                                    width=500,

                                    spacing=20,

                                    controls=[

                                        ft.Text(
                                            "CONOCE MÁS SOBRE NUESTRA INCREIBLE PROPUESTA",
                                            size=42,
                                            weight="bold",
                                            color=self.text_dark
                                        ),

                                        ft.Text(
                                            "Desarrollamos una aplicación educativa para fortalecer las bases académicas de estudiantes que ingresan a la educación superior.",
                                            color=self.text_soft
                                        ),

                                        ft.Text(
                                            "Learning To Fly permite evaluar y reforzar el nivel del estudiante mediante cuestionarios organizados por materias y niveles",
                                            color=self.text_soft
                                        ),

                                        ft.Row(

                                            controls=[

                                                ft.ElevatedButton(
                                                    "NUESTROS SERVICIOS",
                                                    bgcolor=self.primary,
                                                    color="black"
                                                ),

                                                ft.OutlinedButton(
                                                    "REDES SOCIALES"
                                                )
                                            ]
                                        ),

                                        ft.Row(

                                            spacing=20,

                                            controls=[

                                                self.stat(
                                                    "4",
                                                    "MÓDULOS"
                                                ),

                                                self.stat(
                                                    "Matemáticas",
                                                    "MATERIAS"
                                                ),

                                                self.stat(
                                                    "Estudiantes",
                                                    "USUARIOS"
                                                ),
                                            ]
                                        )
                                    ]
                                ),

                                ft.Image(
                                    src="sabiduria.jpg",
                                    width=400,
                                    height=400,
                                    fit=ft.BoxFit.COVER
                                )
                            ]
                        )
                    ),

                    # SERVICIOS

                    self.section(

                        ft.Column(

                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                            controls=[

                                ft.Text(
                                    "Funcionalidades de la aplicación",
                                    size=34,
                                    weight="bold",
                                    color="Black"
                                ),

                                ft.Text(
                                    "Trabajo con imágenes, código y diseño para entregar productos visualmente atractivos y fáciles de usar.",
                                    color="#94a3b8"
                                ),

                                ft.ResponsiveRow(

                                    spacing=20,
                                    run_spacing=20,

                                    controls=[

                                        self.card(
                                            "Evaluación",
                                            "Cuestionarios estructurados para medir el conocimiento"
                                        ),

                                        self.card(
                                            "Niveles progresivos",
                                            "El estudiante avanza por niveles según su desempeño"
                                        ),

                                        self.card(
                                            "Enfoque en matematicas",
                                            "El estudiante fortalece y descrubre nuevas hábilidades"
                                        ),

                                        self.card(
                                            "Retroalimentación automática",
                                            "Actualización constante del progreso"
                                        ),

                                        self.card(
                                            "Aprendizaje dinámico",
                                            "Uso de imágenes y animaciones"
                                        ),

                                        self.card(
                                            "Seguimiento del progreso",
                                            "Monitoreo del avance del estudiante"
                                        ),
                                    ]
                                )
                            ]
                        ),

                        bg=self.section_bg
                    ),

                    # RESUMEN

                    self.section(

                        ft.Column(

                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                            controls=[

                                ft.Text(
                                    "SOMOS LEARNING TO FLY",
                                    size=34,
                                    weight="bold",
                                    color=self.text_dark
                                ),

                                ft.Text(
                                    "Somos un proyecto enfocado en mejorar la transición del colegio a la educación superior.",
                                    text_align=ft.TextAlign.CENTER,
                                    color="#00060d"
                                ),

                                self.info(
                                    "Objetivo del proyecto",
                                    "Brindar herramientas que fortalezcan las bases académicas de los estudiantes"
                                ),

                                self.info(
                                    "Metodología",
                                    "Uso de cuestionarios estructurados por niveles y materias"
                                ),

                                self.info(
                                    "Ingeniería de software",
                                    "Estudiantes de tercer semestre con enfoque en desarrollo de aplicaciones"
                                ),

                                self.info(
                                    "Capacidades",
                                    "Comunicación asertiva y dominio del área del software"
                                ),

                                ft.Text(
                                    "Habilidades",
                                    size=28,
                                    weight="bold",
                                    color="black"
                                ),

                                self.skill("Python", 0.95),
                                self.skill("POO", 0.88),
                                self.skill("FLET", 0.80),
                                self.skill("TKINTER", 0.72),
                            ]
                        )
                    ),

                    # CONTACTO

                    self.section(

                        ft.Column(

                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                            controls=[

                                ft.Text(
                                    "Contáctanos",
                                    size=34,
                                    weight="bold",
                                    color=self.text_dark
                                ),

                                ft.Text(
                                    "Si deseas conocer más sobre Learning To Fly o implementar esta solución educativa, contáctanos.",
                                    text_align=ft.TextAlign.CENTER,
                                    color="#000000"
                                ),

                                self.info(
                                    "Autores",
                                    "Esteban Cruz y Fabián Vera"
                                ),

                                self.info(
                                    "Teléfonos",
                                    "300-414-8733 / 321-924-1875"
                                ),

                                self.info(
                                    "Redes",
                                    "Próximamente disponibles"
                                ),
                            ]
                        ),

                        bg=self.section_bg
                    ),

                    # FOOTER

                    ft.Container(

                        padding=20,

                        alignment=ft.Alignment(0, 0),

                        content=ft.Text(
                            "Learning To Fly © 2026",
                            color="#64748b"
                        )
                    )
                ]
            )
        )

    # =====================================================
    # COMPONENTES
    # =====================================================

    def stat(self, titulo, valor):

        return ft.Container(

            padding=10,

            bgcolor=self.card_color,

            border_radius=8,

            content=ft.Column(

                controls=[

                    ft.Text(
                        valor,
                        weight="bold",
                        color=self.text_dark
                    ),

                    ft.Text(
                        titulo,
                        color=self.text_soft
                    )
                ]
            )
        )

    def card(self, titulo, desc):

        return ft.Container(

            col={"xs": 12, "md": 4},

            padding=20,

            bgcolor=self.card_color,

            border_radius=10,

            content=ft.Column(

                controls=[

                    ft.Text(
                        titulo,
                        weight="bold",
                        color=self.text_dark
                    ),

                    ft.Text(
                        desc,
                        color=self.text_soft
                    )
                ]
            )
        )

    def info(self, titulo, desc):

        return ft.Container(

            padding=15,

            bgcolor=self.card_color,

            border_radius=10,

            content=ft.Column(

                controls=[

                    ft.Text(
                        titulo,
                        weight="bold",
                        color=self.text_dark
                    ),

                    ft.Text(
                        desc,
                        color=self.text_soft
                    )
                ]
            )
        )

    def skill(self, nombre, valor):

        return ft.Column(

            controls=[

                ft.Row(

                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    controls=[

                        ft.Text(
                            nombre,
                            color="white"
                        ),

                        ft.Text(
                            f"{int(valor*100)}%",
                            color="#94a3b8"
                        ),
                    ]
                ),

                ft.ProgressBar(
                    value=valor,
                    color=self.primary,
                    bgcolor="#c8e6c9"
                )
            ]
        )

    # =====================================================
    # TARJETAS DASHBOARD
    # =====================================================

    def dashboard_card(self, materia, descripcion, nombre_usuario="Usuario"):

        nivel_dropdown = ft.Dropdown(
            label="Nivel",
            width=200,
            options=[
                ft.dropdown.Option("Nivel 1"),
                ft.dropdown.Option("Nivel 2"),
                ft.dropdown.Option("Nivel 3"),
            ]
        )

        return ft.Container(

            width=400,

            padding=30,

            bgcolor="white",

            border_radius=12,

            content=ft.Column(

                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[

                    ft.Text(
                        materia,
                        size=26,
                        weight="bold",
                        color="black"
                    ),

                    ft.Text(
                        descripcion,
                        color="#4b5563",
                        text_align=ft.TextAlign.CENTER
                    ),

                    ft.Container(height=10),

                    nivel_dropdown,

                    ft.Container(height=10),

                    ft.ElevatedButton(
                        "Comenzar",
                        bgcolor="#1B5E20",
                        color="white",
                        width=200,
                        height=45,
                        on_click=lambda e, m=materia, d=nivel_dropdown, n=nombre_usuario:
                            self.abrir_preguntas(m, d.value, n)
                    )
                ]
            )
        )


# =========================================================
# EJECUTAR
# =========================================================

ft.app(
    target=LandingPage,
    view=ft.AppView.WEB_BROWSER
)


