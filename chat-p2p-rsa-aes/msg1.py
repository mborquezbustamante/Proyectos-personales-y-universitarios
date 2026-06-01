import socket
import threading
import time
import os
import hashlib
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

stop_event = threading.Event()
path = os.getcwd()
clave_privada = "priv_servidor.pem"
clave_publica = "pub_servidor.pem"
path_priv = os.path.join(path, clave_privada)
path_pub = os.path.join(path, clave_publica)

def rsa_claves():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def guardar_clave_pem(filename, key, private=False):
    if private:
        if os.path.exists(filename):
            return
        data = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        if os.path.exists(filename):
            return
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

def firmar_clave_privada(priv_key, datos_bytes):
    return priv_key.sign(
        datos_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def recibir_mensajes(sock, session, aes_key):
    try:
        while not stop_event.is_set():
            datos = sock.recv(4096)
            if not datos:
                print("[!] El cliente cerró la conexión.", flush=True)
                stop_event.set()
                try:
                    if session.app and session.app.is_running:
                        session.app.exit()
                except Exception:
                    pass
                break
            iv = datos[:16]
            mensaje_cifrado = datos[16:]
            respuesta = aes_decrypt(aes_key, iv, mensaje_cifrado).decode('utf-8', errors="replace")

            if respuesta == "exit":
                print("Cliente escribió exit. Cerrando conexión.", flush=True)
                stop_event.set()
                try:
                    if session.app and session.app.is_running:
                        session.app.exit()
                except Exception:
                    pass
                break

            print(f"\n[Cliente]: {respuesta}", flush=True)
    except Exception as e:
        print(f"[!] Error en recibir: {e}", flush=True)
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
    except Exception as e:
        print(f"[!] Error en enviar: {e}", flush=True)
        stop_event.set()

def main():
    server = socket.socket()
    server.bind(("0.0.0.0", 4444))
    server.listen(1)
    print("[+] Esperando conexión del cliente...", flush=True)
    cliente, direccion = server.accept()

    # Crear claves si no existen
    if not os.path.exists(path_priv) or not os.path.exists(path_pub):
        priv_servidor, pub_servidor = rsa_claves()
        guardar_clave_pem(path_priv, priv_servidor, True)
        guardar_clave_pem(path_pub, pub_servidor, False)
    else:
        priv_servidor = cargar_clave_pem(path_priv, True)
        pub_servidor = cargar_clave_pem(path_pub, False)

    # Recibir clave pública cliente
    pub_cliente_pem = cliente.recv(2048)
    pub_cliente = serialization.load_pem_public_key(pub_cliente_pem)

    # Guardar clave pública cliente correctamente
    with open("pub_cliente.pem", "wb") as f:
        f.write(pub_cliente_pem)

    # Enviar clave pública servidor al cliente
    pub_servidor_bytes = pub_servidor.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    firma = firmar_clave_privada(priv_servidor, pub_servidor_bytes)

    # Enviar clave pública servidor y firma (con longitudes)
    cliente.sendall(len(pub_servidor_bytes).to_bytes(4, 'big') + pub_servidor_bytes)
    cliente.sendall(len(firma).to_bytes(4, 'big') + firma)

    # Generar clave AES para sesión
    key_aes = os.urandom(32)

    # Encriptar clave AES con clave pública cliente y enviar
    clave_aes_encriptada = pub_cliente.encrypt(
        key_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    cliente.sendall(clave_aes_encriptada)

    print(f"[+] Cliente conectado desde {direccion}", flush=True)

    session = PromptSession()

    # Aquí pasamos la clave AES DESCIFRADA (key_aes), no la cifrada
    recibir = threading.Thread(target=recibir_mensajes, args=(cliente, session, key_aes))
    recibir.start()

    # Enviar mensajes con la clave AES DESCIFRADA
    enviar_mensajes(cliente, session, key_aes)

    recibir.join()
    try:
        server.shutdown(socket.SHUT_RDWR)
    except:
        pass
    cliente.close()
    server.close()
    print("[+] Servidor cerrado", flush=True)

if __name__ == "__main__":
    main()
