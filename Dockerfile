FROM python:3.12

# Install dependencies and Microsoft repo
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https && \
    apt-get install -y iputils-ping && \
    apt-get install -y traceroute && \
    apt-get install -y netcat-openbsd && \ 
    apt-get install -y dnsutils && \ 
    apt-get install -y openssl && \ 
    mkdir -p /etc/apt/keyrings && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . swiss_army_container/

CMD ["uvicorn", "swiss_army_container.main:app", "--host", "0.0.0.0", "--port", "8000"]
