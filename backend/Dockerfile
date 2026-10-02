FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir "fastapi>=0.120,<1" "uvicorn[standard]>=0.30,<1" "sqlalchemy>=2.0,<2.1" "alembic>=1.16,<2" "pydantic>=2.10,<3" "pydantic-settings>=2.8,<3" "PyJWT>=2.9,<3" "argon2-cffi>=23.1,<26" "python-multipart>=0.0.20,<1" "psycopg[binary]>=3.2,<4"
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
