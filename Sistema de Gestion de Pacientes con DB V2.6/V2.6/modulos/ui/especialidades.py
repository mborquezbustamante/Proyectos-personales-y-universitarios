import streamlit as st
import pandas as pd
from modulos.db.especialidad import (
    mostrar_especialidades,
    agregar_especialidad,
    actualizar_especialidad,
    eliminar_especialidad
)

def mostrar_seccion_especialidades():
    """Interfaz Streamlit para gestionar las especialidades médicas."""

    st.header("Especialidades")
    tab_listar, tab_crear, tab_actualizar, tab_eliminar = st.tabs(
        ["📋 Listar", "➕ Crear", "🔄 Actualizar", "❌ Eliminar"]
    )

    # =============================
    #           LISTAR 
    # =============================
    with tab_listar:
        st.subheader("Lista de Especialidades")

        # Si se acaba de crear o eliminar, limpiar filtro ID
        if st.session_state.get("esp_reset_lista", False):
            st.session_state["esp_list_filtro_id"] = 0
            st.session_state["esp_reset_lista"] = False

        # Filtros (ID + búsqueda por nombre/descr.)
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            # Inicializar el valor en session_state solo si no existe
            if "esp_list_filtro_id" not in st.session_state:
                st.session_state["esp_list_filtro_id"] = 0
                
            filtro_id = st.number_input(
                "Buscar por ID de Especialidad",
                min_value=0,  # 0 significa sin filtro
                step=1,
                key="esp_list_filtro_id"
            )
        with col2:
            filtro_nombre = st.text_input("Nombre contiene", key="esp_list_filtro_nombre", placeholder="Ej: Cardiología")
        with col3:
            filtro_desc = st.text_input("Descripción contiene", key="esp_list_filtro_desc", placeholder="Ej: estudio del corazón")

        # Obtener datos
        data = mostrar_especialidades()

        if not data:
            st.warning("No hay especialidades registradas.")
        else:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower

            if filtro_id > 0:
                id_col = 'id' if 'id' in df.columns else 'id_especialidad'
                df = df[df[id_col] == filtro_id]
            # Filtros por texto
            if filtro_nombre:
                df = df[df["nombre"].astype(str).str.contains(filtro_nombre, case=False, na=False)]
            if filtro_desc:
                df = df[df["descripcion"].astype(str).str.contains(filtro_desc, case=False, na=False)]

            if not df.empty:
                id_col = 'id' if 'id' in df.columns else 'id_especialidad'
                df_mostrar = df.rename(columns={
                    id_col: "ID",
                    "nombre": "Nombre",
                    "descripcion": "Descripción"
                })
                st.dataframe(df_mostrar, hide_index=True, width="stretch")
                st.info(f"Total: {len(df)} registro(s)")
            else:
                st.warning("No se encontraron resultados con ese ID.")

    # =============================
    #           CREAR 
    # =============================
    with tab_crear:
        st.subheader("Crear Especialidad")

        # Reset controlado del formulario
        if st.session_state.get("esp_reset_form", False):
            st.session_state["esp_crear_nom"] = ""
            st.session_state["esp_crear_desc"] = ""
            st.session_state["esp_reset_form"] = False

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", key="esp_crear_nom", placeholder="Ej: Cardiología")
        with col2:
            descripcion = st.text_area("Descripción", key="esp_crear_desc", height=50, placeholder="Ej: Especialidad médica dedicada al estudio del corazón y sistema cardiovascular")

        if st.button("Agregar Especialidad", key="esp_crear_btn"):
            if not nombre or not nombre.strip():
                st.warning("El nombre es obligatorio.")
            elif not descripcion or not descripcion.strip():
                st.warning("La descripción es obligatoria.")
            else:
                ok, msg = agregar_especialidad(nombre, descripcion)
                if ok:
                    st.success(msg)
                    # Limpiar formulario y resetear filtro de lista
                    st.session_state["esp_reset_form"] = True
                    st.session_state["esp_reset_lista"] = True
                    st.rerun()
                else:
                    st.error(msg)

    # =============================
    #         ACTUALIZAR 
    # =============================
    with tab_actualizar:
        st.subheader("Actualizar Especialidad")

        # Reset controlado del formulario
        if st.session_state.get("esp_reset_form_upd", False):
            st.session_state["esp_upd_sel"] = None
            st.session_state["esp_upd_nom"] = ""
            st.session_state["esp_upd_desc"] = ""
            st.session_state["esp_reset_form_upd"] = False

        data = mostrar_especialidades()
        if not data:
            st.warning("No hay especialidades registradas.")
        else:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower
            
            id_col = 'id' if 'id' in df.columns else 'id_especialidad'
            
            # Formulario de actualización
            lista_ids = df[id_col].tolist()
            
            id_sel = st.selectbox(
                "Selecciona el ID a modificar", 
                lista_ids, 
                key="esp_upd_sel"
            )
            
            if id_sel:
                fila = df[df[id_col] == id_sel].iloc[0]
                
                nuevo_nombre = st.text_input(
                    "Nuevo nombre", 
                    value=fila["nombre"], 
                    key="esp_upd_nom"
                )
                nueva_desc = st.text_area(
                    "Nueva descripción", 
                    value=fila["descripcion"],
                    key="esp_upd_desc"
                )
                
                if st.button("Actualizar Especialidad", key=f"esp_upd_btn_{id_sel}", type="primary"):
                    if not nuevo_nombre or not nuevo_nombre.strip():
                        st.warning("El nombre es obligatorio.")
                    elif not nueva_desc or not nueva_desc.strip():
                        st.warning("La descripción es obligatoria.")
                    else:
                        ok, msg = actualizar_especialidad(id_sel, nuevo_nombre, nueva_desc)
                        if ok:
                            st.success(msg)
                            # Limpiar formulario y resetear filtro de lista
                            st.session_state["esp_reset_form_upd"] = True
                            st.session_state["esp_reset_lista"] = True
                            st.rerun()
                        else:
                            st.error(msg)
            
            # Mostrar tabla completa al final
            st.markdown("-----")
            st.markdown("#### Especialidades registradas")
            df_mostrar = df.rename(columns={
                id_col: "ID",
                "nombre": "Nombre",
                "descripcion": "Descripción"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")

    # Tab Eliminar
    with tab_eliminar:
        st.markdown("### Eliminar Especialidad")
        data = mostrar_especialidades()
        
        if data:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower
            id_col = 'id' if 'id' in df.columns else 'id_especialidad'
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("**Seleccionar ID:**")
                id_sel = st.selectbox(
                    "Selecciona ID a eliminar",
                    df[id_col].tolist(),
                    key="esp_del_sel",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("<div style='height:2.4em'></div>", unsafe_allow_html=True)
                eliminar_btn = st.button("Eliminar", key=f"esp_del_btn_{id_sel}")
            
            if eliminar_btn:
                ok, msg = eliminar_especialidad(id_sel)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
            st.markdown("-----")
            st.markdown("#### Especialidades registradas")
            
            df_mostrar = df.rename(columns={
                id_col: "ID",
                "nombre": "Nombre",
                "descripcion": "Descripción"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")
        else:
            st.info("No hay registros.")