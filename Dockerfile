FROM python:3

RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		mysql-client libmysqlclient-dev \
		postgresql-client libpq-dev \
		sqlite3 \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

# peragro-at deps
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && apt-get update && apt-get install -y \
        git \
        python-virtualenv \
        python-pip \
        python-software-properties \
        python-dev \
        cython \
        python-pyassimp \
        sox libsox-fmt-mp3 \
        --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "-u", "manage.py", "runserver", "0.0.0.0:8000"]
