import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
  status?: string;
  channel?: string;
}

export function useWebSocket(
  channel: 'all' | 'ai_ml' | 'clinical' | 'system' | 'security' = 'all',
  onMessage?: (message: WebSocketMessage) => void
) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (!token) {
      // Skip WebSocket when not authenticated; avoid noisy error in console
      return;
    }

    // Use same origin in dev so Vite proxy can forward to backend (8001)
    const wsProtocol = typeof location !== 'undefined' && location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.DEV && typeof location !== 'undefined'
      ? `${location.host}`
      : (import.meta.env.VITE_WS_HOST || 'localhost:8001');
    const wsUrl = `${wsProtocol}//${wsHost}/api/v1/ws/monitoring?token=${encodeURIComponent(token)}&channel=${channel}`;
    
    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log(`WebSocket connected to channel: ${channel}`);
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            setLastMessage(message);
            if (onMessage) {
              onMessage(message);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          
          // Reconnect after 5 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 5000);
        };
      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        setIsConnected(false);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [channel, onMessage]);

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return {
    isConnected,
    lastMessage,
    sendMessage,
  };
}

