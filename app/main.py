from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import accounts, discoverybusiness, csrftoken 
from fastapi.middleware.trustedhost import TrustedHostMiddleware



app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:3000",  # Permitir solicitudes desde React
    "http://localhost:8501",  # Permitir solicitudes desde Streamlit
    "https://spygram-frontend.vercel.app"
    # Agrega aquí otros orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Asegúrate de que esta lista contenga todos los orígenes permitidos
    allow_credentials=True,  # Permitir el envío de cookies
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Añadir el middleware de TrustedHost
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Cambia "*" por tu dominio permitido si quieres restringir el acceso
)



app.include_router(accounts.router)
app.include_router(discoverybusiness.router)
app.include_router(csrftoken.router)  # Incluir la nueva ruta para CSRF

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
