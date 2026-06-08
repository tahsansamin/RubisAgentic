import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class MessageRequest(BaseModel):
    text: str

@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.post('/send_message')
def send_message(request: MessageRequest):
    return {'message': request.text}