# ============================================================
# PARÁMETROS GLOBALES Y CONSTANTES
# ============================================================
contador_estado_id = 0 
OPERADORES = {'.', '|', '*'}
PRECEDENCIA = {'|': 1, '.': 2, '*': 3}
ASOCIATIVIDAD = {'|': 'izquierda', '.': 'izquierda', '*': 'derecha'}
ALFABETO_BUSQUEDA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" # Alfabeto para la búsqueda [cite: 29]

# ============================================================
# CLASE ESTADO
# ============================================================
class Estado:
    """
    Clase que representa un estado en un autómata.
    """
    def __init__(self, nombre=None):
        global contador_estado_id
        if nombre is None:
            self.nombre = f"q{contador_estado_id}"
            contador_estado_id += 1
        else:
            self.nombre = nombre 
            
        self.transiciones = {}
        self.aceptacion = False

    def agregar_transicion(self, simbolo, estado):
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = set()
        self.transiciones[simbolo].add(estado)


# ============================================================
# CLASE AFND
# ============================================================
class AFND:
    """
    Clase que representa un autómata finito no determinista (AFND).
    """
    def __init__(self):
        self.estados = []
        self.estado_inicial = None
        self.estados_aceptacion = []

    def agregar_estado(self, estado):
        if estado not in self.estados:
            self.estados.append(estado)
        
        if estado.aceptacion and estado not in self.estados_aceptacion:
            self.estados_aceptacion.append(estado)

    def establecer_estado_inicial(self, estado):
        self.estado_inicial = estado

    def obtener_alfabeto_simbolos(self):
        """Retorna el alfabeto no-epsilon del AFND."""
        simbolos = set()
        for estado in self.estados:
            for simbolo in estado.transiciones.keys():
                if simbolo:  # Ignorar epsilon ('')
                    simbolos.add(simbolo)
        return simbolos


# ============================================================
# FUNCIÓN DE IMPRESIÓN EN FORMATO PROYECTO (ULTRA-FILTRADA)
# ============================================================
def mostrar_afnd_formato_proyecto(afnd):
    """
    Muestra el AFND con filtrado, mapeando s y F a estados secuenciales
    para una salida limpia, asumiendo que q0 es el inicio y q_ultimo es el fin.
    """
    if not afnd.estado_inicial:
        print("Error: No hay estado inicial asignado.")
        return

    # 1. Definir los prefijos de los estados auxiliares que queremos ocultar
    AUXILIAR_PREFIXES = ("q_inicial_", "q_aceptacion_")
    
    # 2. Filtrar Estados (K) y Transiciones (Delta)
    estados_filtrados = []
    
    for estado in afnd.estados:
        if not estado.nombre.startswith(AUXILIAR_PREFIXES):
            estados_filtrados.append(estado)

    # Recolectar transiciones (Delta) filtrando auxiliares en origen/destino
    transiciones_filtradas = []
    for estado in afnd.estados:
        es_origen_aux = estado.nombre.startswith(AUXILIAR_PREFIXES)
        
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                es_destino_aux = destino.nombre.startswith(AUXILIAR_PREFIXES)
                if not es_origen_aux and not es_destino_aux:
                    simbolo_proyecto = simbolo if simbolo else '_' 
                    transiciones_filtradas.append(f"({estado.nombre},{simbolo_proyecto},{destino.nombre})")

    # 3. Impresión del AFND Limpio
    k_list = sorted([estado.nombre for estado in estados_filtrados])
    k_str = "{" + ",".join(k_list) + "}"
    sigma_list = sorted(list(afnd.obtener_alfabeto_simbolos()))
    sigma_str = "{" + ",".join(sigma_list) + "}"
    
    # Mapeamos s y F a los estados visibles
    s_nombre_limpio = k_list[0] if k_list else "q0"
    f_nombre_limpio = k_list[-1] if k_list else "q0"
    f_str_limpio = "{" + f_nombre_limpio + "}"

    print(f"K={k_str} \nSigma={sigma_str}")
    print("Delta:")
    for transicion in sorted(transiciones_filtradas):
        print(transicion)
    print(f"s={s_nombre_limpio} \nF={f_str_limpio}")
# ============================================================
# CONSTRUCCIÓN DE THOMSON Y MODIFICACIÓN PARA BÚSQUEDA
# ============================================================
ALFABETO_SIGMA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def construir_AFND_simple(simbolo):
    # ----------------------------------------------------
    # 1. MANEJO DE EPSILON ( _ ) - Acepta la cadena vacía
    # ----------------------------------------------------
    if simbolo == '_':
        estado_inicial = Estado()
        estado_aceptacion = Estado()
        estado_aceptacion.aceptacion = True
        
        # Transición epsilon: acepta la cadena vacía
        estado_inicial.agregar_transicion('', estado_aceptacion) 
        
        afnd = AFND()
        afnd.agregar_estado(estado_inicial)
        afnd.agregar_estado(estado_aceptacion)
        afnd.establecer_estado_inicial(estado_inicial)
        return afnd
    
    # ----------------------------------------------------
    # 2. MANEJO DE CONJUNTO VACÍO ( 0 ) - No acepta nada
    # ----------------------------------------------------
    if simbolo == '0':
        estado_inicial = Estado()
        estado_aceptacion = Estado()
        estado_aceptacion.aceptacion = True # No tiene transiciones
        
        # No se agrega ninguna transición
        
        afnd = AFND()
        afnd.agregar_estado(estado_inicial)
        afnd.agregar_estado(estado_aceptacion)
        afnd.establecer_estado_inicial(estado_inicial)
        return afnd
        
    # ----------------------------------------------------
    # 3. MANEJO DE ALFABETO COMPLETO ( Σ ) - Acepta cualquier letra
    # ----------------------------------------------------
    if simbolo == 'Σ':
        estado_inicial = Estado()
        estado_aceptacion = Estado()
        estado_aceptacion.aceptacion = True
        
        afnd = AFND()
        afnd.agregar_estado(estado_inicial)
        afnd.agregar_estado(estado_aceptacion)
        afnd.establecer_estado_inicial(estado_inicial)
        
        # Agrega una transición para CADA símbolo del alfabeto.
        for char in ALFABETO_SIGMA:
            estado_inicial.agregar_transicion(char, estado_aceptacion)
            
        return afnd
        
    # ----------------------------------------------------
    # Lógica Original para Literales (a, b, c, etc.)
    # ----------------------------------------------------
    estado_inicial = Estado()
    estado_aceptacion = Estado()
    estado_aceptacion.aceptacion = True
    estado_inicial.agregar_transicion(simbolo, estado_aceptacion)
    afnd = AFND()
    afnd.agregar_estado(estado_inicial)
    afnd.agregar_estado(estado_aceptacion)
    afnd.establecer_estado_inicial(estado_inicial)
    return afnd
def unir_AFND(afnd1, afnd2):
    # ANTES: Estado("q_inicial_U")
    estado_inicial = Estado()
    # ANTES: Estado("q_aceptacion_U")
    estado_aceptacion = Estado()
    estado_aceptacion.aceptacion = True
    estado_inicial.agregar_transicion('', afnd1.estado_inicial)  
    estado_inicial.agregar_transicion('', afnd2.estado_inicial)
    for estado in afnd1.estados_aceptacion:
        estado.agregar_transicion('', estado_aceptacion)
        estado.aceptacion = False
    for estado in afnd2.estados_aceptacion:
        estado.agregar_transicion('', estado_aceptacion)
        estado.aceptacion = False
    afnd = AFND()
    afnd.establecer_estado_inicial(estado_inicial)
    afnd.agregar_estado(estado_inicial)
    afnd.agregar_estado(estado_aceptacion)
    for estado in afnd1.estados + afnd2.estados:
        afnd.agregar_estado(estado)
    return afnd

def concatenar_AFND(afnd1, afnd2):
    for estado in afnd1.estados_aceptacion:
        estado.agregar_transicion('', afnd2.estado_inicial)
        estado.aceptacion = False
    afnd = AFND()
    for estado in afnd1.estados + afnd2.estados:
        afnd.agregar_estado(estado)
    afnd.estados_aceptacion = afnd2.estados_aceptacion
    afnd.establecer_estado_inicial(afnd1.estado_inicial)
    return afnd

def kleene_AFND(afnd):
    # ANTES: Estado("q_inicial_K")
    estado_inicial = Estado()
    # ANTES: Estado("q_aceptacion_K")
    estado_aceptacion = Estado()
    estado_aceptacion.aceptacion = True
    estado_inicial.agregar_transicion('', afnd.estado_inicial)
    estado_inicial.agregar_transicion('', estado_aceptacion)
    for estado in afnd.estados_aceptacion:
        estado.agregar_transicion('', afnd.estado_inicial)
        estado.agregar_transicion('', estado_aceptacion)
        estado.aceptacion = False
    afnd_resultado = AFND()
    afnd_resultado.establecer_estado_inicial(estado_inicial)
    afnd_resultado.agregar_estado(estado_inicial)
    afnd_resultado.agregar_estado(estado_aceptacion)
    for estado in afnd.estados:
        afnd_resultado.agregar_estado(estado)
    afnd_resultado.estados_aceptacion = [estado_aceptacion]
    return afnd_resultado

def agregar_busqueda_flotante(afnd, er_original):
    """
    Modifica el AFND para búsqueda flotante (rizos en el estado inicial).
    Utiliza un alfabeto de búsqueda reducido (símbolos en la ER) para una salida corta 
    que se parezca más al ejemplo, que solo lista a y b en los rizos[cite: 43, 44].
    """
    estado_inicial = afnd.estado_inicial
    if estado_inicial is None:
        return

    # Usamos solo los símbolos del patrón para los rizos de búsqueda
    alfabeto_er = set()
    for char in er_original:
        if operando_valido(char):
            alfabeto_er.add(char)
    alfabeto_rizo = alfabeto_er
        
    for simbolo in alfabeto_rizo:
        estado_inicial.agregar_transicion(simbolo, estado_inicial)

# ============================================================
# FUNCIONES DE SHUNTING-YARD
# ============================================================
def operando_valido(caracter):
    return (
        ('a' <= caracter <= 'z') or
        ('A' <= caracter <= 'Z') or
        (caracter in {'_', '0', 'Σ'})
    )

def Tokenizar(ER):
    ER = ER.replace(" ", "")
    tokens = []
    for ch in ER:
        if ch in ('(', ')') or ch in OPERADORES or operando_valido(ch):
            tokens.append(ch)
        else:
            raise ValueError(f"Símbolo inválido: {ch}")
    return tokens

def agregar_concatenaciones(tokens):
    if not tokens: return []
    res = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i+1]
        res.append(a)
        if (operando_valido(a) or a in {')', '*'}) and (operando_valido(b) or b == '('):
            res.append('.')
    res.append(tokens[-1])
    return res

def APostfija(ER: str):
    tokens = Tokenizar(ER)
    tokens = agregar_concatenaciones(tokens)
    salida = []
    pila = []
    for tok in tokens:
        if operando_valido(tok): salida.append(tok)
        elif tok == '(': pila.append(tok)
        elif tok == ')':
            while pila and pila[-1] != '(': salida.append(pila.pop())
            if not pila: raise ValueError("Paréntesis desbalanceados: falta '('")
            pila.pop()
        elif tok in OPERADORES:
            while (pila and pila[-1] in OPERADORES and
                (PRECEDENCIA[pila[-1]] > PRECEDENCIA[tok] or
                (PRECEDENCIA[pila[-1]] == PRECEDENCIA[tok] and ASOCIATIVIDAD[tok] == 'izquierda'))):
                salida.append(pila.pop())
            pila.append(tok)
    while pila:
        op = pila.pop()
        if op in {'(', ')'}: raise ValueError("Paréntesis desbalanceados.")
        salida.append(op)
    return salida

def convertir_ER_a_AFND(er):
    global contador_estado_id 
    contador_estado_id = 0
    er_postfija = APostfija(er)
    pila = []
    for simbolo in er_postfija:
        if operando_valido(simbolo): afnd = construir_AFND_simple(simbolo); pila.append(afnd)
        elif simbolo == '.':
            if len(pila) < 2: raise ValueError("Error de sintaxis: faltan operandos para la concatenación.")
            afnd2 = pila.pop(); afnd1 = pila.pop(); afnd = concatenar_AFND(afnd1, afnd2); pila.append(afnd)
        elif simbolo == '|':
            if len(pila) < 2: raise ValueError("Error de sintaxis: faltan operandos para la unión.")
            afnd2 = pila.pop(); afnd1 = pila.pop(); afnd = unir_AFND(afnd1, afnd2); pila.append(afnd)
        elif simbolo == '*':
            if len(pila) < 1: raise ValueError("Error de sintaxis: falta operando para Kleene.")
            afnd = pila.pop(); afnd = kleene_AFND(afnd); pila.append(afnd)
    if len(pila) != 1: raise ValueError("No se ha generado un único AFND. Algo salió mal.")
    afnd_resultante = pila.pop()
    if afnd_resultante.estado_inicial is None: raise ValueError("No se ha asignado un estado inicial al AFND.")
    return afnd_resultante

# ============================================================
# FUNCIONES DE SHUNTING-YARD
# ============================================================
def operando_valido(caracter):
    return (
        ('a' <= caracter <= 'z') or
        ('A' <= caracter <= 'Z') or
        (caracter in {'_', '0', 'Σ'})
    )

def Tokenizar(ER):
    ER = ER.replace(" ", "")
    tokens = []
    for ch in ER:
        if ch in ('(', ')') or ch in OPERADORES or operando_valido(ch):
            tokens.append(ch)
        else:
            raise ValueError(f"Símbolo inválido: {ch}")
    return tokens

def agregar_concatenaciones(tokens):
    if not tokens: return []
    res = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i+1]
        res.append(a)
        if (operando_valido(a) or a in {')', '*'}) and (operando_valido(b) or b == '('):
            res.append('.')
    res.append(tokens[-1])
    return res

def APostfija(ER: str):
    tokens = Tokenizar(ER)
    tokens = agregar_concatenaciones(tokens)
    salida = []
    pila = []
    for tok in tokens:
        if operando_valido(tok): salida.append(tok)
        elif tok == '(': pila.append(tok)
        elif tok == ')':
            while pila and pila[-1] != '(': salida.append(pila.pop())
            if not pila: raise ValueError("Paréntesis desbalanceados: falta '('")
            pila.pop()
        elif tok in OPERADORES:
            while (pila and pila[-1] in OPERADORES and
                (PRECEDENCIA[pila[-1]] > PRECEDENCIA[tok] or
                (PRECEDENCIA[pila[-1]] == PRECEDENCIA[tok] and ASOCIATIVIDAD[tok] == 'izquierda'))):
                salida.append(pila.pop())
            pila.append(tok)
    while pila:
        op = pila.pop()
        if op in {'(', ')'}: raise ValueError("Paréntesis desbalanceados.")
        salida.append(op)
    return salida

def convertir_ER_a_AFND(er):
    global contador_estado_id 
    contador_estado_id = 0
    er_postfija = APostfija(er)
    pila = []
    for simbolo in er_postfija:
        if operando_valido(simbolo): afnd = construir_AFND_simple(simbolo); pila.append(afnd)
        elif simbolo == '.':
            if len(pila) < 2: raise ValueError("Error de sintaxis: faltan operandos para la concatenación.")
            afnd2 = pila.pop(); afnd1 = pila.pop(); afnd = concatenar_AFND(afnd1, afnd2); pila.append(afnd)
        elif simbolo == '|':
            if len(pila) < 2: raise ValueError("Error de sintaxis: faltan operandos para la unión.")
            afnd2 = pila.pop(); afnd1 = pila.pop(); afnd = unir_AFND(afnd1, afnd2); pila.append(afnd)
        elif simbolo == '*':
            if len(pila) < 1: raise ValueError("Error de sintaxis: falta operando para Kleene.")
            afnd = pila.pop(); afnd = kleene_AFND(afnd); pila.append(afnd)
    if len(pila) != 1: raise ValueError("No se ha generado un único AFND. Algo salió mal.")
    afnd_resultante = pila.pop()
    if afnd_resultante.estado_inicial is None: raise ValueError("No se ha asignado un estado inicial al AFND.")
    return afnd_resultante