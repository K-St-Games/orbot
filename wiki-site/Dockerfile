ARG MKDOCS_MATERIAL_VERSION=9.7.6

FROM squidfunk/mkdocs-material:${MKDOCS_MATERIAL_VERSION} AS build

WORKDIR /docs
COPY hi-orbit-wiki/mkdocs.yml ./
COPY hi-orbit-wiki/docs ./docs
RUN mkdocs build --strict --site-dir /site

FROM nginxinc/nginx-unprivileged:1.29-alpine

COPY --from=build /site /usr/share/nginx/html

EXPOSE 8080
