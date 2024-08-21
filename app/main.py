from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import accounts, discoverybusiness

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:3000",  # Permitir solicitudes desde React
    "http://localhost:8501",  # Permitir solicitudes desde Streamlit
    # Agrega aquí otros orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

app.include_router(accounts.router)
app.include_router(discoverybusiness.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)