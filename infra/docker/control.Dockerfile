FROM python:3.12-slim
WORKDIR /app
COPY services/control-api/src /app/services/control-api/src
COPY apps/console /app/apps/console
COPY scripts/dev.py /app/scripts/dev.py
RUN useradd --uid 10001 --create-home affiliate && mkdir /app/.local && chown affiliate /app/.local
USER affiliate
EXPOSE 8787
CMD ["python", "scripts/dev.py", "--bind", "0.0.0.0"]
