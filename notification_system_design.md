# Notification System Design

## Stage 1: API Design
- GET /notifications
- PATCH /notifications/:id/read
- POST /notifications

## Stage 2: Database
Use PostgreSQL with table:
(id, user_id, type, message, is_read, created_at)

## Stage 3: Optimization
Problem: slow query due to full table scan
Solution: composite index on (user_id, is_read, created_at)

## Stage 4: Scaling
- Redis caching
- Pagination
- Read replicas

## Stage 5: Reliability
Use message queue (Kafka/RabbitMQ)
Async processing for email + DB

## Stage 6: Priority
Sort by:
- Type weight (Placement > Result > Event)
- Timestamp
Return top 10 notifications