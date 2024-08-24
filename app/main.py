from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import accounts, discoverybusiness, csrftoken 



app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:3000",  # Permitir solicitudes desde React
    "http://localhost:8501",  # Permitir solicitudes desde Streamlit
    # Agrega aquí otros orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Asegúrate de que esta lista contenga todos los orígenes permitidos
    allow_credentials=True,  # Permitir el envío de cookies
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)



app.include_router(accounts.router)
app.include_router(discoverybusiness.router)
app.include_router(csrftoken.router)  # Incluir la nueva ruta para CSRF

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
