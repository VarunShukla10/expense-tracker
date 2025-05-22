from fastapi import FastAPI
from app.database import startup, shutdown
from app.routes.auth_routes import router as auth_router
from app.routes.expense_routes import router as expense_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.include_router(auth_router)
app.include_router(expense_router)

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
