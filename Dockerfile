FROM python:3-alpine3.19
WORKDIR /app
COPY . /app
RUN pip install -r requirement.txt
EXPOSE 6969
CMD python ./app.py