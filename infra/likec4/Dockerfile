# Custom LikeC4 image: align Playwright browsers with bundled likec4 CLI (export png).
# See: https://github.com/likec4/likec4/issues/2132
ARG LIKEC4_BASE=likec4/likec4:latest
FROM ${LIKEC4_BASE}

USER root

WORKDIR /usr/local/lib/node_modules/likec4
RUN npx playwright install chromium

WORKDIR /data
