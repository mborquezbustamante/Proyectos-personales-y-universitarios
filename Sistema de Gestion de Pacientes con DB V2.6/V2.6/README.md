# 🏥⚕️ Sistema de Gestión Hospitalaria

Proyecto universitario para la gestión de pacientes, médicos, citas, diagnósticos, tratamientos, historiales y atenciones en un hospital. Desarrollado en Python con Streamlit y SQLite.

## Características

- Registro y gestión de pacientes y médicos
- Agendamiento y control de citas médicas
- Registro de diagnósticos y tratamientos
- Historial médico completo por paciente
- Gestión de atenciones y seguimiento
- Interfaz web amigable con Streamlit
- Base de datos relacional en SQLite
- Datos de prueba automáticos para desarrollo

## Estructura del proyecto

```
V2/
│
├── app.py                      # Entrada principal de la app Streamlit
├── hospital.sql                # Script SQL con el esquema de la base de datos
├── scripts/
│   └── datos_pruebas.py   # Script para poblar la base con datos de prueba
├── modulos/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── especialidad.py
│   │   ├── medico.py
│   │   ├── paciente.py
│   │   ├── cita.py
│   │   ├── diagnostico.py
│   │   ├── tratamiento.py
│   │   ├── historial.py
│   │   ├── atencion.py
│   │   └── utilidades.py
│   └── ui/
│       ├── especialidades.py
│       ├── medicos.py
│       ├── pacientes.py
│       ├── citas.py
│       ├── diagnosticos.py
│       ├── tratamientos.py
│       ├── historiales.py
│       └── atenciones.py
└── ...
```

## Instalación

1. **Clona el repositorio**
   ```sh
   git clone <url-del-repo>
   cd V2
   ```

2. **Instala dependencias**
   ```sh
   pip install streamlit
   ```

3. **Crea la base de datos**
   ```sh
   sqlite3 hospital.db < hospital.sql
   ```

4. **Pobla la base con datos de prueba**
   ```sh
   python scripts/datos_pruebas.py
   ```

## Uso

1. **Inicia la aplicación**
   ```sh
   streamlit run app.py
   ```

2. **Accede desde el navegador**
   - URL por defecto: `http://localhost:8501`

3. **Navega por las secciones**
   - Pacientes, Médicos, Citas, Diagnósticos, Tratamientos, Historiales, Atenciones, Especialidades.

## Scripts útiles

- `hospital.sql`: Crea todas las tablas y vistas necesarias.
- `scripts/datos_pruebas.py`: Inserta datos de ejemplo para pruebas y desarrollo.

## Requisitos

- Python 3.8+
- Streamlit
- SQLite3

## Notas técnicas

- El sistema valida relaciones entre entidades (por ejemplo, no se puede eliminar un diagnóstico si tiene tratamientos asociados).
- Los módulos en `modulos/db` gestionan la lógica de acceso a datos.
- Los módulos en `modulos/ui` implementan la interfaz Streamlit para cada entidad.
- El script de datos de prueba genera 10 registros por sección, con datos realistas y relaciones válidas.

## Accesibilidad

- Todos los widgets Streamlit tienen etiquetas descriptivas para cumplir con buenas prácticas de accesibilidad.

## 🧙🏻‍♂️ Autores

- Catalina Palma
- Matías Bórquez
- Benjamín Rivera

## Licencia

Este proyecto es de uso académico. Puedes modificarlo y adaptarlo libremente para fines educativos.
