FROM node:lts-alpine as builder
COPY ./frontend .
RUN npm install
RUN npm run build
FROM python:3.7-slim-stretch
COPY --from=builder ./dist /dist/
COPY ./backend /dist/
WORKDIR /dist
RUN RUN apt-get update && apt-get install -y \
    libevent-dev \
    python-all-dev
RUN pip install -r requirements.txt
EXPOSE 5001
ENTRYPOINT ["python", "/dist/__init__.py"]