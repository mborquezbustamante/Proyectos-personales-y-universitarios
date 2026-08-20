import streamlit as st
import pandas as pd
import re
from modulos.db.medico import (
    crear_medico,
    mostrar_medicos,
    borrar_medico,
    actualizar_medico
)
from modulos.db.utilidades import (
    formatear_rut,
    validar_rut,
    validar_email,
    validar_telefono
)

def limpiar_rut_med(rut_valor):
    """Elimina puntos, guiones y espacios del RUT y lo convierte a minúsculas."""
    if pd.isna(rut_valor):
        return ""
    rut_texto = str(rut_valor)
    rut_limpio = re.sub(r"[^0-9kK]", "", rut_texto)
    return rut_limpio.lower()

def mostrar_seccion_medicos():
    st.header("Médicos")
    
    # Inicializar variables de estado si no existen
    if "med_refresh_list" not in st.session_state:
        st.session_state["med_refresh_list"] = False
    
    tab_listar, tab_crear, tab_actualizar, tab_eliminar = st.tabs(
        ["📋 Listar", "➕ Crear", "🔄 Actualizar", "❌ Eliminar"]
    )

    # Tab Listar
    with tab_listar:
        st.subheader("Lista de Médicos")
        
        # Reset de filtros si se acaba de crear/actualizar/eliminar
        if st.session_state.get("med_refresh_list", False):
            st.session_state["med_list_filtro_nombre"] = ""
            st.session_state["med_list_filtro_apellido"] = ""
            st.session_state["med_list_filtro_rut"] = ""
            st.session_state["med_list_filtro_id"] = 1
            st.session_state["med_refresh_list"] = False
            
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            filtro_nombre = st.text_input(
                "Buscar por nombre",
                key="med_list_filtro_nombre",
                placeholder="Ej: Juan"
            )

        with col2:
            filtro_apellido = st.text_input(
                "Buscar por apellido",
                key="med_list_filtro_apellido",
                placeholder="Ej: Pérez"
            )

        with col3:
            filtro_rut = st.text_input(
                "Buscar por RUT",
                key="med_list_filtro_rut",
                placeholder="Ej: 12.345.678-9"
            )

        with col4:
            filtro_id = st.number_input(
                "ID Médico",
                min_value=1,
                step=1,
                key="med_list_filtro_id"
            )

        with st.spinner("Cargando lista de médicos..."):
            # Obtener datos
            data = mostrar_medicos()
            
            if data:
                # Convertir a DataFrame y normalizar nombres de columnas
                df = pd.DataFrame(data)
                
                # Verificar si hay datos antes de continuar
                if df.empty:
                    st.warning("No hay datos para mostrar")
                    return
                
                # Crear columna de RUT limpio para búsqueda
                if "rut" in df.columns:
                    df["rut_limpio"] = df["rut"].apply(limpiar_rut_med)
                
                # Aplicar filtros solo si se han especificado
                df_filtrado = df.copy()
                filtros_aplicados = False
                
                if filtro_id > 1:  # Solo aplicar si es mayor que 1
                    df_filtrado = df_filtrado[df_filtrado["id"] == filtro_id]
                    filtros_aplicados = True
                
                if filtro_nombre and filtro_nombre.strip():
                    df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(filtro_nombre, case=False, na=False)]
                    filtros_aplicados = True
                
                if filtro_apellido and filtro_apellido.strip():
                    df_filtrado = df_filtrado[df_filtrado["apellido"].str.contains(filtro_apellido, case=False, na=False)]
                    filtros_aplicados = True
                
                if filtro_rut and filtro_rut.strip():
                    filtro_rut_limpio = limpiar_rut_med(filtro_rut)
                    if "rut_limpio" in df_filtrado.columns:
                        df_filtrado = df_filtrado[df_filtrado["rut_limpio"].str.contains(filtro_rut_limpio, na=False)]
                        filtros_aplicados = True
                
                # Si no se aplicó ningún filtro, mostrar todos los registros
                if not filtros_aplicados:
                    df_filtrado = df
                
                # Preparar datos para mostrar
                if not df_filtrado.empty:
                    # Eliminar columna de RUT limpio si existe
                    columnas_a_mostrar = []
                    for col in df_filtrado.columns:
                        if col != 'rut_limpio':
                            columnas_a_mostrar.append(col)
                    df_mostrar = df_filtrado[columnas_a_mostrar].copy()
                    
                    # Renombrar columnas para visualización
                    nombres_columnas = {
                        'id': 'ID',
                        'rut': 'RUT',
                        'nombre': 'Nombre',
                        'apellido': 'Apellido',
                        'correo': 'Correo',
                        'telefono': 'Teléfono',
                        'id_especialidad': 'ID Especialidad',
                        'especialidad': 'Especialidad',
                        'horario': 'Horario'
                    }
                    df_mostrar = df_mostrar.rename(columns=nombres_columnas)
                    
                    # Configurar y mostrar la tabla
                    try:
                        st.dataframe(
                            data=df_mostrar,
                            hide_index=True,
                            column_config={
                                "ID": st.column_config.NumberColumn(
                                    width="small",
                                    format="%d"
                                ),
                                "RUT": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "Nombre": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "Apellido": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "Correo": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "Teléfono": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "ID Especialidad": st.column_config.NumberColumn(
                                    width="small",
                                    format="%d"
                                ),
                                "Especialidad": st.column_config.TextColumn(
                                    width="medium"
                                ),
                                "Horario": st.column_config.TextColumn(width="medium")
                            },
                            width="stretch"
                        )
                        
                        # Mostrar totales
                        if filtros_aplicados:
                            st.success(f"Se encontraron {len(df_mostrar)} registro(s) con los filtros aplicados")
                        else:
                            st.info(f"Total: {len(df_mostrar)} registro(s)")
                    except Exception as e:
                        st.error(f"Error al mostrar la tabla: {str(e)}")
                        with st.expander("Detalles del error"):
                            st.write(e)
                else:
                    st.warning("No se encontraron resultados con los filtros aplicados.")
            else:
                st.warning("No hay médicos registrados.")


    # Tab Crear
    with tab_crear:
        st.subheader("Crear Médico")
        
        # Reset controlado del formulario
        if st.session_state.get("med_reset_form", False):
            st.session_state["med_crear_rut"] = ""
            st.session_state["med_crear_nom"] = ""
            st.session_state["med_crear_ape"] = ""
            st.session_state["med_crear_correo"] = ""
            st.session_state["med_crear_tel"] = ""
            st.session_state["med_crear_esp"] = 1
            st.session_state["med_crear_hor"] = ""  # Resetear horario
            st.session_state["med_reset_form"] = False

        col1, col2, col3 = st.columns(3)

        with col1:
            rut = st.text_input(
                "RUT",
                key="med_crear_rut",
                placeholder="Ej: 12.345.678-9"
            )
            nombre = st.text_input("Nombre", key="med_crear_nom", placeholder="Ej: Alberto")
            apellido = st.text_input("Apellido", key="med_crear_ape", placeholder="Ej: Marín")

        with col2:
            correo = st.text_input("Correo", key="med_crear_correo", placeholder="Ej: alberto.marin@hospital.cl")
            telefono = st.text_input("Teléfono", key="med_crear_tel", placeholder="Ej: +56912345678")

        with col3:
            id_esp = st.number_input(
                "ID Especialidad",
                min_value=1,
                step=1,
                key="med_crear_esp"
            )
            horario = st.text_input("Horario de atención", key="med_crear_hor", placeholder="Ej: Lunes-Viernes 9:00-13:00")

        if st.button("Agregar Médico", key="med_crear_btn", type="primary"):
            # Validar que la especialidad exista primero
            from modulos.db.db import existe_tabla_id
            if not existe_tabla_id("especialidad", id_esp):
                st.error(f"No existe una especialidad con ID {id_esp}. Por favor, verifique el ID.")
                return
                
            if not rut or not rut.strip():
                st.error("El RUT es obligatorio.")
            elif not validar_rut(rut):
                st.error("RUT inválido. Formato esperado: 12.345.678-9")
            elif not nombre or not nombre.strip():
                st.error("El nombre es obligatorio.")
            elif not apellido or not apellido.strip():
                st.error("El apellido es obligatorio.")
            elif not correo or not correo.strip():
                st.error("El correo es obligatorio.")
            elif not validar_email(correo):
                st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
            elif not telefono or not telefono.strip():
                st.error("El teléfono es obligatorio.")
            elif not validar_telefono(telefono):
                st.error("Teléfono inválido. Usa solo dígitos o formato +56...")
            else:
                with st.spinner("Creando médico..."):
                    rut_formateado = formatear_rut(rut)
                    ok, msg = crear_medico(
                        rut=rut_formateado,
                        nombre=nombre.strip(),
                        apellido=apellido.strip(),
                        correo=correo.strip(),
                        telefono=telefono.strip(),
                        id_especialidad=id_esp,
                        horario=horario.strip()  # Pasar el horario al crear médico
                    )
                    if ok:
                        st.success(msg)
                        # Limpiar formulario y activar refresco de lista
                        st.session_state["med_reset_form"] = True
                        st.session_state["med_refresh_list"] = True
                        st.rerun()
                    else:
                        st.error(msg)
                        # Mostrar más detalles del error en un expander
                        with st.expander("Detalles del error"):
                            st.write("Datos que se intentaron insertar:")
                            st.json({
                                "rut": rut_formateado,
                                "nombre": nombre.strip(),
                                "apellido": apellido.strip(),
                                "correo": correo.strip(),
                                "telefono": telefono.strip(),
                                "id_especialidad": id_esp,
                                "horario": horario.strip()  # Mostrar el horario también en el error
                            })


    # Tab Actualizar
    with tab_actualizar:
        data = mostrar_medicos()
        if data:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower
            
            id_sel = st.selectbox(
                "Selecciona ID a actualizar",
                df["id"].tolist(),
                key="med_upd_sel"
            )
            
            fila = df[df["id"] == id_sel].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                rut_upd = st.text_input(
                    "RUT",
                    value=fila["rut"],
                    key=f"med_upd_rut_{id_sel}"
                )
                nombre_upd = st.text_input(
                    "Nombre",
                    value=fila["nombre"],
                    key=f"med_upd_nom_{id_sel}"
                )
                apellido_upd = st.text_input(
                    "Apellido",
                    value=fila["apellido"],
                    key=f"med_upd_ape_{id_sel}"
                )

            with col2:
                correo_upd = st.text_input(
                    "Correo",
                    value=fila["correo"],
                    key=f"med_upd_cor_{id_sel}"
                )
                telefono_upd = st.text_input(
                    "Teléfono",
                    value=fila["telefono"],
                    key=f"med_upd_tel_{id_sel}"
                )

            with col3:
                id_esp_upd = st.number_input(
                    "ID Especialidad",
                    value=fila["id_especialidad"],
                    min_value=1,
                    step=1,
                    key=f"med_upd_esp_{id_sel}"
                )
                # Añadir el campo para el horario de atención
                horario_upd = st.text_input(
                    "Horario de atención",
                    value=fila["horario"],
                    key=f"med_upd_hor_{id_sel}",
                    placeholder="Ej: Lunes-Viernes 9:00-13:00"
                )

            if st.button("Actualizar Médico", key=f"med_upd_btn_{id_sel}"):
                from modulos.db.db import existe_tabla_id
                if not validar_rut(rut_upd):
                    st.error("RUT inválido. Formato esperado: 12.345.678-9")
                elif not nombre_upd or not nombre_upd.strip():
                    st.error("El nombre es obligatorio.")
                elif not apellido_upd or not apellido_upd.strip():
                    st.error("El apellido es obligatorio.")
                elif not validar_email(correo_upd):
                    st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
                elif not validar_telefono(telefono_upd):
                    st.error("Teléfono inválido. Usa solo dígitos o formato +56...")
                elif id_esp_upd < 1:
                    st.error("Debe ingresar un ID de especialidad válido (mayor o igual a 1).")
                elif not existe_tabla_id("especialidad", id_esp_upd):
                    st.error(f"No existe una especialidad con ID {id_esp_upd}. Por favor, verifique el ID.")
                else:
                    rut_upd_formateado = formatear_rut(rut_upd)
                    ok, msg = actualizar_medico(
                        id_medico=id_sel,
                        rut=rut_upd_formateado,
                        nombre=nombre_upd,
                        apellido=apellido_upd,
                        correo=correo_upd,
                        telefono=telefono_upd,
                        id_especialidad=id_esp_upd,
                        horario=horario_upd.strip()  # Actualizar el horario de atención
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("-----")
            st.markdown("#### Médicos registrados")
            df_mostrar = df.rename(columns={
                "id": "ID",
                "rut": "RUT",
                "nombre": "Nombre",
                "apellido": "Apellido",
                "correo": "Correo",
                "telefono": "Teléfono",
                "id_especialidad": "ID Especialidad",
                "especialidad": "Especialidad",
                "horario": "Horario"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")
        else:
            st.info("No hay registros.")


    # Tab Eliminar
    with tab_eliminar:
        data = mostrar_medicos()
        if data:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower
            
            col1, col2 = st.columns([1, 3])
            with col1:
                id_sel_del = st.selectbox(
                    "Selecciona ID a eliminar",
                    df["id"].tolist(),
                    key="med_del_sel"
                )

            with col2:
                st.markdown("<div style='height:2.0em'></div>", unsafe_allow_html=True)
                if st.button("Eliminar", key=f"med_del_btn_{id_sel_del}"):
                    ok, msg = borrar_medico(id_sel_del)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("-----")
            st.markdown("#### Médicos registrados")
            
            df = df.rename(columns={
                "id": "ID",
                "rut": "RUT",
                "nombre": "Nombre",
                "apellido": "Apellido",
                "correo": "Correo",
                "telefono": "Teléfono",
                "id_especialidad": "ID Especialidad",
                "horario": "Horario"
            })
            
            st.dataframe(df, hide_index=True, width="stretch")
        else:
            st.info("No hay registros.")
