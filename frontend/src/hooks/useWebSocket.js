import { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const useWebSocket = (userId, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!userId) return;

    // Create WebSocket connection using native WebSocket for better compatibility
    const API_URL = process.env.REACT_APP_BACKEND_URL || window.location.origin;
    const wsUrl = API_URL.replace('http', 'ws').replace('https', 'wss');
    
    try {
      socketRef.current = new WebSocket(`${wsUrl}/ws/${userId}`);
      
      socketRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        
        // Send ping to keep connection alive
        const pingInterval = setInterval(() => {
          if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
        
        socketRef.current.pingInterval = pingInterval;
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== 'pong') {
            onMessage(data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      socketRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        if (socketRef.current?.pingInterval) {
          clearInterval(socketRef.current.pingInterval);
        }
      };

      socketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }

    return () => {
      if (socketRef.current) {
        if (socketRef.current.pingInterval) {
          clearInterval(socketRef.current.pingInterval);
        }
        socketRef.current.close();
      }
    };
  }, [userId, onMessage]);

  const sendMessage = (message) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, sendMessage };
};

export default useWebSocket;