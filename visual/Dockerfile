FROM node:18-slim
WORKDIR /app
# Comentamos as linhas de npm se você não tiver pacotes extras
# COPY package*.json ./
# RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]