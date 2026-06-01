# 🔐 Chat P2P con Cifrado Híbrido RSA + AES

Sistema de mensajería punto a punto con cifrado híbrido. Implementa RSA-2048 para el intercambio seguro de claves y AES-256-CBC para el cifrado de mensajes en tiempo real. La comunicación ocurre directamente entre dos nodos sin servidor intermedio.

---

## ⚙️ Arquitectura

```
[Servidor (msg1.py)]                    [Cliente (Crypto_Talk.py)]
        |                                           |
        |--- pub_servidor.pem + firma PSS --------->|
        |<-- pub_cliente.pem ------------------------|
        |--- clave AES cifrada con RSA-OAEP ------->|
        |                                           |
        |<====== Mensajes cifrados con AES-CBC ====>|
```

**Flujo de handshake:**
1. El servidor genera un par de claves RSA y firma su clave pública con PSS.
2. El cliente verifica la firma para descartar ataques Man-in-the-Middle.
3. El servidor genera una clave AES aleatoria de 256 bits, la cifra con la clave pública del cliente (RSA-OAEP) y la envía.
4. Ambos nodos cifran y descifran mensajes con AES-CBC usando esa clave compartida.

---

## 🛠️ Tecnologías

- **Python 3.10+**
- [`cryptography`](https://cryptography.io/) — RSA, AES, OAEP, PSS
- [`prompt_toolkit`](https://python-prompt-toolkit.readthedocs.io/) — interfaz de entrada en terminal
- `socket` / `threading` — comunicación y concurrencia

---

## 🚀 Instalación y uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/mborquezbustamante/Proyectos-personales-y-universitarios.git
cd Proyectos-personales-y-universitarios/chat-p2p-rsa-aes
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```bash
python msg1.py
```

### 4. Ejecutar el cliente (en otra terminal o equipo)
```bash
python Crypto_Talk.py
# Ingresar la IP del servidor cuando lo solicite
```

> Para probar en local, usar `127.0.0.1` como IP.

---

## 🔒 Seguridad

| Componente | Algoritmo | Detalle |
|---|---|---|
| Intercambio de clave | RSA-2048 + OAEP | SHA-256 como hash |
| Autenticación de clave | RSA-PSS | Firma de la clave pública del servidor |
| Cifrado de mensajes | AES-256-CBC | IV aleatorio por mensaje |
| Padding | PKCS7 | Para bloques AES |

> ⚠️ Los archivos `.pem` se generan localmente y están excluidos del repositorio por `.gitignore`. **Nunca compartir las claves privadas.**

---

## 📁 Estructura

```
chat-p2p-rsa-aes/
├── msg1.py            # Nodo servidor
├── Crypto_Talk.py     # Nodo cliente
├── requirements.txt   # Dependencias
├── .gitignore         # Excluye claves .pem y caché
└── README.md          # Este archivo
```

---

## 👤 Autor

**Matías Bórquez Bustamante**  
Ingeniería Civil en Informática y Telecomunicaciones — Universidad Finis Terrae  
📧 mborquezb@uft.edu
