#------------------------------------------------------------------
# INTRODUCIR ER
#------------------------------------------------------------------
def introducir_er(er: str):
    print("Iniciando validación de la ER...")  # Mensaje de depuración
    if er is None:
        raise ValueError("No se ingresó ninguna expresión regular")

    er = er.strip()
    if er == "":
        raise ValueError("No se ingresó ninguna expresión regular")

    # Caracteres permitidos: letras/dígitos, '_', '0'(Representa conjunto vacio), operadores . | * ( )
    Operadores = {'.', '|', '*', '(', ')'} # Operadores permitidos
    simbolos_especiales = {'_', '0'}  # _ (Epsilon)y 0 (vacío) son permitidos
    
    #--------------------------------------------------------------------------------
    # 1. Validación de caracteres permitidos
    #--------------------------------------------------------------------------------
    for caracter in er:
        if caracter.isalnum():
            continue
        if caracter in Operadores or caracter in simbolos_especiales:
            continue
        if caracter.isspace():
            continue
        raise ValueError(f"Carácter no permitido en la ER: '{caracter}'")

    #--------------------------------------------------------------------------------
    # 2. Verificación de paréntesis desbalanceados
    #--------------------------------------------------------------------------------
    stack = []
    for caracter in er:
        if caracter == '(':
            stack.append(caracter)
        elif caracter == ')':
            if not stack:
                raise ValueError("Paréntesis desbalanceados: hay un ')' sin su '('")
            stack.pop()
    if stack:
        raise ValueError("Paréntesis desbalanceados: falta ')'")

    #--------------------------------------------------------------------------------
    # 3. Verificación de la colocación de operadores
    #--------------------------------------------------------------------------------
    for i in range(len(er)):
        # Validación de operadores binarios (., |)
        if er[i] in {'.', '|'}: 
            if i == 0 or i == len(er) - 1 or er[i-1] in {'.', '|', '(', ')'} or er[i+1] in {'.', '|', '(', ')'}:
                raise ValueError(f"Operador '{er[i]}' mal colocado en la ER")
        # Validación del operador unario (*)
        if er[i] in {'*'}:  
            if i == 0 or er[i-1] in {'.', '|', '*', '('}:
                raise ValueError(f"Operador '{er[i]}' mal colocado, debe seguir un operando o cerrar paréntesis")

    #--------------------------------------------------------------------------------
    # 4. Verificación de inicio/fin con operadores incorrectos
    #--------------------------------------------------------------------------------
    if er[0] in {'.', '|', '*'}:
        raise ValueError("La ER no puede comenzar con un operador binario o unario")
    if er[-1] in {'.', '|'}:
        raise ValueError("La ER no puede terminar con un operador binario")

    # Devolver ER normalizada (sin espacios extras)
    return "".join(er.split())

