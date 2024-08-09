FROM python:3.12-alpine3.19

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

EXPOSE 9185
ENTRYPOINT ["./tuya_exporter.py"]
