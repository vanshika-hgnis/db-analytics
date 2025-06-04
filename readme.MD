# DB Analytics
Application for chatting with Database (primarily mssql through sql server) also includes an intent log which displays data table and visualization whenever necessary.
## Code Structure

project_root/
│
├── core/
│   ├── sql_server.py
│   ├── schema_extractor.py
│   ├── vector_store.py
│   ├── prompt_builder.py
│   ├── llm_sql_generator.py
│   ├── sql_validator.py
│
├── streamlit_app.py
├── .env
├── requirements.txt


![alt text](resources\image.png)