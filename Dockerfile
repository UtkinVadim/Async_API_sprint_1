FROM python:3.9.7-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install netcat -y

ARG USER=fastapi
RUN addgroup --system ${USER} && \
    adduser --system --no-create-home --ingroup ${USER} ${USER} && \
    chown -R ${USER}:${USER} /app
USER $USER

COPY src .
COPY .env .

RUN chmod +x wait_for_elastic.sh

EXPOSE 8000

ENTRYPOINT ["./wait_for_elastic.sh"]

CMD ["python", "-m", "main"]
