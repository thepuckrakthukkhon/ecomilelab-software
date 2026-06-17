const http = require("http");
const fs = require("fs");
const path = require("path");
const { generateTelemetryPacket, MODES } = require("./mock-data/mock-generator");

const PORT = Number(process.env.PORT || 3000);
const PUBLIC_DIR = path.join(__dirname, "public");

function sendJson(res, payload) {
  res.writeHead(200, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify(payload));
}

function readQuery(url) {
  return new URL(url, `http://localhost:${PORT}`).searchParams;
}

function getTelemetryOptions(req) {
  const query = readQuery(req.url);
  const mode = query.get("mode") || "normal";
  const session = query.get("session") || "dashboard_live";

  if (!MODES.has(mode)) {
    return { error: `Unknown mode: ${mode}` };
  }

  return { mode, session };
}

function serveStatic(req, res) {
  const requestedPath = req.url === "/" ? "/index.html" : req.url;
  const safePath = path.normalize(requestedPath).replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(PUBLIC_DIR, safePath);

  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (error, content) => {
    if (error) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }

    const ext = path.extname(filePath);
    const contentType = ext === ".css" ? "text/css" : "text/html";

    res.writeHead(200, { "Content-Type": `${contentType}; charset=utf-8` });
    res.end(content);
  });
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith("/api/telemetry/latest")) {
    const options = getTelemetryOptions(req);

    if (options.error) {
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: options.error }));
      return;
    }

    sendJson(res, generateTelemetryPacket(options));
    return;
  }

  if (req.url.startsWith("/api/telemetry/stream")) {
    const options = getTelemetryOptions(req);

    if (options.error) {
      res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify({ error: options.error }));
      return;
    }

    res.writeHead(200, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });

    const sendPacket = () => {
      res.write(`data: ${JSON.stringify(generateTelemetryPacket(options))}\n\n`);
    };

    sendPacket();
    const interval = setInterval(sendPacket, 1000);
    req.on("close", () => clearInterval(interval));
    return;
  }

  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`ECOMILE dashboard running at http://localhost:${PORT}`);
});
