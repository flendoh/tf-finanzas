FROM odoo:18.0

# Cambiar a usuario root para instalar paquetes
USER root

COPY ./requirements.txt .

# Instalar librerías requeridas
RUN apt-get update && apt-get install -y \
    python-is-python3 \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    python3-dev \
    build-essential \
    python3-pypdf2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt && rm requirements.txt

# Volver al usuario odoo
USER odoo

# Exponer el puerto 8069
EXPOSE 8069

# Comando por defecto
CMD ["odoo"]