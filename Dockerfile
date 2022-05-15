FROM python:3.10.4-slim-bullseye
RUN pip3 install flask flask-wtf email-validator requests flask-login
COPY app.py app.py
COPY templates templates
CMD python app.py
