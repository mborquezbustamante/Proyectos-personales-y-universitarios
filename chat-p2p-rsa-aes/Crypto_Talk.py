import socket
import threading
import time
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

stop_event = threading.Event()
path = os.getcwd()
clave_privada = "priv_cliente.pem"
clave_publica = "pub_cliente.pem"
path_priv = os.path.join(path, clave_privada)
path_pub = os.path.join(path, clave_publica)

def rsa_claves():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def guardar_clave_pem(filename, key, private=False):
    if os.path.exists(filename):
        return  # No sobrescribir si ya existe
    if private:
        data = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        data = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    with open(filename, "wb") as f:
        f.write(data)

def cargar_clave_pem(filename, private=False):
    with open(filename, "rb") as f:
        data = f.read()
        if private:
            return serialization.load_pem_private_key(data, password=None)
        else:
            return serialization.load_pem_public_key(data)

def aes_encrypt(key, iv, plaintext):
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()

def aes_decrypt(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    return unpadder.update(padded_plaintext) + unpadder.finalize()

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def verificar_firma(pub_key, datos_bytes, firma):
    try:
        pub_key.verify(
            firma,
            datos_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def recibir_mensajes(sock, session, aes_key):
    try:
        while not stop_event.is_set():
            datos = sock.recv(4096)
            if not datos:
                print("[!] El servidor cerró la conexión.", flush=True)
                stop_event.set()
                try:
                    if session.app and session.app.is_running:
                        session.app.exit()
                except Exception:
                    pass
                break

            try:
                if session.app and session.app.is_running:
                    session.app.exit()
            except Exception:
                pass

            iv = datos[:16]
            mensaje_cifrado = datos[16:]
            respuesta = aes_decrypt(aes_key, iv, mensaje_cifrado).decode('utf-8', errors="replace")

            # Mantenemos el condicional para "meow"
            if respuesta.lower() == "meow":
                print("\nEl servidor pidió abrir un enlace:")
                os.system('start https://www.youtube.com/shorts/vfUhm_XK8lc')
                continue


            if respuesta == "exit":
                print("El servidor solicitó cerrar la conexión.", flush=True)
                stop_event.set()
                try:
                    if session.app and session.app.is_running:
                        session.app.exit()
                except Exception:
                    pass
                break

            print(f"\n[Servidor]: {respuesta}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        stop_event.set()
        try:
            if session.app and session.app.is_running:
                session.app.exit()
        except Exception:
            pass

def enviar_mensajes(sock, session, aes_key):
    try:
        with patch_stdout():
            while not stop_event.is_set():
                mensaje = session.prompt("[Tú]: ")
                if mensaje is None:
                    continue
                iv = os.urandom(16)
                mensaje_cifrado = aes_encrypt(aes_key, iv, mensaje)
                sock.sendall(iv + mensaje_cifrado)
                if mensaje == "exit":
                    stop_event.set()
                    break
    except Exception as e:
        print(f"[!] Error en enviar mensaje: {e}", flush=True)
        stop_event.set()

def main(ip):
    cliente = socket.socket()
    while True:
        try:
            cliente.connect((ip, 4444))
            print("Conectado :)", flush=True)
            break
        except Exception:
            print("Esperando conexión...", flush=True)
            time.sleep(1)

    # Crear claves si no existen
    if not os.path.exists(path_priv) or not os.path.exists(path_pub):
        priv_cliente, pub_cliente = rsa_claves()
        guardar_clave_pem(path_priv, priv_cliente, True)
        guardar_clave_pem(path_pub, pub_cliente, False)
    else:
        priv_cliente = cargar_clave_pem(path_priv, True)
        pub_cliente = cargar_clave_pem(path_pub, False)

    # Enviar clave pública al servidor
    pub_cliente_bytes = pub_cliente.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    cliente.sendall(pub_cliente_bytes)

    # Recibir longitud de clave pública (4 bytes)
    len_pub_servidor_bytes = recvall(cliente, 4)
    if len_pub_servidor_bytes is None:
        raise Exception("Error recibiendo longitud clave pública servidor")
    len_pub_servidor = int.from_bytes(len_pub_servidor_bytes, 'big')

    # Recibir clave pública del servidor
    pub_servidor_pem = recvall(cliente, len_pub_servidor)
    if pub_servidor_pem is None:
        raise Exception("Error recibiendo clave pública servidor")

    # Recibir longitud de la firma (4 bytes)
    len_firma_bytes = recvall(cliente, 4)
    if len_firma_bytes is None:
        raise Exception("Error recibiendo longitud firma servidor")
    len_firma = int.from_bytes(len_firma_bytes, 'big')

    # Recibir firma
    firma = recvall(cliente, len_firma)
    if firma is None:
        raise Exception("Error recibiendo firma servidor")

    # Cargar la clave pública del servidor
    pub_servidor = serialization.load_pem_public_key(pub_servidor_pem)

    # Verificar la firma
    if verificar_firma(pub_servidor, pub_servidor_pem, firma):
        print("Clave pública verificada correctamente")
    else:
        print("ERROR: Firma inválida. Posible ataque MitM")
        cliente.close()
        return

    # Guardar la clave pública verificada
    with open("pub_servidor.pem", "wb") as f:
        f.write(pub_servidor_pem)

    # Recibir clave AES cifrada (usar función recvall para garantizar lectura completa)
    clave_aes_cifrada = recvall(cliente, 256)
    if clave_aes_cifrada is None:
        raise Exception("No se recibió la clave AES completa")

    # Descifrar clave AES con clave privada
    clave_aes = priv_cliente.decrypt(
        clave_aes_cifrada,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    session = PromptSession()

    recibir = threading.Thread(target=recibir_mensajes, args=(cliente, session, clave_aes))
    recibir.start()

    enviar_mensajes(cliente, session, clave_aes)

    recibir.join()
    try:
        cliente.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    cliente.close()


if __name__ == "__main__":
    ip = input("Ingresa la ip:")
    main(ip)
