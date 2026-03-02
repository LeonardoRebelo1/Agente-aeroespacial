const http = require("http");
const https = require("https");
const fs = require('fs');
try {
  const env = fs.readFileSync('.env', 'utf-8');
  env.split('\n').forEach(line => {
    const [key, ...val] = line.split('=');
    if (key && val.length) process.env[key.trim()] = val.join('=').trim();
  });
} catch {}
const path = require("path");
const crypto = require("crypto");
const url = require("url");

const PORT = process.env.PORT || 3000;
const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";
const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;



function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function serveFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end("Not Found"); return; }
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  });
}

function getBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => (body += chunk.toString()));
    req.on("end", () => { try { resolve(JSON.parse(body || "{}")); } catch { resolve({}); } });
    req.on("error", reject);
  });
}

function proxyRequest(method, endpoint, payload) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new url.URL(endpoint);
    const isHttps = parsedUrl.protocol === "https:";
    const lib = isHttps ? https : http;
    const bodyStr = payload ? JSON.stringify(payload) : "";
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.pathname + (parsedUrl.search || ""),
      method,
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(bodyStr) },
    };
    const req = lib.request(options, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: { message: data } }); }
      });
    });
    req.on("error", reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = parsedUrl.pathname;

  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") { res.writeHead(204); res.end(); return; }

  if (req.method === "GET" && pathname === "/") {
    return serveFile(res, path.join(__dirname, "public", "index.html"), "text/html");
  }

  if (req.method === "POST" && pathname === "/chat") {
    try {
      const body = await getBody(req);
      const { user_id, thread_id, content } = body;
      if (!user_id || !thread_id || !content) return sendJSON(res, 400, { error: "Campos obrigatórios faltando." });
      const result = await proxyRequest("POST", CHAT_ENDPOINT, { user_id, thread_id, content });
      return sendJSON(res, result.status, result.body);
    } catch (err) {
      return sendJSON(res, 502, { error: "Não foi possível conectar à API do agente.", detail: err.message });
    }
  }

  if (req.method === "DELETE" && pathname === "/chat") {
  try {
    const body = await getBody(req);
    const { user_id, thread_id } = body;
    if (!user_id || !thread_id) return sendJSON(res, 400, { error: "user_id e thread_id são obrigatórios." });
    
    const deleteUrl = `${API_BASE_URL}/api/chat/${thread_id}`;
    const result = await proxyRequest("DELETE", deleteUrl, null);
    return sendJSON(res, result.status, result.body);
  } catch (err) {
    return sendJSON(res, 502, { error: "Não foi possível conectar à API do agente.", detail: err.message });
  }
}

  res.writeHead(404); res.end("Not Found");
});

server.listen(PORT, () => {
  console.log(`\n🚀 Space Chat rodando em http://localhost:${PORT}`);
  console.log(`🌐 API do agente: ${API_BASE_URL}`);
  console.log(`\nDefina API_BASE_URL para apontar para sua API: API_BASE_URL=https://sua-api.com node server.js\n`);
});