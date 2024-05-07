\c scpgram;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL);

CREATE TABLE secret_chats (
    chat_id SERIAL PRIMARY KEY,
    owner_id INT REFERENCES users(user_id),
    chat_name VARCHAR(100),
    chat_uuid UUID DEFAULT uuid_generate_v4());

CREATE TABLE chat_participants (
    participant_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    chat_id INT REFERENCES secret_chats(chat_id),
    UNIQUE (user_id, chat_id));

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(user_id),
    chat_id INT REFERENCES secret_chats(chat_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT);
