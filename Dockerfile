FROM python:latest
EXPOSE 5000
WORKDIR ./app
COPY  requirments.txt .
RUN pip install -r requirments.txt
COPY . .
CMD ["flask","run","--debug", "--host", "0.0.0.0"]