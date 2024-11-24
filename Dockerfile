FROM python:latest
EXPOSE 5000
COPY  requirments.txt .
RUN pip install -r requirments.txt
COPY . .
CMD ["flask","run","--debug", "--host", "0.0.0.0"]