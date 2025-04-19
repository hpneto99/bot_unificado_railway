
FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y wget gnupg unzip     && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -     && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'     && apt-get update && apt-get install -y google-chrome-stable     && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver compatível
RUN CHROME_VERSION=$(google-chrome --version | sed 's/[^0-9.]//g' | cut -d. -f1) &&     wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(wget -q -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")/chromedriver_linux64.zip &&     unzip /tmp/chromedriver.zip -d /usr/local/bin &&     rm /tmp/chromedriver.zip

# Criar diretório do app
WORKDIR /app
COPY . /app

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Porta padrão da Railway
EXPOSE 8080

# Executar o bot
CMD ["python", "bot_unificado.py"]
