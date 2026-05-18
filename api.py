from flask import Flask


# =====================================================
# CREAR APP FLASK
# =====================================================

app = Flask(__name__)


# =====================================================
# RUTA PRINCIPAL
# =====================================================

@app.route("/")

def inicio():

    return {
        "mensaje": "Servidor Flask funcionando correctamente"
    }


# =====================================================
# RUTA MATEMÁTICAS
# =====================================================

@app.route("/matematicas/nivel_1")

def matematicas_nivel_1():

    preguntas = [

        {
            "pregunta": "¿La unidad de medida de las resistencias son los Ohmnios?",
            "respuesta": "Si"
        },

        {
            "pregunta": "¿Para generar una tupla debo escribir esto: []?",
            "respuesta": "No"
        },

        {
            "pregunta": "Si la matríz es de 3x2 ¿tiene 2 filas?",
            "respuesta": "No"
        }
    ]

    return {
        "nivel": "Nivel 1",
        "materia": "Matemáticas",
        "preguntas": preguntas
    }


@app.route("/matematicas/nivel_2")

def matematicas_nivel_2():

    preguntas = [

        {
            "pregunta": "¿Obtenemos Newton si multiplicamos Kilogramos por metro sobre segundo cuadrado?",
            "respuesta": "Si"
        },

        {
            "pregunta": "Si tengo una función f(x) y está elevada al cuadrado, ¿su gráfica es lineal?",
            "respuesta": "No"
        },

        {
            "pregunta": "¿Puedo hacer privado un atributo usando el doble *?",
            "respuesta": "No"
        }
    ]

    return {
        "nivel": "Nivel 2",
        "materia": "Matemáticas",
        "preguntas": preguntas
    }


@app.route("/matematicas/nivel_3")

def matematicas_nivel_3():

    preguntas = [

        {
            "pregunta": "En física, ¿Si el periodo de una onda aumenta, disminuye su frecuencia?",
            "respuesta": "Si"
        },

        {
            "pregunta": "¿En Flask, una ruta puede devolver directamente un diccionario en formato JSON?",
            "respuesta": "Sí"
        },

        {
            "pregunta": "Si la frecuencia de una onda aumenta y la velocidad se mantiene constante, ¿la longitud de onda aumenta?",
            "respuesta": "No"
        }
    ]

    return {
        "nivel": "Nivel 3",
        "materia": "Matemáticas",
        "preguntas": preguntas
    }


# =====================================================
# EJECUTAR SERVIDOR
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )



