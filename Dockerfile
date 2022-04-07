# build Vue frontend
FROM node:lts-alpine as builder
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

ENV DD_SERVICE=bang-backend
ENV DD_ENV=dev-test
ENV DD_LOGS_INJECTION=true
ENV DD_PROFILING_ENABLED=true
ENV DD_TRACE_AGENT_URL=http://0.0.0.0:8126

ENV PATH=/root/.local/bin:${PATH}

ENTRYPOINT ["ddtrace-run", "python", "/dist/server.py"]
