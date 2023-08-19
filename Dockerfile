From python:3-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .

CMD [ "gunicorn", "autoloading:app", "-c", "gunicorn.conf.py" ]
