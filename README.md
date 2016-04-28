peragro-rest
==========

Django-based REST api for Peragro.

Running
----------
Build the image
```
    docker build -t peragro/peragro-rest github.com/peragro/peragro-rest
```
Run the image using the name 'peragro-rest' with public port 80
```
    docker run --name peragro-rest -p 80:8000 -d peragro/peragro-rest
```

Configuration
---------------
Create a superuser so you can log on to the django admin interface
```
    docker exec -it peragro-rest python manage.py createsuperuser
```

Test data
---------
Currently requires a user admin/admin.
```
	docker exec -it peragro-rest /bin/bash
	git clone https://github.com/peragro/peragro-test-files.git ../tempest-data
	python manage.py upload_test_data
	python manage.py upload_test_comments
```

Development
----------
```
    git clone https://github.com/peragro/peragro-rest.git
```
Run the server on public port 8000 with the local git check-out mounted in the container under '/usr/src/app'
```
    docker run --rm -p 8000:8000 -v <path_to_checkout>:/usr/src/app -d peragro/peragro-rest
```

