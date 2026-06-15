export interface MCPServerInfo {
  name: string;
  version: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface MCPToolsListResult {
  tools: MCPTool[];
  nextCursor?: string;
}

export interface MCPContentBlock {
  type: "text";
  text: string;
}

export interface MCPToolsCallResult {
  content: MCPContentBlock[];
  isError?: boolean;
}

export interface MCPServerRecord {
  id: string;
  name: string;
  transport: "stdio" | "sse";
  status: "stopped" | "running" | "error";
  capabilities: {
    tools?: boolean;
    resources?: boolean;
    prompts?: boolean;
  };
}

export type { MCPServerRecord as MCPServer };
