FROM python:3-alpine

ENV FLASK_APP="autoloading"
ENV TESTING="true"

WORKDIR /usr/src/app

COPY . .
RUN chmod +x ./start.sh

RUN apk add --no-cache pkgconf mariadb-dev build-base
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install .
# CMD ["flask", "run", "-p", "8080", "-h", "0.0.0.0", "--debug"]
CMD ["bash", "start.sh"]