# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# dependencies with poetry
RUN pip install 'poetry==1.1.4'
COPY ./src/poetry.lock ./src/pyproject.toml /code/
RUN poetry install --no-dev --no-interaction --no-ansi

# copy the content of the local src directory to the working directory
COPY src/ .
RUN rm *.tmp

# command to run on container start
CMD [ "poetry", "run", "./bgzf", "--interval", "1440"]
