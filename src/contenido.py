"""Contenido del sitio: datos del grupo y temario de cada materia.

Para cambiar textos del sitio edita este archivo y vuelve a generar con:
    python3 src/build.py

Los datos de los integrantes del equipo NO están aquí: se editan en
assets/js/equipo.js (así se pueden cambiar sin usar Python).
"""

SITIO = {
    "escuela": "Escuela Politécnica de Guadalajara",
    "carrera": "Tecnólogo en Sistemas Informáticos",
    "grupo": "1A",
    "turno": "Matutino",
    "clave": "TSIN1AM",
    "ciclo": "2026B",
    "titulo": "Mapa del Semestre 1A",
}

# Áreas para filtrar las materias en la portada
AREAS = {
    "tecnologia": "Tecnología",
    "ciencias": "Ciencias exactas",
    "comunicacion": "Lenguaje y comunicación",
    "integral": "Formación integral",
}

NOTA_TUTORIA = (
    "Estas sesiones se llevan a cabo de manera continua durante todo el semestre, "
    "haciendo un espacio para la intervención en el momento en que lo requiera "
    "el grupo o un estudiante."
)


def T(codigo, texto, *sub):
    """Un tema del temario. `sub` son subtemas (otros T o textos simples)."""
    return {"c": codigo, "t": texto, "sub": [s if isinstance(s, dict) else T("", s) for s in sub]}


SESION_TUTORIAL = "Sesiones de intervención tutorial focalizada a las necesidades individuales y grupales"

MATERIAS = [
    # ------------------------------------------------------------------ 1
    {
        "slug": "tutoria",
        "nombre": "Tutoría de Ingreso I",
        "corto": "Tutoría",
        "area": "integral",
        "icono": "compass",
        "color": "#E8962E",
        "docente": "",
        "tipo_seccion": "Unidad",
        "resumen": "Integración grupal, reglamentos, SIIAU y estrategias para permanecer y aprender mejor en el bachillerato.",
        "intro": (
            "Contribuir en la integración grupal, el trabajo colaborativo y la mejora del aprendizaje, "
            "mediante el conocimiento de recursos y estrategias que favorezcan al estudiantado su "
            "tránsito y permanencia escolar en el bachillerato."
        ),
        "proposito": (
            "Contribuir en la integración grupal, el trabajo colaborativo y mejora del aprendizaje, "
            "mediante el conocimiento de recursos y estrategias que favorezcan al estudiantado su "
            "tránsito y permanencia escolar en el Bachillerato."
        ),
        "indicadores": [
            {
                "titulo": "Conocimientos teóricos / técnicos",
                "icono": "book-open",
                "items": [
                    "Derechos y obligaciones de la comunidad estudiantil",
                    "Reglamento general de evaluación y promoción de alumnos",
                    "Reglamento interno de la escuela",
                    "Funciones del Sistema Integral de Información y Administración Universitaria (SIIAU)",
                    "Tutoría, momentos y tipos",
                    "Habilidades mentales",
                    "Inteligencias múltiples",
                    "Barreras para el aprendizaje y la participación",
                    "Neurodiversidad",
                    "Hábitos de estudio",
                    "Estrategias de aprendizaje",
                    "Metodologías activas",
                ],
            },
            {
                "titulo": "Habilidades cognitivas y destrezas procedimentales",
                "icono": "puzzle",
                "items": [
                    "Habilidad para convivir",
                    "Actitud de apertura",
                    "Empatía",
                    "Capacidad de consensuar",
                    "Capacidad de negociar",
                    "Asertividad",
                    "Búsqueda del bien común",
                    "Sentido de pertenencia",
                ],
            },
            {
                "titulo": "Actitudes",
                "icono": "flame",
                "items": [
                    "Constancia",
                    "Autodisciplina",
                    "Compromiso",
                    "Dedicación",
                    "Manejo oportuno de habilidades sociales y emocionales",
                ],
            },
            {
                "titulo": "Valores",
                "icono": "gem",
                "items": [
                    "Puntualidad",
                    "Responsabilidad",
                    "Disposición",
                    "Proactividad",
                    "Tolerancia",
                    "Solidaridad",
                    "Respeto",
                ],
            },
        ],
        "secciones": [
            {
                "titulo": "Mi espacio, mi grupo, mi contexto",
                "icono": "school",
                "objetivo": (
                    "Conocer los lineamientos que rigen la permanencia en el bachillerato para fomentar "
                    "la integración grupal y con la comunidad escolar a través de la convivencia positiva."
                ),
                "temas": [
                    T("1.1", "Mis expectativas y mis compromisos en el bachillerato"),
                    T("1.2", "Integración y reglas de convivencia grupal",
                      T("1.2.1", "Integración grupal"),
                      T("1.2.2", "Habilidades sociales: escucha activa, asertividad, vínculo, empatía, autocontrol"),
                      T("1.2.3", "Reglas y acuerdos de convivencia")),
                    T("1.3", "Conociendo los espacios de mi escuela",
                      T("1.3.1", "Visita guiada")),
                    T("1.4", "Recursos que favorecen mi permanencia en el bachillerato",
                      T("1.4.1", "Derechos y obligaciones",
                        T("1.4.1.1", "Estatutos, normas, código de ética, etc., que apliquen al alumnado"),
                        T("1.4.1.2", "Reglamento general de evaluación y promoción de estudiantes"),
                        T("1.4.1.3", "Reglamento interno")),
                      T("1.4.2", "Mi expediente escolar"),
                      T("1.4.3", "Herramienta: Sistema Integral de Información y Administración Universitaria (SIIAU)",
                        T("1.4.3.1", "Kardex/Boleta, revisión de horarios, orden de pago, IMSS"),
                        T("1.4.3.2", "¿Qué es el SIIAU y para qué me sirve?"),
                        T("1.4.3.3", "¿Cómo ingresar al SIIAU?")),
                      T("1.4.4", SESION_TUTORIAL)),
                ],
                "nota": NOTA_TUTORIA,
                "insignia": "Actividad integradora de la unidad 1",
            },
            {
                "titulo": "La tutoría como acompañamiento",
                "icono": "hand-heart",
                "objetivo": (
                    "Identificar el propósito de la tutoría y sus principales funciones con la finalidad de "
                    "que el estudiantado conozca los momentos y tipos de acompañamiento que recibirá durante "
                    "su trayecto en el bachillerato."
                ),
                "temas": [
                    T("2.1", "La tutoría en mi bachillerato",
                      T("2.1.1", "¿Qué es la tutoría en la educación?"),
                      T("2.1.2", "Concepto, propósito e importancia de la tutoría en el SEMS-UDG")),
                    T("2.2", "Funciones del cuerpo docente tutor",
                      T("2.2.1", "Momentos y tipos de tutoría",
                        T("2.2.1.1", "Momentos: tutoría de ingreso, tutoría de trayectoria, tutoría de egreso"),
                        T("2.2.1.2", "Tipos: grupal, individual, entre pares"))),
                    T("2.3", "Líneas de intervención",
                      T("2.3.1", "Desarrollo humano"),
                      T("2.3.2", "Vocacional"),
                      T("2.3.3", "Académica"),
                      T("2.3.4", "Familiar")),
                    T("2.4", SESION_TUTORIAL),
                ],
                "nota": NOTA_TUTORIA,
            },
            {
                "titulo": "Mejorando mi aprendizaje",
                "icono": "lightbulb",
                "objetivo": (
                    "Explorar las habilidades y hábitos de estudio para facilitar la obtención de aprendizajes "
                    "significativos con el propósito de mejorar el desempeño escolar."
                ),
                "temas": [
                    T("3.1", "¿Cómo aprendo?",
                      T("3.1.1", "Habilidades mentales"),
                      T("3.1.2", "Inteligencias múltiples"),
                      T("3.1.3", "Barreras para el aprendizaje y la participación"),
                      T("3.1.4", "Neurodiversidad")),
                    T("3.2", "Mis hábitos de estudio",
                      T("3.2.1", "¿Qué es un hábito de estudio?"),
                      T("3.2.2", "Explorando mis hábitos de estudio")),
                    T("3.3", SESION_TUTORIAL),
                ],
                "nota": NOTA_TUTORIA,
            },
            {
                "titulo": "Habilidades para la colaboración en el aula",
                "icono": "users-round",
                "objetivo": (
                    "Motivar al estudiantado a participar en diversas actividades que le permitan "
                    "desenvolverse e integrarse de manera adecuada en lo colectivo y de manera individual."
                ),
                "temas": [
                    T("4.1", "Habilidades sociales"),
                    T("4.2", "Comunicación",
                      T("4.2.1", "La importancia de la comunicación con los adolescentes")),
                    T("4.3", "Creatividad"),
                    T("4.4", "Autogestión del conocimiento"),
                    T("4.5", "Construcción colectiva (roles, relaciones y tareas)",
                      T("4.5.1", SESION_TUTORIAL)),
                ],
                "nota": NOTA_TUTORIA,
            },
        ],
    },
    # ------------------------------------------------------------------ 2
    {
        "slug": "tecnologias",
        "nombre": "Tecnologías de la Información",
        "corto": "Tecnologías",
        "area": "tecnologia",
        "icono": "laptop",
        "color": "#3B6FF5",
        "docente": "Prof. Tapia Sandoval D.",
        "tipo_seccion": "Eje",
        "resumen": "Sistema operativo, archivos, ofimática y ciudadanía digital para trabajar con orden y seguridad.",
        "intro": (
            "El punto de partida de un tecnólogo: dominar el entorno operativo, las herramientas de "
            "productividad y las reglas para usar internet con seguridad, privacidad y respeto."
        ),
        "secciones": [
            {
                "titulo": "Entorno operativo y gestión de archivos",
                "icono": "folder-tree",
                "temas": [
                    T("", "Sistemas operativos de escritorio"),
                    T("", "Interfaz gráfica"),
                    T("", "Administración de carpetas"),
                    T("", "Extensiones de archivo"),
                    T("", "Almacenamiento local y en la nube"),
                ],
            },
            {
                "titulo": "Herramientas de productividad y ofimática",
                "icono": "file-spreadsheet",
                "temas": [
                    T("", "Procesadores de texto",
                      "Formato académico", "Estilos", "Índices", "Citas y referencias"),
                    T("", "Hojas de cálculo",
                      "Fórmulas básicas", "Funciones lógicas y estadísticas", "Gráficos y tablas"),
                    T("", "Presentaciones electrónicas efectivas"),
                ],
            },
            {
                "titulo": "Ciudadanía digital e internet",
                "icono": "globe-lock",
                "temas": [
                    T("", "Navegadores"),
                    T("", "Motores de búsqueda avanzada"),
                    T("", "Seguridad informática básica"),
                    T("", "Privacidad de datos"),
                    T("", "Derechos de autor"),
                    T("", "Netiqueta"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 3
    {
        "slug": "sexualidad",
        "nombre": "Sexualidad y Perspectiva de Género",
        "corto": "Sexualidad y género",
        "area": "integral",
        "icono": "heart-handshake",
        "color": "#E0517A",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Sexualidad humana, igualdad de género, salud sexual y reproductiva, y decisiones informadas.",
        "intro": (
            "Una mirada integral a la sexualidad humana desde lo biológico, lo psicológico, lo social y lo "
            "cultural, con perspectiva de género, salud y respeto para tomar decisiones informadas."
        ),
        "secciones": [
            {
                "titulo": "Dimensiones de la sexualidad humana",
                "icono": "layers",
                "descripcion": "Aspectos biológicos, psicológicos, sociales y culturales de la sexualidad.",
                "temas": [
                    T("", "Aspectos biológicos"),
                    T("", "Aspectos psicológicos"),
                    T("", "Aspectos sociales"),
                    T("", "Aspectos culturales"),
                ],
            },
            {
                "titulo": "Perspectiva de género",
                "icono": "scale",
                "temas": [
                    T("", "Conceptos de sexo, género e identidad"),
                    T("", "Roles y estereotipos"),
                    T("", "Prevención de la violencia de género"),
                    T("", "Promoción de la igualdad"),
                ],
            },
            {
                "titulo": "Salud sexual y reproductiva",
                "icono": "shield-check",
                "temas": [
                    T("", "Anatomía y fisiología reproductiva"),
                    T("", "Métodos anticonceptivos"),
                    T("", "Prevención de Infecciones de Transmisión Sexual (ITS)"),
                    T("", "Prevención de embarazos no planeados"),
                ],
            },
            {
                "titulo": "Vínculos afectivos y toma de decisiones",
                "icono": "heart",
                "temas": [
                    T("", "Autoestima"),
                    T("", "Consentimiento"),
                    T("", "Relaciones saludables"),
                    T("", "Proyecto de vida"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 4
    {
        "slug": "algoritmos",
        "nombre": "Algoritmos y Programación",
        "corto": "Algoritmos",
        "area": "tecnologia",
        "icono": "code-xml",
        "color": "#17A88A",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Datos, variables y operadores; pseudocódigo, diagramas de flujo, estructuras de control y C.",
        "intro": (
            "Pensar como programador: describir un problema paso a paso, representarlo con pseudocódigo "
            "y diagramas de flujo, y traducirlo a código en PSeInt y en un lenguaje base C."
        ),
        "secciones": [
            {
                "titulo": "Fundamentos de algoritmos",
                "icono": "binary",
                "temas": [
                    T("", "Concepto de algoritmo"),
                    T("", "Datos, variables y constantes"),
                    T("", "Tipos de datos", "Enteros", "Flotantes", "Caracteres", "Booleanos"),
                    T("", "Operadores", "Aritméticos", "Relacionales", "Lógicos"),
                ],
            },
            {
                "titulo": "Representación de algoritmos",
                "icono": "workflow",
                "temas": [
                    T("", "Elaboración de pseudocódigo"),
                    T("", "Diagramas de flujo (simbología estándar)"),
                    T("", "Pruebas de escritorio"),
                ],
            },
            {
                "titulo": "Estructuras de control",
                "icono": "git-branch",
                "temas": [
                    T("", "Secuenciales", "Entrada", "Proceso", "Salida"),
                    T("", "Selectivas o condicionales", "if", "if-else", "switch"),
                    T("", "Repetitivas o ciclos", "while", "do-while", "for"),
                    T("", "Uso de contadores y acumuladores"),
                ],
            },
            {
                "titulo": "Introducción a la codificación",
                "icono": "braces",
                "temas": [
                    T("", "Traducción de algoritmos a un lenguaje de programación base C"),
                    T("", "PSeInt"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 5
    {
        "slug": "ingles",
        "nombre": "Inglés Básico",
        "corto": "Inglés",
        "area": "comunicacion",
        "icono": "languages",
        "color": "#D9473B",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Presentaciones personales, verb to be, pronombres, demostrativos y rutinas en presente simple.",
        "intro": (
            "Las bases para comunicarse en inglés: presentarse, describir a otras personas y hablar de la "
            "vida diaria con las estructuras gramaticales esenciales."
        ),
        "secciones": [
            {
                "titulo": "Información personal y presentaciones",
                "icono": "speech",
                "temas": [
                    T("", "Saludos y despedidas"),
                    T("", "Alfabeto"),
                    T("", "Números"),
                    T("", "Países y nacionalidades"),
                    T("", "Profesiones"),
                ],
            },
            {
                "titulo": "Estructuras gramaticales base",
                "icono": "spell-check",
                "temas": [
                    T("", "Verbo to be", "Afirmativo", "Negativo", "Interrogativo"),
                    T("", "Pronombres personales"),
                    T("", "Adjetivos posesivos"),
                    T("", "Artículos indefinidos (a/an)"),
                    T("", "Demostrativos (this/that/these/those)"),
                ],
            },
            {
                "titulo": "Vida cotidiana y rutinas",
                "icono": "clock",
                "temas": [
                    T("", "Presente simple (Simple Present)"),
                    T("", "Adverbios de frecuencia"),
                    T("", "Expresión de la hora"),
                    T("", "Días de la semana"),
                    T("", "Vocabulario del entorno escolar y familiar"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 6
    {
        "slug": "historia",
        "nombre": "Historia e Identidad Universitaria",
        "corto": "Historia UDG",
        "area": "integral",
        "icono": "landmark",
        "color": "#B07A36",
        "docente": "",
        "tipo_seccion": "Unidad",
        "resumen": "De la Real Universidad de 1792 a la Red Universitaria: historia, misión y ser universitario.",
        "intro": (
            "Conocer de dónde viene la Universidad de Guadalajara, cómo se organiza hoy y qué significa "
            "formar parte de ella como estudiante universitario."
        ),
        "linea_tiempo": [
            {"anio": "1792", "texto": "Real Universidad de Guadalajara"},
            {"anio": "1821", "texto": "Luchas libertarias: clausuras y aperturas"},
            {"anio": "1861", "texto": "Inicia el periodo sin universidad (Interregno)"},
            {"anio": "1925", "texto": "Refundación de la UDG"},
            {"anio": "1989", "texto": "Cierra la etapa de consolidación"},
            {"anio": "Hoy", "texto": "La Red Universitaria"},
        ],
        "secciones": [
            {
                "titulo": "Historia y desarrollo de la UDG",
                "icono": "scroll-text",
                "temas": [
                    T("1.1", "La Real Universidad de Guadalajara, 1792"),
                    T("1.2", "Las clausuras y aperturas de la UDG",
                      T("", "Las luchas libertarias: 1821 y 1861")),
                    T("1.3", "El periodo sin universidad (Interregno), 1861–1924"),
                    T("1.4", "La refundación y consolidación de la UDG, 1925–1989"),
                    T("1.5", "La Red Universitaria y la actualidad"),
                ],
            },
            {
                "titulo": "Identidad y misión de la UDG",
                "icono": "building-2",
                "temas": [
                    T("2.1", "Organización y estructura",
                      T("2.1.1", "Órganos de gobierno")),
                    T("2.2", "La misión de la UDG"),
                    T("2.3", "Derechos y obligaciones de los universitarios"),
                ],
            },
            {
                "titulo": "La universidad en la sociedad actual",
                "icono": "globe",
                "temas": [
                    T("3.1", "Interacción entre la universidad y la sociedad",
                      T("3.1.1", "Extensión universitaria")),
                    T("3.2", "El papel de la universidad en la investigación e innovación"),
                    T("3.3", "La responsabilidad social de la universidad"),
                    T("3.4", "Mi escuela en la comunidad"),
                    T("3.5", "Desafíos y oportunidades para la universidad en el futuro"),
                ],
            },
            {
                "titulo": "Ser universitario",
                "icono": "graduation-cap",
                "temas": [
                    T("4.1", "Mi responsabilidad como universitario"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 7
    {
        "slug": "numerica",
        "nombre": "Habilidad Numérica",
        "corto": "Habilidad numérica",
        "area": "ciencias",
        "icono": "sigma",
        "color": "#2E9E57",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Números reales, proporciones y porcentajes, álgebra básica y razonamiento lógico-matemático.",
        "intro": (
            "Agilidad con los números para resolver problemas reales: operaciones con números reales, "
            "proporcionalidad, primeros pasos en el álgebra y razonamiento lógico."
        ),
        "secciones": [
            {
                "titulo": "Sentido numérico y aritmética",
                "icono": "calculator",
                "temas": [
                    T("", "Operaciones con números reales", "Enteros", "Fracciones", "Decimales"),
                    T("", "Jerarquía de operaciones"),
                    T("", "Signos de agrupación"),
                ],
            },
            {
                "titulo": "Proporcionalidad y porcentajes",
                "icono": "percent",
                "temas": [
                    T("", "Razones"),
                    T("", "Proporciones directas e inversas"),
                    T("", "Regla de tres simple y compuesta"),
                    T("", "Cálculo de porcentajes"),
                ],
            },
            {
                "titulo": "Introducción al pensamiento algebraico",
                "icono": "square-function",
                "temas": [
                    T("", "Lenguaje algebraico"),
                    T("", "Reducción de términos semejantes"),
                    T("", "Operaciones básicas con polinomios"),
                    T("", "Resolución de ecuaciones lineales de primer grado"),
                ],
            },
            {
                "titulo": "Razonamiento lógico-matemático",
                "icono": "puzzle",
                "temas": [
                    T("", "Sucesiones numéricas"),
                    T("", "Series espaciales"),
                    T("", "Resolución de problemas aplicados"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 8
    {
        "slug": "lectoescritura",
        "nombre": "Habilidad de Lectoescritura",
        "corto": "Lectoescritura",
        "area": "comunicacion",
        "icono": "pen-line",
        "color": "#5B5FD8",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Comprensión lectora, ortografía, redacción de textos y expresión oral frente a grupo.",
        "intro": (
            "Leer con comprensión, escribir con corrección y hablar con seguridad: las habilidades que "
            "sostienen el trabajo en todas las demás materias."
        ),
        "secciones": [
            {
                "titulo": "Comprensión lectora",
                "icono": "book-open-text",
                "temas": [
                    T("", "Estrategias de lectura",
                      "Predicción", "Inferencia", "Ideas principales y secundarias"),
                    T("", "Análisis de textos", "Expositivos", "Argumentativos", "Narrativos"),
                ],
            },
            {
                "titulo": "Normativa de la lengua",
                "icono": "spell-check",
                "temas": [
                    T("", "Ortografía puntual"),
                    T("", "Ortografía acentual", "Reglas generales", "Acento diacrítico"),
                    T("", "Uso de grafías"),
                ],
            },
            {
                "titulo": "Producción de textos",
                "icono": "notebook-pen",
                "temas": [
                    T("", "Propiedades textuales", "Coherencia", "Cohesión", "Adecuación"),
                    T("", "Redacción de textos", "Resúmenes", "Síntesis", "Reseñas", "Ensayos cortos"),
                ],
            },
            {
                "titulo": "Expresión oral",
                "icono": "mic",
                "temas": [
                    T("", "Técnicas de comunicación efectiva"),
                    T("", "Lenguaje no verbal"),
                    T("", "Exposición frente a grupo"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ 9
    {
        "slug": "fisica",
        "nombre": "Física y sus Aplicaciones",
        "corto": "Física",
        "area": "ciencias",
        "icono": "atom",
        "color": "#8B4FF0",
        "docente": "",
        "tipo_seccion": "Unidad",
        "resumen": "Medición, movimiento y fuerzas, electricidad y magnetismo, sonido y luz en 18 semanas.",
        "intro": (
            "Del método científico a la luz y el sonido: cuatro unidades de competencia organizadas "
            "semana a semana, con sus actividades, tareas y exámenes."
        ),
        "secciones": [
            {
                "titulo": "Método científico y medición",
                "icono": "ruler",
                "temas": [
                    T("", "Encuadre, diagnóstico y método científico"),
                    T("1.3", "Magnitudes"),
                    T("1.4", "Sistemas de unidades"),
                    T("1.5", "Conversión de unidades"),
                    T("1.6", "Prefijos del Sistema Internacional"),
                ],
            },
            {
                "titulo": "Movimiento y fuerzas",
                "icono": "rocket",
                "temas": [
                    T("2.1", "Movimiento Rectilíneo Uniforme (MRU)"),
                    T("2.2", "Movimiento Rectilíneo Uniformemente Acelerado y caída libre"),
                    T("2.3", "Las fuerzas y las Leyes de Newton"),
                    T("2.4", "Sistemas de fuerzas",
                      T("", "Teoría"),
                      T("", "Proyecto experimental de equilibrio")),
                ],
            },
            {
                "titulo": "Electricidad y magnetismo",
                "icono": "zap",
                "temas": [
                    T("3.1", "Electricidad estática"),
                    T("3.2", "Campo eléctrico"),
                    T("3.3", "Voltaje"),
                    T("3.4", "Corriente"),
                    T("3.5", "Ley de Ohm"),
                    T("3.6", "Circuitos en serie y paralelo"),
                    T("3.7", "Magnetismo"),
                    T("3.8", "Electromagnetismo"),
                ],
            },
            {
                "titulo": "Sonido y luz",
                "icono": "waves",
                "temas": [
                    T("4.1", "Definición y propagación del sonido"),
                    T("4.2", "Propiedades del sonido y contaminación"),
                    T("4.3", "Luz visible y cámara oscura"),
                    T("4.4", "Espectro no visible y evaluación final"),
                ],
            },
        ],
        # Desglose semanal (tipos: part, act, tarea, examen, integrador)
        "calendario": [
            {"s": 1, "u": 1, "ini": "2026-08-17", "fechas": "17 – 21 ago", "temas": ["Encuadre, diagnóstico y método científico"], "p": [("part", 0.5)]},
            {"s": 2, "u": 1, "ini": "2026-08-24", "fechas": "24 – 28 ago", "temas": ["1.3 Magnitudes", "1.4 Sistemas de unidades"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 3, "u": 1, "ini": "2026-08-31", "fechas": "31 ago – 4 sep", "temas": ["1.5 Conversión de unidades"], "p": [("tarea", 4.0, "Tarea 1"), ("act", 1.8)]},
            {"s": 4, "u": 1, "ini": "2026-09-07", "fechas": "7 – 11 sep", "temas": ["1.6 Prefijos del Sistema Internacional"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 5, "u": 2, "ini": "2026-09-14", "fechas": "14 – 18 sep", "temas": ["2.1 Movimiento Rectilíneo Uniforme (MRU)"], "p": [("examen", 10.0, "Examen 1"), ("act", 1.8)]},
            {"s": 6, "u": 2, "ini": "2026-09-21", "fechas": "21 – 25 sep", "temas": ["2.2 Movimiento R. U. Acelerado y caída libre"], "p": [("tarea", 4.0, "Tarea 2"), ("act", 1.8)]},
            {"s": 7, "u": 2, "ini": "2026-09-28", "fechas": "28 sep – 2 oct", "temas": ["2.3 Las fuerzas y las Leyes de Newton"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 8, "u": 2, "ini": "2026-10-05", "fechas": "5 – 9 oct", "temas": ["2.4 Sistemas de fuerzas (teoría)"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 9, "u": 2, "ini": "2026-10-12", "fechas": "12 – 16 oct", "temas": ["2.4 Proyecto experimental de equilibrio"], "p": [("tarea", 4.0, "Tarea 3"), ("act", 1.8)]},
            {"s": 10, "u": 3, "ini": "2026-10-19", "fechas": "19 – 23 oct", "temas": ["3.1 Electricidad estática (inicio de examen departamental)"], "p": [("examen", 10.0, "Examen departamental"), ("act", 1.8)]},
            {"s": 11, "u": 3, "ini": "2026-10-26", "fechas": "26 – 30 oct", "temas": ["3.2 Campo eléctrico"], "p": [("examen", 10.0, "Examen 2"), ("act", 1.8)]},
            {"s": 12, "u": 3, "ini": "2026-11-02", "fechas": "2 – 6 nov", "temas": ["3.3 Voltaje", "3.4 Corriente", "3.5 Ley de Ohm"], "p": [("tarea", 4.0, "Tarea 4"), ("act", 1.8)]},
            {"s": 13, "u": 3, "ini": "2026-11-09", "fechas": "9 – 13 nov", "temas": ["3.6 Circuitos en serie y paralelo"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 14, "u": 3, "ini": "2026-11-16", "fechas": "16 – 20 nov", "temas": ["3.7 Magnetismo", "3.8 Electromagnetismo"], "p": [("tarea", 4.0, "Tarea 5"), ("act", 1.8)]},
            {"s": 15, "u": 4, "ini": "2026-11-23", "fechas": "23 – 27 nov", "temas": ["4.1 Definición y propagación del sonido"], "p": [("act", 1.8), ("part", 0.5)]},
            {"s": 16, "u": 4, "ini": "2026-11-30", "fechas": "30 nov – 4 dic", "temas": ["4.2 Propiedades del sonido y contaminación"], "p": [("act", 1.8), ("part", 1.0)]},
            {"s": 17, "u": 4, "ini": "2026-12-07", "fechas": "7 – 11 dic", "temas": ["4.3 Luz visible y cámara oscura", "4.4 Espectro no visible y evaluación final"], "p": [("integrador", 10.0, "Integrador"), ("act", 1.0), ("act", 1.0), ("part", 0.5)]},
            {"s": 18, "u": 0, "ini": "2026-12-14", "fechas": "14 – 18 dic", "temas": ["Fecha límite para el registro y publicación de la evaluación continua en el periodo ordinario y extraordinario"], "p": []},
        ],
    },
    # ------------------------------------------------------------------ 10
    {
        "slug": "socioemocional",
        "nombre": "Educación Socioemocional",
        "corto": "Socioemocional",
        "area": "integral",
        "icono": "brain",
        "color": "#1C97C9",
        "docente": "",
        "tipo_seccion": "Eje",
        "resumen": "Autoconocimiento, autorregulación, empatía, colaboración y un proyecto de vida con metas claras.",
        "intro": (
            "Conocer y regular las propias emociones, convivir con empatía y construir un proyecto de vida "
            "con metas personales y académicas."
        ),
        "secciones": [
            {
                "titulo": "Autoconocimiento",
                "icono": "eye",
                "temas": [
                    T("", "Identificación y comprensión de emociones propias"),
                    T("", "Reconocimiento de fortalezas y áreas de oportunidad"),
                    T("", "Autoestima"),
                    T("", "Manejo del estrés académico"),
                ],
            },
            {
                "titulo": "Autorregulación",
                "icono": "gauge",
                "temas": [
                    T("", "Estrategias de gestión emocional"),
                    T("", "Control de impulsos"),
                    T("", "Tolerancia a la frustración"),
                    T("", "Toma de decisiones responsables"),
                ],
            },
            {
                "titulo": "Conciencia social y empatía",
                "icono": "handshake",
                "temas": [
                    T("", "Escucha activa"),
                    T("", "Respeto a la diversidad"),
                    T("", "Resolución pacífica de conflictos"),
                    T("", "Comunicación asertiva dentro del aula y la comunidad"),
                ],
            },
            {
                "titulo": "Colaboración y sentido de pertenencia",
                "icono": "users",
                "temas": [
                    T("", "Trabajo en equipo"),
                    T("", "Corresponsabilidad"),
                    T("", "Construcción de redes de apoyo"),
                    T("", "Adaptación al entorno universitario"),
                ],
            },
            {
                "titulo": "Proyecto de vida",
                "icono": "milestone",
                "temas": [
                    T("", "Establecimiento de metas personales y académicas a corto y mediano plazo"),
                ],
            },
        ],
    },
]

# Ejemplo que se muestra en la página de Algoritmos
EJEMPLO_PSEINT = """Algoritmo PromedioParcial
    Definir c1, c2, c3, prom Como Real
    Escribir "Captura tres calificaciones:"
    Leer c1, c2, c3
    prom <- (c1 + c2 + c3) / 3
    Si prom >= 60 Entonces
        Escribir "Aprobado con ", prom
    SiNo
        Escribir "Reprobado con ", prom
    FinSi
FinAlgoritmo"""
