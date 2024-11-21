FROM python:3.10-buster


# Install required drivers and applications
RUN apt-get update && \
    apt-get install -y apt-transport-https && \
    apt-get install -y apt-utils && \
    apt-get install -y debconf-utils && \
    apt-get install -y build-essential && \
    apt-get install git


COPY config/  /app/config
COPY manage.py /app
COPY Pipfile    /app
COPY Pipfile.lock /app

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pipenv
# RUN pipenv install --system --dev
RUN pipenv install --system --deploy
EXPOSE 8000

COPY src/       /app/src

CMD python manage.py runserver --noreload 0.0.0.0:8000
