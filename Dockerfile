FROM python:3.9-slim

# Instalar dependências para o Chromium e outras bibliotecas
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxtst6 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Setando o diretório de trabalho no container
WORKDIR /app

# Copiando o arquivo de requisitos para o container
COPY requirements.txt .

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiando o código-fonte para dentro do container
COPY . .

# Expondo a porta 8000 para acessar a aplicação
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI
CMD ["uvicorn", "automation.app:app", "--host", "0.0.0.0", "--port", "8000"]