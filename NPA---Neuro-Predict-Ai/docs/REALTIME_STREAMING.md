# راهنمای Real-time Data Streaming - NeuroPredict-AI

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [Architecture](#architecture)
3. [Stream Types](#stream-types)
4. [WebSocket API](#websocket-api)
5. [REST API](#rest-api)
6. [Usage Examples](#usage-examples)
7. [Frontend Integration](#frontend-integration)

---

## مقدمه

سیستم Real-time Data Streaming برای NeuroPredict-AI امکان دریافت داده‌های real-time از منابع مختلف را فراهم می‌کند:

- **AI Predictions**: نتایج پیش‌بینی در لحظه
- **System Monitoring**: معیارهای سیستم
- **Clinical Alerts**: هشدارهای بالینی
- **Device Data**: داده‌های دستگاه‌های پزشکی
- **AI/ML Health**: سلامت مدل‌های AI

---

## Architecture

### Components

1. **RealTimeStreamingService**: سرویس اصلی برای مدیریت streaming
2. **StreamChannel**: کانال‌های streaming
3. **WebSocket Connections**: اتصالات WebSocket
4. **Message Queue**: صف پیام‌ها برای reliable delivery
5. **Data Producers**: تولیدکنندگان داده

### Flow

```
Data Source → Producer → Message Queue → Broadcasting → WebSocket → Client
```

---

## Stream Types

### 1. Predictions

```python
channel_id = "predictions:{patient_id}"
```

برای دریافت نتایج پیش‌بینی در لحظه.

### 2. Monitoring

```python
channel_id = "monitoring:system"  # System metrics
channel_id = "monitoring:ai_ml"   # AI/ML health
```

برای دریافت معیارهای monitoring.

### 3. Clinical Alerts

```python
channel_id = "alerts:patient:{patient_id}"  # Patient-specific
channel_id = "alerts:global"                 # Global alerts
```

برای دریافت هشدارهای بالینی.

### 4. Device Data

```python
channel_id = "devices:{device_id}"
```

برای دریافت داده‌های دستگاه‌های پزشکی.

---

## WebSocket API

### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/streaming/connect?channels=predictions:123,monitoring:system');
```

### Message Format

#### Incoming Messages

```json
{
  "channel": "predictions:123",
  "stream_type": "predictions",
  "timestamp": "2024-01-15T10:00:00Z",
  "message_id": "uuid",
  "data": {
    "prediction_id": 456,
    "patient_id": 123,
    "result": {...},
    "status": "completed"
  }
}
```

#### Outgoing Messages

**Subscribe:**
```json
{
  "type": "subscribe",
  "channel_id": "predictions:123"
}
```

**Unsubscribe:**
```json
{
  "type": "unsubscribe",
  "channel_id": "predictions:123"
}
```

**Ping:**
```json
{
  "type": "ping"
}
```

---

## REST API

### Create Channel

```bash
POST /api/v1/streaming/channels
Content-Type: application/json

{
  "channel_id": "predictions:123",
  "stream_type": "predictions"
}
```

### Broadcast Message

```bash
POST /api/v1/streaming/broadcast
Content-Type: application/json

{
  "channel_id": "predictions:123",
  "message": {
    "prediction_id": 456,
    "result": {...}
  },
  "exclude_connections": []
}
```

### List Channels

```bash
GET /api/v1/streaming/channels
```

### Get Channel Stats

```bash
GET /api/v1/streaming/channels/{channel_id}
```

### List Connections

```bash
GET /api/v1/streaming/connections
```

---

## Usage Examples

### Backend: Stream Prediction Result

```python
from app.services.streaming.data_producers import PredictionStreamProducer

await PredictionStreamProducer.stream_prediction_result(
    prediction_id=123,
    patient_id=456,
    result={
        "disease_type": "alzheimer",
        "risk_level": "high",
        "risk_score": 0.85,
        "confidence": 0.92
    }
)
```

### Backend: Stream Clinical Alert

```python
from app.services.streaming.data_producers import ClinicalAlertProducer

await ClinicalAlertProducer.stream_alert(
    alert_type="high_risk",
    severity="high",
    patient_id=456,
    message="High risk of Alzheimer's detected",
    data={"risk_score": 0.85}
)
```

### Backend: Stream System Metrics

```python
from app.services.streaming.data_producers import MonitoringStreamProducer

await MonitoringStreamProducer.stream_system_metrics({
    "cpu_usage": 45.2,
    "memory_usage": 62.5,
    "disk_usage": 38.1
})
```

---

## Frontend Integration

### React Hook Example

```typescript
import { useEffect, useState } from 'react';

function useRealtimeStream(channels: string[]) {
  const [data, setData] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    const channelList = channels.join(',');
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/streaming/connect?channels=${channelList}`
    );
    
    ws.onopen = () => {
      setConnected(true);
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setData(message.data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      setConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, [channels]);
  
  return { data, connected };
}

// Usage
function PredictionMonitor({ patientId }: { patientId: number }) {
  const { data, connected } = useRealtimeStream([`predictions:${patientId}`]);
  
  return (
    <div>
      {connected ? (
        <div>
          {data && (
            <div>
              <p>Risk Level: {data.result.risk_level}</p>
              <p>Risk Score: {data.result.risk_score}</p>
            </div>
          )}
        </div>
      ) : (
        <p>Connecting...</p>
      )}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <div v-if="connected">
      <div v-if="data">
        <p>Risk Level: {{ data.result.risk_level }}</p>
        <p>Risk Score: {{ data.result.risk_score }}</p>
      </div>
    </div>
    <div v-else>
      Connecting...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  patientId: Number
});

const data = ref(null);
const connected = ref(false);
let ws = null;

onMounted(() => {
  const channel = `predictions:${props.patientId}`;
  ws = new WebSocket(
    `ws://localhost:8000/api/v1/streaming/connect?channels=${channel}`
  );
  
  ws.onopen = () => {
    connected.value = true;
  };
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    data.value = message.data;
  };
  
  ws.onclose = () => {
    connected.value = false;
  };
});

onUnmounted(() => {
  if (ws) {
    ws.close();
  }
});
</script>
```

---

## Best Practices

### 1. Connection Management

- همیشه connection را در cleanup ببندید
- از reconnection logic استفاده کنید
- Ping/Pong برای keep-alive

### 2. Error Handling

```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Implement retry logic
};

ws.onclose = (event) => {
  if (event.code !== 1000) {
    // Unexpected close, reconnect
    setTimeout(() => connect(), 1000);
  }
};
```

### 3. Message Handling

```javascript
ws.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);
    
    // Handle different message types
    switch (message.type) {
      case 'connection':
        handleConnection(message);
        break;
      case 'data':
        handleData(message.data);
        break;
      case 'error':
        handleError(message);
        break;
    }
  } catch (error) {
    console.error('Error parsing message:', error);
  }
};
```

### 4. Channel Subscription

```javascript
// Subscribe to additional channel
ws.send(JSON.stringify({
  type: 'subscribe',
  channel_id: 'monitoring:system'
}));

// Unsubscribe
ws.send(JSON.stringify({
  type: 'unsubscribe',
  channel_id: 'monitoring:system'
}));
```

---

## Performance Considerations

### 1. Message Rate Limiting

برای جلوگیری از overload، rate limiting اعمال کنید:

```python
# In producer
if channel.message_count > 1000:
    await asyncio.sleep(0.1)  # Throttle
```

### 2. Connection Limits

حداکثر تعداد connections را محدود کنید:

```python
MAX_CONNECTIONS = 1000
if len(realtime_service.connections) >= MAX_CONNECTIONS:
    raise HTTPException(503, "Too many connections")
```

### 3. Message Queue Size

اندازه queue را monitor کنید:

```python
if realtime_service.message_queue.qsize() > 10000:
    logger.warning("Message queue size is high")
```

---

## Troubleshooting

### مشکل: Connection Drops

**راه‌حل:**
- بررسی network connectivity
- استفاده از ping/pong برای keep-alive
- پیاده‌سازی reconnection logic

### مشکل: Messages Not Received

**راه‌حل:**
- بررسی کنید که به channel درست subscribe شده‌اید
- بررسی channel stats
- بررسی connection stats

### مشکل: High Memory Usage

**راه‌حل:**
- محدود کردن تعداد connections
- محدود کردن message queue size
- Cleanup old channels

---

## منابع بیشتر

- [WebSocket API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

---

## پشتیبانی

برای سوالات و مشکلات:
- Integration Team: integration@neuropredict-ai.com
- Technical Support: support@neuropredict-ai.com

