# Use an official Python runtime as a parent image
FROM python:3.8

RUN pip install pipenv

# Set the working directory to /booker
WORKDIR /booker

COPY Pipfile.lock /booker

RUN pipenv install --ignore-pipfile --keep-outdated --dev

# Copy the current directory contents into the container at /booker
COPY . /booker
