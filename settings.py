import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("TOKEN")
APP_HASH=os.getenv("app_hash")
API_ID=os.getenv("app_id")
BOT_NAME=os.getenv("BOT_NAME")
ROOM_ID=os.getenv("CHAT_ID")

def printenvironment():
    print(f'The secret id is: {SECRET_KEY}.')
    print(f'The APP_HASH id is: {APP_HASH}.')
    print(f'The API_ID id is: {API_ID}.')
    print(f'The BOT_NAME id is: {BOT_NAME}.')
    print(f'The ROOM_ID id is: {ROOM_ID}.')


if __name__ == "__main__":
    printenvironment()