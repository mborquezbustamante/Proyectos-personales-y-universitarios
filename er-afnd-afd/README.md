# Conversor de Expresiones Regulares a AFND/AFD

![Python](https://img.shields.io/badge/Python-3.7%2B-blue) 

## 📋 Descripción

Herramienta con interfaz gráfica que convierte una expresión regular (ER) en un Autómata Finito No Determinista (AFND) mediante la **construcción de Thompson**, y luego lo transforma en un Autómata Finito Determinista (AFD) equivalente mediante el **algoritmo de construcción de subconjuntos**. Permite visualizar ambos autómatas como grafos, buscar todas las ocurrencias de la ER en un texto de entrada, y simular la ejecución del AFD paso a paso sobre ese texto.

Este proyecto es parte del coursework de **Teoría de la Computación** en la Universidad Finis Terrae.

## 🎯 Características

- ✅ **Validación de ER** — Verifica caracteres permitidos, paréntesis balanceados y colocación correcta de operadores antes de procesar
- ✅ **Shunting-Yard** — Conversión de la ER a notación postfija respetando precedencia (`*` > `.` > `|`) y asociatividad
- ✅ **Construcción de Thompson** — Genera el AFND a partir de la ER postfija (unión, concatenación, cerradura de Kleene)
- ✅ **Soporte de símbolos especiales** — Epsilon (`_`), conjunto vacío (`0`) y alfabeto completo (`Σ`)
- ✅ **Búsqueda flotante** — Permite detectar la ER en cualquier posición del texto, no solo desde el inicio
- ✅ **Conversión AFND → AFD** — Algoritmo de subconjuntos con épsilon-clausura, incluyendo estado sumidero automático
- ✅ **Búsqueda de ocurrencias** — Reporta todos los calces válidos (más cortos) por línea de texto
- ✅ **Simulación paso a paso** — Genera cada transición del AFD como evento individual, pensado para animar en la GUI
- ✅ **Visualización con Graphviz** — Renderiza AFND y AFD como grafos dirigidos dentro de la interfaz
- ✅ **Interfaz gráfica en Tkinter** — Controles para convertir, buscar y simular con play/pausa/paso

## 🔧 Requisitos

- Python 3.7 o superior
- [Graphviz](https://graphviz.org/download/) instalado en el sistema (el binario `dot`, no solo la librería de Python)
- Librerías de Python:
  ```bash
  pip install graphviz pillow
  ```

## 📦 Instalación

```bash
git clone https://github.com/mborquezbustamante/Proyectos-personales-y-universitarios.git
cd Proyectos-personales-y-universitarios/er-afnd-afd
pip install graphviz pillow
```

**Nota sobre Graphviz:** la librería de Python (`pip install graphviz`) solo genera el código del grafo; necesitas el programa Graphviz instalado en el sistema operativo para que se renderice como imagen.
- Fedora: `sudo dnf install graphviz`
- Ubuntu/Debian: `sudo apt install graphviz`
- Windows: instalador desde [graphviz.org](https://graphviz.org/download/) (agregar a PATH)

## 🚀 Uso

```bash
python Interfas_Final.py
```

1. Escribe una expresión regular en el campo **ER** (ej: `a.b|c*`)
2. Haz clic en **ER → AFND** para construir y visualizar el autómata no determinista
3. Haz clic en **AFND → AFD** para convertirlo al autómata determinista equivalente
4. Escribe o pega un texto en el panel de entrada y usa **Buscar Ocurrencias** para encontrar todos los calces
5. Usa **Simular ▶ / Pausa ⏸ / Paso ▷** para ver cómo el AFD procesa el texto carácter por carácter

### Sintaxis de la expresión regular

| Símbolo | Significado |
|---|---|
| `a`, `b`, ... | Literal (letras y dígitos) |
| `.` | Concatenación |
| `\|` | Unión (OR) |
| `*` | Cerradura de Kleene (cero o más repeticiones) |
| `( )` | Agrupación |
| `_` | Epsilon (cadena vacía) |
| `0` | Conjunto vacío |
| `Σ` | Cualquier letra del alfabeto |

**Ejemplo:** `a.(b|c)*` acepta `a`, `ab`, `ac`, `abbc`, `acbc`, etc.

## 📁 Estructura del proyecto

```
er-afnd-afd/
├── Introducir_ER.py    # Validación sintáctica de la ER (caracteres, paréntesis, operadores)
├── ER_AFND.py           # Tokenizador, Shunting-Yard y construcción de Thompson (ER → AFND)
├── AFND_AFD.py          # Algoritmo de subconjuntos (AFND → AFD), búsqueda y simulación
├── Interfas_Final.py    # Interfaz gráfica (Tkinter + Graphviz)
└── README.md
```

## 🧠 Cómo funciona

### 1. Validación (`Introducir_ER.py`)
Antes de procesar la ER, se valida que:
- Solo contenga caracteres permitidos (alfanuméricos, operadores `. | * ( )`, y los símbolos especiales `_`/`0`)
- Los paréntesis estén balanceados
- Los operadores binarios (`.`, `|`) y el operador unario (`*`) estén bien colocados (no al inicio/fin, no consecutivos sin operando)

### 2. ER → AFND (`ER_AFND.py`)
- **Tokenización**: separa la ER en símbolos individuales y valida que cada uno sea reconocible
- **Concatenación implícita**: inserta el operador `.` donde corresponda (ej: `ab` → `a.b`)
- **Shunting-Yard**: convierte la ER de notación infija a postfija respetando precedencia y asociatividad
- **Construcción de Thompson**: recorre la ER postfija construyendo el AFND pieza por pieza — cada literal genera un mini-autómata de dos estados, y los operadores (`.`, `|`, `*`) combinan sub-autómatas mediante transiciones epsilon

### 3. AFND → AFD (`AFND_AFD.py`)
- **Épsilon-clausura**: calcula el conjunto de estados alcanzables sin consumir ningún símbolo
- **Construcción de subconjuntos**: cada estado del AFD representa un conjunto de estados del AFND; se procesan iterativamente hasta cubrir todas las transiciones posibles
- **Estado sumidero**: se crea automáticamente cuando una transición no tiene destino válido, garantizando que el AFD sea total

### 4. Búsqueda y simulación
- `buscar_ocurrencias`: recorre cada línea del texto probando cada posición de inicio, reportando el calce más corto y válido desde cada una
- `simular_afd_generador`: versión en forma de generador (`yield`) de la misma lógica, emitiendo cada transición individual para poder animarla en la GUI

## 🎓 Conceptos educativos

Este proyecto ilustra:
- ✅ Teoría de autómatas — AFND, AFD, equivalencia entre ambos
- ✅ Construcción de Thompson para expresiones regulares
- ✅ Algoritmo de construcción de subconjuntos (*subset construction*)
- ✅ Épsilon-clausura y transiciones epsilon
- ✅ Algoritmo Shunting-Yard (notación infija → postfija)
- ✅ Parsing y validación sintáctica
- ✅ Interfaces gráficas con Tkinter
- ✅ Visualización de grafos con Graphviz
- ✅ Generadores de Python (`yield`) para animación paso a paso

## ✍️ Autor

- **Rad** — Estudiante de Ingeniería Civil en Informática y Telecomunicaciones, Universidad Finis Terrae

## 📚 Referencias

- [Construcción de Thompson - Wikipedia](https://es.wikipedia.org/wiki/Construcci%C3%B3n_de_Thompson)
- [Algoritmo de construcción de subconjuntos](https://es.wikipedia.org/wiki/Construcci%C3%B3n_de_subconjuntos)
- [Algoritmo Shunting-Yard - Wikipedia](https://es.wikipedia.org/wiki/Algoritmo_shunting_yard)
- [Documentación de Graphviz](https://graphviz.readthedocs.io/)

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.
