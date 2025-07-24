## roadmap
- actions implementation
- webhook deploy && webhook integration for live interations

## installation
-docker
```sh
$ docker buildx build -t image-name .
$ docker run -d --name container-name -p 80:80 image-name
```

-poetry
```sh
$ pip install poetry # might need `poetry-plugin-shell`
$ poetry install
$ poetry shell
```
