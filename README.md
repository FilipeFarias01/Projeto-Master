# Projeto - API de Tarefas

## Como rodar

Abra esta pasta no VS Code.

No terminal, rode:

```bash
pip install -r requirements.txt
```

Depois:

```bash
uvicorn app.main:app --reload
```

Abra no navegador:

- Front-end: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Arquivos principais

- app/models.py
- app/routers/tarefas.py
- front/index.html
- front/app.js
- front/style.css
