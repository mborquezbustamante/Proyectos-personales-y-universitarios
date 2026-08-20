# ============================================================
# IMPORTACIÓN DE CLASES Y FUNCIONES NECESARIAS
# ============================================================
from ER_AFND import (Estado,  AFND, contador_estado_id)

# ============================================================
# AFND A AFD: Lógica Principal (Clausura y Movimiento)
# ============================================================

def e_clausura(estados_set, afnd):
    #Calcula la epsilon-clausura de un conjunto de estados
    pila = list(estados_set)
    clausura = set(estados_set)
    
    while pila:
        estado_actual = pila.pop()
        
        if '' in estado_actual.transiciones:
            for siguiente_estado in estado_actual.transiciones['']:
                if siguiente_estado not in clausura:
                    clausura.add(siguiente_estado)
                    pila.append(siguiente_estado)
                    
    return clausura

def mover(estados_set, simbolo):
    #Calcula el conjunto de estados alcanzables con un símbolo
    siguientes_estados = set()
    for estado in estados_set:
        if simbolo in estado.transiciones:
            siguientes_estados.update(estado.transiciones[simbolo])
            
    return siguientes_estados

def crear_estado_sumidero(afd, alfabeto, next_sequential_id):
    #Crea o recupera el estado sumidero (la papelera), garantizando su nomenclatura qN
    
    #Buscamos si ya existe el sumidero
    for estado in afd.estados:
        if hasattr(estado, 'es_sumidero') and estado.es_sumidero:
            return estado
            
    #Forzamos el contador global al ID secuencial que debería seguir (q4)
    global contador_estado_id
    contador_estado_id = next_sequential_id
    
    #Creamos el estado. Ahora, Estado() asignará 'q4'.
    sumidero = Estado() 
    
    #Garantizamos que el sumidero no sea de aceptación.
    sumidero.es_sumidero = True
    sumidero.aceptacion = False 

    #Agregamos transiciones de bucle para todo el alfabeto
    for simbolo in alfabeto:
        sumidero.agregar_transicion(simbolo, sumidero)

    #Añadir al autómata
    afd.agregar_estado(sumidero) 
    return sumidero

def afnd_a_afd(afnd):
    """Implementa el algoritmo de conversión de AFND a AFD."""
    alfabeto = sorted(list(afnd.obtener_alfabeto_simbolos()))
    afd = AFND()
    
    mapeo_estados = {} 
    conjuntos_sin_marcar = []

    #Estado inicial del AFD: Usamos q0
    q0_set = e_clausura({afnd.estado_inicial}, afnd)
    q0_afd = Estado(nombre="q0") # <-- Usamos 'q'

    #Reinicio/Sincronizacion del contador:
    #Aseguramos que el siguiente ID (para q1, q2...) comience en 1, 
    #ignorando el alto valor del contador global del AFND.
    estado_id = 1
    
    #Reemplazamos el contador global por el contador local (estado_id)
    from ER_AFND import contador_estado_id
    contador_estado_id = 1 
    
    afd.establecer_estado_inicial(q0_afd)
    afd.agregar_estado(q0_afd)
    mapeo_estados[frozenset(q0_set)] = q0_afd
    conjuntos_sin_marcar.append(q0_set)

    while conjuntos_sin_marcar:
        T = conjuntos_sin_marcar.pop(0)
        T_afd = mapeo_estados[frozenset(T)]

        if any(estado in T for estado in afnd.estados_aceptacion):
            T_afd.aceptacion = True

        for simbolo in alfabeto:
            U_mover = mover(T, simbolo)
            U_set = e_clausura(U_mover, afnd)

            if not U_set:
                estado_destino_afd = crear_estado_sumidero(afd, alfabeto,estado_id)
            else:
                if frozenset(U_set) not in mapeo_estados:
                    nombre_nuevo = f"q{estado_id}" #<-- Usamos 'q' y el contador local
                    U_afd = Estado(nombre=nombre_nuevo)
                    afd.agregar_estado(U_afd)
                    mapeo_estados[frozenset(U_set)] = U_afd
                    conjuntos_sin_marcar.append(U_set)
                    estado_id += 1
                estado_destino_afd = mapeo_estados[frozenset(U_set)]
            
            T_afd.agregar_transicion(simbolo, estado_destino_afd)

    #Reajustamos el contador global al final para que el sumidero, si fue creado,
    #mantenga el nombre que se le asignó.
    from ER_AFND import contador_estado_id
    contador_estado_id = estado_id + 1

    afd.estados_aceptacion = [e for e in afd.estados if e.aceptacion]
    return afd


# ============================================================
# AFND A AFD: FUNCIÓN DE REPORTE DE OCURRENCIAS
# ============================================================

def buscar_ocurrencias(afd, texto_entrada):
    """
    Simula la ejecución del AFD y reporta los calces válidos.
    Se reporta el calce más corto y válido desde cada posición de inicio.
    """
    lineas = texto_entrada.split('\n')
    reporte_final = {"Ocurrencias": []}
        
    for num_linea, linea in enumerate(lineas, start=1):
        linea_procesada = linea.strip() 
        
        if linea_procesada.endswith('-'):
            linea_procesada = linea_procesada[:-1].strip()
            
        ocurrencias_linea = []
        
        for i in range(len(linea_procesada)):
            estado_actual = afd.estado_inicial
            match_actual = ""
            
            for j in range(i, len(linea_procesada)):
                simbolo = linea_procesada[j]
                
                siguiente_estado = None
                if simbolo in estado_actual.transiciones:
                    destino_set = estado_actual.transiciones[simbolo]
                    if destino_set:
                        #En el AFD, solo hay un destino
                        siguiente_estado = list(destino_set)[0]
                
                if siguiente_estado is None or (hasattr(siguiente_estado, "es_sumidero") and siguiente_estado.es_sumidero):
                    break
                
                estado_actual = siguiente_estado
                match_actual += simbolo
                
                #Criterio de aceptación: Solo el estado_actual.aceptacion es necesario
                if estado_actual.aceptacion:
                    posicion = i + 1
                    ocurrencias_linea.append(f"{posicion} {match_actual}")
                    break 
            
        if ocurrencias_linea:
            reporte_final["Ocurrencias"].append(f"linea {num_linea}: {' '.join(ocurrencias_linea)}")

    print("Ocurrencias:")
    #La salida final es con el formato de línea: linea 1: 3 ab 5 ab 7 ab
    for reporte in reporte_final["Ocurrencias"]:
        print(reporte)
# ============================================================
# FUNCIÓN DE IMPRESIÓN DEL AFD (Formato Proyecto)
# ============================================================

def mostrar_afd_formato_proyecto(afd):
    """Muestra el AFD en el formato K={}, Sigma={}, delta: (q, s, q')"""
    if not afd.estado_inicial: return
    
    # Usamos la lista de estados del AFD
    k_list = sorted([estado.nombre for estado in afd.estados])
    k_str = "{" + ",".join(k_list) + "}"
    sigma_list = sorted(list(afd.obtener_alfabeto_simbolos()))
    sigma_str = "{" + ",".join(sigma_list) + "}"
    print(f"K={k_str}")
    print(f"Sigma={sigma_str}")
    print("delta:")
    
    delta_list = []
    for estado in afd.estados:
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                delta_list.append(f"({estado.nombre},{simbolo},{destino.nombre})")
    
    for transicion in sorted(delta_list):
        print(transicion)

    f_list = sorted([estado.nombre for estado in afd.estados_aceptacion])
    f_str = "{" + ",".join(f_list) + "}"
    
    print(f"s={afd.estado_inicial.nombre}")
    print(f"F={f_str}")

# ============================================================
# SIMULACIÓN PASO A PASO DEL AFD (para GUI)
# ============================================================

def simular_afd_generador(afd, texto_entrada):
    """
    Genera pasos atómicos para animar la detección:
      - Recorre línea por línea.
      - Para cada posición i en la línea, reinicia en s y avanza j>=i.
      - Emite cada transición (q, símbolo) -> q'.
      - Marca cuando llega a aceptación y corta esa sub-simulación.
    Yields: dict con {evento, linea, i, j, simbolo, q_from, q_to, aceptacion}
    """
    lineas = texto_entrada.split('\n')

    def _siguiente(q, simb):
        if simb in q.transiciones:
            destinos = q.transiciones[simb]
            if destinos:
                return next(iter(destinos))
        return None

    for idx_linea, linea in enumerate(lineas, start=1):
        raw = linea.rstrip('\n')
        #Regla del enunciado: '-' al final de línea es “continuación de texto” y no se consume
        if raw.endswith('-'):
            raw = raw[:-1]

        #Notificar nueva línea
        yield {"evento": "nueva_linea", "linea": idx_linea, "texto": raw}

        for i in range(len(raw)):
            #Notificar nuevo arranque en posición i
            yield {"evento": "nuevo_inicio", "linea": idx_linea, "i": i+1}

            q = afd.estado_inicial
            aceptado = False
            for j in range(i, len(raw)):
                simb = raw[j]
                q_next = _siguiente(q, simb)

                #Emitir transición
                yield {
                    "evento": "transicion",
                    "linea": idx_linea,
                    "i": i+1,
                    "j": j+1,
                    "simbolo": simb,
                    "q_from": q.nombre,
                    "q_to": None if q_next is None else q_next.nombre,
                    "aceptacion": False
                }

                if q_next is None:
                    break

                q = q_next

                if q.aceptacion:
                    aceptado = True
                    yield {
                        "evento": "aceptacion",
                        "linea": idx_linea,
                        "i": i+1,
                        "j": j+1,
                        "simbolo": simb,
                        "q_from": None,
                        "q_to": q.nombre,
                        "aceptacion": True
                    }
                    break  # “más corto válido” desde i
            #Fin sub-simulación i
            yield {
                "evento": "fin_inicio",
                "linea": idx_linea,
                "i": i+1,
                "resultado": "aceptado" if aceptado else "rechazado"
            }
        #Fin de línea
        yield {"evento": "fin_linea", "linea": idx_linea}
