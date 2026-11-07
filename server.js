const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "public");
const PORT = 3000;

http.createServer((req, res) => {
  let pathname = decodeURIComponent(req.url.split("?")[0]);
  if (pathname === "/") pathname = "/index.html";

  const file = path.join(ROOT, pathname);

  if (!file.startsWith(ROOT)) {
    res.writeHead(403);
    return res.end("Forbidden");
  }

  fs.readFile(file, (err, data) => {
    if (err) {
      res.writeHead(404);
      return res.end("Not found");
    }

    const ext = path.extname(file);
    const types = {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css",
      ".js": "application/javascript",
      ".png": "image/png",
      ".jpg": "image/jpeg",
      ".svg": "image/svg+xml"
    };

    res.writeHead(200, {
      "Content-Type": types[ext] || "application/octet-stream"
    });
    res.end(data);
  });
}).listen(PORT, "0.0.0.0", () => {
  console.log("DAN AREWA DATA yana aiki a http://localhost:" + PORT);
});
