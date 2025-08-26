# pull official base image
FROM python:3.12.2 as builder

EXPOSE 8080

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python -m venv /opt/venv
RUN apt-get update
RUN apt-get update -y
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"
# install dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
COPY constraints.txt .
RUN python -m pip install -r requirements.txt

# Copy the entire api directory structure
COPY . .

# Add the current directory to Python path
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

RUN ls -ll

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
