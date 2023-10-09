FROM python:3.11-slim-buster
# Install python and pip
# RUN apk add --no-cache --update python3 py3-pip bash
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt

# Run the image as a non-root user
# RUN adduser -D myuser
# # USER myuser

ADD . /code
WORKDIR /code


# COPY . /app
# WORKDIR /app

# EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["app.py"]