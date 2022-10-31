## Documentation

Useful commands to install and run the project.
```
$ docker-compose -f docker-compose.yaml build
$ docker-compose -f docker-compose.yaml up
```

Run tests or flake8.
```
$ docker-compose -f docker-compose.yaml run --rm web python manage.py test
$ docker-compose -f docker-compose.yaml run --rm web /bin/bash -c "flake8 ."
```
