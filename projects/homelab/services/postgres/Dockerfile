FROM postgres:16-alpine

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    git \
    build-base \
    postgresql-dev

# Build and install pgvector extension without LLVM bitcode
RUN cd /tmp && \
    git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make with_llvm=no OPTFLAGS="" && \
    make install with_llvm=no

# Cleanup build artifacts
RUN apk del .build-deps && \
    rm -rf /tmp/pgvector
