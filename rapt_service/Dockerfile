FROM python:3.10-slim

WORKDIR /rapt_service

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

CMD ["/rapt_service/entrypoint.sh"]