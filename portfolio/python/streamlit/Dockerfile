FROM scratch
# pull official base image
FROM python:3.10.6 as builder

EXPOSE 8501

# set work directory
WORKDIR /usr/src/app

# set environment variablesdoc
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
RUN python -m pip install -r requirements.txt -c constraints.txt
COPY main.py .
COPY plots ./plots/
COPY statistical_indicators ./statistical_indicators/

RUN ls -ll

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]