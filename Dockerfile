FROM python:3.13-slim

# Instala herramientas necesarias para agregar repositorios
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg2 apt-transport-https

# Agrega la clave GPG de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Agrega el repositorio de Microsoft (reemplaza buster, bullseye, etc. según tu versión base)
RUN curl https://packages.microsoft.com/config/debian/11/prod.list \
    > /etc/apt/sources.list.d/msprod.list

# Instala el driver ODBC de Microsoft y unixODBC
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17 \
    unixodbc-dev

# Limpieza opcional
RUN rm -rf /var/lib/apt/lists/*

# A partir de aquí, ya puedes instalar pyodbc y el resto de tu proyecto
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]


