FROM python:3.11-slim

# Sistem araçları kur (tüm derleyiciler + Wine)
RUN apt-get update && apt-get install -y \
    wine wine64 \
    build-essential g++ mingw-w64 \
    wget curl git unzip \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Rust kur
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup target add x86_64-pc-windows-gnu

# .NET 8 SDK kur (C# için)
RUN wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh && \
    chmod +x dotnet-install.sh && \
    ./dotnet-install.sh --channel 8.0 && \
    rm dotnet-install.sh
ENV PATH="/root/.dotnet:${PATH}"

# Wine'ı başlat
RUN wineboot --init || true

# Python paketleri
RUN pip install --no-cache-dir streamlit pyinstaller

# Çalışma dizini
WORKDIR /app

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
