# Usa una imagen oficial de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo requirements.txt y luego instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de la carpeta actual al contenedor
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
