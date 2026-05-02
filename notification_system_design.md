# Stage 1 - Notification System Design

## API Endpoints

GET /api/notifications
GET /api/notifications/unread
POST /api/notifications
PUT /api/notifications/{id}/read
DELETE /api/notifications/{id}

---

## Request (POST /api/notifications)

```json
{
  "title": "Placement Drive",
  "message": "TCS hiring tomorrow",
  "type": "placement",
  "userId": "123"
}
```

## Response

```json
{
  "id": "n101",
  "title": "Placement Drive",
  "message": "TCS hiring tomorrow",
  "type": "placement",
  "isRead": false,
  "createdAt": "2026-05-02T10:00:00Z"
}
```

---

## Headers

Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJtdWt0ZXNobmFpZHVfY2hhbmRha2FAc3JtYXAuZWR1LmluIiwiZXhwIjoxNzc3NzA0MzYwLCJpYXQiOjE3Nzc3MDM0NjAsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJlOGE5NDk4OS0zZGYxLTQ4ZjQtODc4Ni01ZWM0MmVkZmVhZTUiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJtdWt0ZXNoIG5haWR1Iiwic3ViIjoiNzBmZGRlOTQtMTFjMi00NTA2LTkzMzEtMjU2NTJjOThmMTYxIn0sImVtYWlsIjoibXVrdGVzaG5haWR1X2NoYW5kYWthQHNybWFwLmVkdS5pbiIsIm5hbWUiOiJtdWt0ZXNoIG5haWR1Iiwicm9sbE5vIjoiYXAyMzExMDAxMTQ3NiIsImFjY2Vzc0NvZGUiOiJRa2JweEgiLCJjbGllbnRJRCI6IjcwZmRkZTk0LTExYzItNDUwNi05MzMxLTI1NjUyYzk4ZjE2MSIsImNsaWVudFNlY3JldCI6IkRjVHFUUUZNZUVhRlFhS0UifQ.aFc-YzlaMHliWl87m5SJz_1wl0OUa-3ZqeNuwPUantg"

---

## JSON Schema

```json
{
  "id": "string",
  "title": "string",
  "message": "string",
  "type": "string",
  "isRead": "boolean",
  "createdAt": "datetime"
}
```


## Stage 2

### Database Choice

PostgreSQL (relational database)

---

### Table Schema

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    userId INT,
    title TEXT,
    message TEXT,
    type VARCHAR(20),
    isRead BOOLEAN DEFAULT FALSE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Problems with Large Data

* Slow queries
* High latency due to full table scans

---

### Solutions

* Add indexes on userId, isRead, createdAt
* Use pagination (LIMIT, OFFSET)
* Table partitioning for large datasets

---

### Queries

```sql
-- Get all notifications
SELECT * FROM notifications WHERE userId = 123;

-- Get unread notifications
SELECT * FROM notifications 
WHERE userId = 123 AND isRead = FALSE 
ORDER BY createdAt DESC;

-- Mark notification as read
UPDATE notifications 
SET isRead = TRUE 
WHERE id = 101;
```

## Stage 3

### Given Query

```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```

---

### Is it correct?

Yes, it correctly fetches unread notifications for a student.

---

### Why is it slow?

* No index on studentID, isRead, createdAt
* Causes full table scan

---

### Optimization (Index)

```sql
CREATE INDEX idx_notifications 
ON notifications(studentID, isRead, createdAt DESC);
```

---

### Computation Cost

* Without index: O(n)
* With index: O(log n)

---

### Should we index every column?

No:

* Increases storage
* Slows insert/update operations
* Only index frequently queried columns

---

### Query (Placement notifications in last 7 days)

```sql
SELECT DISTINCT userId
FROM notifications
WHERE type = 'Placement'
AND createdAt >= NOW() - INTERVAL '7 days';
```

## Stage 4

### Problem

Fetching notifications on every page load causes high database load and slow response time.

---

### Solutions

* **Caching (Redis)**
  Store frequently accessed notifications in cache to reduce database queries.

* **Pagination**
  Fetch limited records using LIMIT and OFFSET instead of all data.

* **Lazy Loading**
  Load notifications only when the user opens the notifications section.

* **Real-time Updates**
  Use WebSockets or SSE to push new notifications instead of polling.

---

### Trade-offs

* Caching → Faster reads, but possible stale data
* Pagination → Reduces load, but shows partial data
* Real-time → Efficient, but increases system complexity


## Stage 5

### Issues in Current Implementation

* Sequential processing → slow for large users (50,000)
* No retry mechanism for failed emails
* Email failure causes inconsistency
* Tight coupling of DB and email operations

---

### Improved Approach

* Use asynchronous processing (queue system)
* Save to DB first (reliable)
* Send emails via background workers
* Add retry mechanism for failures

---

### Revised Pseudocode

```python
def notify_all(student_ids, message):
    for student_id in student_ids:
        save_to_db(student_id, message)     # store notification
        queue_email(student_id, message)    # async email sending
        push_to_app(student_id, message)    # real-time notification
```

---

### Failure Handling

* Track failed emails
* Retry using background workers

---

### DB and Email Together?

No:

* DB write should be immediate and reliable
* Email should be asynchronous and retryable


## Stage 6

### Approach

* Fetch notifications from API
* Assign priority: Placement > Result > Event
* Sort by priority and latest time
* Return top 10 notifications

---

### Code

import requests
from datetime import datetime

API_URL = "http://20.207.122.201/evaluation-service/notifications"

priority_map = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJtdWt0ZXNobmFpZHVfY2hhbmRha2FAc3JtYXAuZWR1LmluIiwiZXhwIjoxNzc3NzA0MzYwLCJpYXQiOjE3Nzc3MDM0NjAsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJlOGE5NDk4OS0zZGYxLTQ4ZjQtODc4Ni01ZWM0MmVkZmVhZTUiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJtdWt0ZXNoIG5haWR1Iiwic3ViIjoiNzBmZGRlOTQtMTFjMi00NTA2LTkzMzEtMjU2NTJjOThmMTYxIn0sImVtYWlsIjoibXVrdGVzaG5haWR1X2NoYW5kYWthQHNybWFwLmVkdS5pbiIsIm5hbWUiOiJtdWt0ZXNoIG5haWR1Iiwicm9sbE5vIjoiYXAyMzExMDAxMTQ3NiIsImFjY2Vzc0NvZGUiOiJRa2JweEgiLCJjbGllbnRJRCI6IjcwZmRkZTk0LTExYzItNDUwNi05MzMxLTI1NjUyYzk4ZjE2MSIsImNsaWVudFNlY3JldCI6IkRjVHFUUUZNZUVhRlFhS0UifQ.aFc-YzlaMHliWl87m5SJz_1wl0OUa-3ZqeNuwPUantg"
}

response = requests.get(API_URL, headers=headers)
data = response.json()
print(data)
notifications = data["notifications"]

for n in notifications:
    n["priority"] = priority_map.get(n["Type"], 0)
    n["time"] = datetime.strptime(n["Timestamp"], "%Y-%m-%d %H:%M:%S")

notifications.sort(key=lambda x: (-x["priority"], -x["time"].timestamp()))

top_10 = notifications[:10]

for n in top_10:
    print(n)
---
