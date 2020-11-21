FROM python:3.7-slim-stretch

WORKDIR /code
COPY * /code/
RUN pip install -r requirements.txt
EXPOSE 5001

ENTRYPOINT ["python", "/code/__init__.py"]