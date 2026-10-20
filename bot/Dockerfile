FROM node:24-bookworm-slim

ENV NODE_ENV=production
WORKDIR /app

COPY bot/package.json bot/package-lock.json /app/bot/
RUN cd /app/bot \
    && npm ci --omit=dev --ignore-scripts \
    && node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js \
    && node -e "require('@matrix-org/matrix-sdk-crypto-nodejs')"

COPY bot/src /app/bot/src
COPY shared /app/shared
COPY catalog/human-design-bodygraph-topology.json /app/catalog/human-design-bodygraph-topology.json
COPY catalog/gate-ai-affordances.json /app/catalog/gate-ai-affordances.json
COPY catalog/gate-endocrine-correspondences.json /app/catalog/gate-endocrine-correspondences.json

RUN mkdir -p /var/lib/metheus && chown -R node:node /var/lib/metheus
USER node
WORKDIR /app/bot
ENV METHEUS_BOT_DATA_DIR=/var/lib/metheus

CMD ["node", "src/index.mjs"]
