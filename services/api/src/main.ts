import { createServer } from "node:http";

import type { MCPServerRecord } from "@mcp-platform/shared-types";

const port = Number(process.env.PORT ?? 3001);

const sampleServers: MCPServerRecord[] = [
  {
    id: "filesystem",
    name: "filesystem-server",
    transport: "stdio",
    status: "stopped",
    capabilities: { tools: true },
  },
];

const server = createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  if (req.url === "/mcp/servers") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ servers: sampleServers }));
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(port, () => {
  console.log(`api listening on :${port}`);
});
