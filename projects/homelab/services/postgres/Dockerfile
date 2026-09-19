FROM postgres:16-alpine

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    git \
    build-base \
    postgresql-dev

# The PG build system is persistent about bitcode (JIT) generation.
# Fake clang-19 and llvm-lto to satisfy the Makefile on Alpine.
RUN mkdir -p /usr/lib/llvm19/bin && \
    echo '#!/bin/sh' > /usr/bin/clang-19 && \
    echo 'exit 0' >> /usr/bin/clang-19 && \
    chmod +x /usr/bin/clang-19 && \
    ln -s /usr/bin/clang-19 /usr/lib/llvm19/bin/llvm-lto

# Build and install pgvector extension
RUN cd /tmp && \
    git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make OPTFLAGS="" && \
    mkdir -p src && \
    touch src/bitutils.bc src/bitvec.bc src/halfutils.bc src/halfvec.bc \
          src/hnsw.bc src/hnswbuild.bc src/hnswinsert.bc src/hnswscan.bc \
          src/hnswutils.bc src/hnswvacuum.bc src/ivfbuild.bc src/ivfflat.bc \
          src/ivfinsert.bc src/ivfkmeans.bc src/ivfscan.bc src/ivfutils.bc \
          src/ivfvacuum.bc src/sparsevec.bc src/vector.bc && \
    make install

# Cleanup build artifacts
RUN apk del .build-deps && \
    rm -rf /tmp/pgvector /usr/bin/clang-19 /usr/lib/llvm19
