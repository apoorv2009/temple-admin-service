# Temple Admin Service

FastAPI service for admin review, approval, rejection, and audit actions.

## Responsibilities

- list pending signup requests
- show request details
- approve a request
- reject a request with reason
- record admin audit actions later

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --port 8003
```

## Render start command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

