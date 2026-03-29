import { useEffect, useCallback, useState } from 'react';
import wsService from '../services/websocket';
import { WebSocketMessage } from '../types';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    wsService.connect();
    setIsConnected(true);

    const unsubscribe = wsService.subscribe((message) => {
      setLastMessage(message);
    });

    return () => {
      unsubscribe();
      wsService.disconnect();
      setIsConnected(false);
    };
  }, []);

  const sendMessage = useCallback((message: any) => {
    wsService.send(message);
  }, []);

  return {
    isConnected,
    lastMessage,
    sendMessage,
  };
}

export function useRealtimeUpdates<T>(
  initialValue: T,
  messageHandler: (current: T, message: WebSocketMessage) => T
): T {
  const [value, setValue] = useState<T>(initialValue);
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    if (lastMessage) {
      setValue((current) => messageHandler(current, lastMessage));
    }
  }, [lastMessage, messageHandler]);

  return value;
}
