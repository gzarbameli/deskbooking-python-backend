# Usa un'immagine base di Python
FROM python:3.9

# Copia il file dei requisiti
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione nell'immagine
COPY . .

# Esponi la porta 5000
EXPOSE 5000

# Comando per eseguire l'applicazione
CMD ["python", "app.py"]