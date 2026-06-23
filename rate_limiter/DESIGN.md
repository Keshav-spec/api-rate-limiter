# Design Decisions

## Storage

Supported:
- InMemoryStorage
- RedisStorage

Future:
- PostgreSQL
- DynamoDB

## Thread Safety

InMemoryStorage will use threading.Lock.

Redis relies on atomic operations.

## Clock Source

Server time is authoritative.

Client timestamps are ignored.

## Rate Limits

Supports:
- Global limits
- Route-specific limits

Route-specific limits override global limits.