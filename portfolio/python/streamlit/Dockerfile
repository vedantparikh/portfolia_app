FROM scratch
# pull official base image
RUN echo "$PWD"
FROM python:3.9.7 as builder

EXPOSE 8501

# set work directory
WORKDIR /usr/src/app

# set environment variablesdoc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY main.py .
RUN apt-get update
RUN apt-get update -y

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]