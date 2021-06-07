FROM node:lts-alpine as builder
COPY ./frontend .
ENV NODE_ENV=production
RUN npm install
RUN npm run build
FROM python:3.7-slim-stretch
COPY --from=builder ./dist /dist/
COPY ./backend /dist/
WORKDIR /dist
RUN pip install -r requirements.txt
EXPOSE 5001
ENTRYPOINT ["python", "/dist/__init__.py"]