import threading
import time
from datetime import datetime, timedelta

# Variables globales para control
fracciones_generadas = 0
inicio_tiempo = None
stop_timer = False
lock = threading.Lock()

def mcd(a, b):
    """Calcula el Máximo Común Divisor usando el algoritmo de Euclides"""
    while b:
        a, b = b, a % b
    return a

def temporizador():
    """Hilo separado que muestra el tiempo transcurrido cada 10 segundos"""
    global fracciones_generadas, inicio_tiempo, stop_timer
    
    while not stop_timer:
        with lock:
            if inicio_tiempo and fracciones_generadas > 0:
                tiempo_transcurrido = time.time() - inicio_tiempo
                horas = int(tiempo_transcurrido // 3600)
                minutos = int((tiempo_transcurrido % 3600) // 60)
                segundos = int(tiempo_transcurrido % 60)
                
                velocidad = fracciones_generadas / tiempo_transcurrido
                
                print(f"\n[TIMER] Tiempo: {horas:02d}:{minutos:02d}:{segundos:02d} | "
                      f"Fracciones: {fracciones_generadas:,} | "
                      f"Velocidad: {velocidad:.2f} frac/seg")
        
        time.sleep(10)  # Actualiza cada 10 segundos

def sq(num, nombre_archivo="fracciones.txt"):
    """
    Genera fracciones únicas en forma reducida (mcd = 1)
    Utiliza threading para monitorear el progreso en paralelo
    Guarda todas las fracciones en un archivo .txt
    
    Args:
        num: Cantidad de fracciones a generar
        nombre_archivo: Nombre del archivo donde guardar las fracciones
    """
    global fracciones_generadas, inicio_tiempo, stop_timer
    
    # Inicia el hilo del temporizador
    stop_timer = False
    inicio_tiempo = time.time()
    hilo_timer = threading.Thread(target=temporizador, daemon=True)
    hilo_timer.start()
    
    print(f"Iniciando generación de {num:,} fracciones...")
    print(f"Guardando en: {nombre_archivo}")
    print("=" * 70)
    
    n = 1
    i2 = 0
    
    try:
        # Abre el archivo una sola vez para mejor rendimiento
        with open(nombre_archivo, 'w', buffering=8192) as archivo:
            while i2 < num:
                for i in range(n, 0, -1):
                    j = n - i + 1
                    divisor = mcd(i, j)
                    
                    if divisor == 1:
                        with lock:
                            # Escribe en archivo en lugar de mostrar en terminal
                            archivo.write(f"{i}/{j} {i/j:.6f}\n")
                            fracciones_generadas += 1
                            i2 += 1
                        
                        if i2 == num:
                            break
                n += 1
    
    except KeyboardInterrupt:
        print("\n[!] Generación interrumpida por el usuario")
    
    except IOError as e:
        print(f"\n[ERROR] No se pudo escribir en el archivo: {e}")
    
    finally:
        # Detiene el temporizador
        stop_timer = True
        hilo_timer.join(timeout=1)
        
        # Muestra estadísticas finales
        tiempo_total = time.time() - inicio_tiempo
        horas = int(tiempo_total // 3600)
        minutos = int((tiempo_total % 3600) // 60)
        segundos = int(tiempo_total % 60)
        
        print("\n" + "=" * 70)
        print(f"[COMPLETADO] Se generaron {fracciones_generadas:,} fracciones")
        print(f"[TIEMPO TOTAL] {horas:02d}:{minutos:02d}:{segundos:02d}")
        print(f"[VELOCIDAD PROMEDIO] {fracciones_generadas/tiempo_total:.2f} fracciones/segundo")
        print(f"[ARCHIVO] Guardado en: {nombre_archivo}")
        print("=" * 70)

if __name__ == "__main__":
    # Genera 2,000,000 de fracciones con monitoreo en tiempo real
    # Las fracciones se guardan en fracciones.txt
    sq(2000000)
    
    # Alternativa: especificar un nombre de archivo personalizado
    # sq(2000000, "mis_fracciones.txt")
