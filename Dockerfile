# build Vue frontend
FROM node:16-alpine as builder
COPY ./frontend .
RUN npm install
RUN npm run build
# now we should have a dist folder containing the static website

FROM python:3.7.10-stretch as pybuilder
WORKDIR /code
COPY ./backend /code/
RUN pip install --user -r requirements.txt
# We get the dependencies with the full python image so we can compile the one with missing binaries
ENV UseRobots=false

FROM python:3.7.10-slim-stretch as app
# copy the dependencies from the pybuilder
COPY --from=pybuilder /root/.local /root/.local
# copy the backend python files from the pybuilder
COPY --from=pybuilder /code /dist
# copy the frontend static files from the builder
COPY --from=builder ./dist /dist/
WORKDIR /dist
EXPOSE 5001

ENV PATH=/root/.local/bin:${PATH}
VOLUME /code/save

ENTRYPOINT ["python", "/dist/server.py"]
