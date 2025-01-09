CREATE KEYSPACE bookstore
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE bookstore;

CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    event_type TEXT,
    timestamp TIMESTAMP,
    book_id TEXT,
    book_title TEXT,
    details TEXT
);
