# Django Channels Lab

Two minimal WebSocket servers built with Django Channels, small enough to read in five minutes:

- **Echo** (`/ws/echo/`): receives a JSON message and sends it back in uppercase, to the sender only.
- **Chat** (`/ws/chat/`): a chat room. One message sent by any client is delivered to every connected client, using a Channels group and Redis as the channel layer.

## Tech Stack

- Python, Django, Django Channels
- Daphne (ASGI server)
- Redis, through `channels_redis`, as the channel layer for the chat room

## Project Structure

```
config/        Django project (settings, asgi.py)
chat/          App with consumers and WebSocket routing
  consumers.py EchoConsumer and ChatConsumer
  routing.py   websocket_urlpatterns
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

In `config/settings.py`, make sure these are set:

```python
INSTALLED_APPS = [
    "daphne",          # must be first, so runserver uses ASGI
    # ...
    "channels",
    "chat",
]

ASGI_APPLICATION = "config.asgi.application"
```

`config/asgi.py` routes WebSocket traffic to the consumers:

```python
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})
```

### Channel layer (needed for the chat room)

Start Redis:

```bash
docker run -d --name redis-lab -p 6379:6379 redis
```

Then in `config/settings.py`:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": "redis://127.0.0.1:6379",
                    "socket_timeout": 30,
                }
            ],
        },
    }
}
```

> **Why `socket_timeout`?** With `redis` 8.x and `channels_redis` 4.3.0, idle WebSocket connections died after 5 seconds with `Timeout reading from ...`. `channels_redis` waits up to 5 seconds for a message, and the Redis client's default read timeout expired at the same moment. A higher `socket_timeout` fixes it.

For a quick local test without Redis, you can use the in-memory layer (single process only, development only):

```python
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
```

## Run

```bash
python manage.py runserver
```

## Try It

No frontend needed. Use the `websockets` command-line client.

### Echo

```bash
python -m websockets ws://127.0.0.1:8000/ws/echo/
> {"message": "hello"}
< {"echo": "HELLO"}
```

### Chat room

Open two terminals and run in both:

```bash
python -m websockets ws://127.0.0.1:8000/ws/chat/
```

Send `{"message": "hello"}` from the first terminal. It appears in **both** terminals. Send `{"message": "bye bye"}` from the second, and both receive that too.

## How It Works

1. A client opens a WebSocket. The routing in `chat/routing.py` sends it to a consumer.
2. **Echo:** `receive()` parses the JSON, uppercases the message, and answers on the same connection.
3. **Chat:** on `connect()`, the consumer joins the group `"chat"` (`group_add`). On `receive()`, it sends the message to the whole group (`group_send`) with `"type": "chat.message"`. Channels maps that type to the `chat_message()` handler, which pushes the message to each client.
4. Redis carries messages between consumers, so it also works across multiple server processes.

## Notes and Pitfalls

- `group_add` joins a group; `group_send` delivers a message. Mixing them up raises `Channel name must be a valid unicode string...`.
- The message type uses a dot: `"chat.message"` maps to the method `chat_message`. A space or underscore in the type means no handler is found.
- Invalid JSON is handled with `json.JSONDecodeError`, and the message is wrapped in `str(...)` so non-string values do not crash the consumer.
- `disconnect()` return values are ignored by Channels; use it for cleanup (here: `group_discard`).

## Known Limitations

- No usernames: messages are anonymous.
- No message history: messages are not stored, so late joiners see nothing from before.
- No authentication.
- One global room (`"chat"`).

## Author

**Ramin Ghorbani Hesari**, Full-Stack Developer
raminmini.com