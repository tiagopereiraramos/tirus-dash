// WebSocket client for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  
  constructor() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    this.url = `${protocol}//${window.location.host}/ws`;
  }
  
  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log("WebSocket connected");
      };
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket message:", data);
      };
      
      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
      
      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
      };
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const wsClient = new WebSocketClient();