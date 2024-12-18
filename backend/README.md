# Prerequisites

- Add secret key in main.py

to create secret key run= `openssl rand -hex 32` in your terminal.

- Change database url in database.py

- Rochak's service at get_responce_RAG() in main.py

## Run

- run mysql server first

- `uvicorn main:app --reload`

## In code

- Database used in code -> db_example

- Tables in database -> chat, users

- Structure of tables:

![Structure of tables](st.jpg)
