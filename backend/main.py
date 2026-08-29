import os
import sys

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from invokeagent import combine_and_write

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
    # Extract JSON data from the message
    
    
    # Write the JSON data to a spreadsheet
    combine_and_write(request.text)
    
    return {'message': request.text}

