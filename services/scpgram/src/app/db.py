import hashlib
import os
import psycopg2
from flask_socketio import emit

def dbConnect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        user="scpgram",
        password=os.getenv('DB_PASSWORD', 'P4ssw0rd'),
        database=os.getenv('DB_NAME', 'scpgram')
    )
    return conn


def signin(username, password):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT password FROM users WHERE username = %s", (username,))
        hash_password = cursor.fetchall()
        if hash_password == "":
            conn.close()
            return "User not found"
        
        if hashlib.sha256(password.encode('utf-8')).hexdigest() != hash_password[0][0]:
            conn.close()
            return "incorrect password"
        conn.close()
        return "Successfully login"
    except Exception as e:
        conn.close()
        return "Database error: " + str(e)


def signup(username, password):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM users WHERE username = %s)", (username,)
        )

        exist = cursor.fetchall()[0][0]
        if exist:
            conn.close()
            return "User already exist"
        hash_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        instert = cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s,%s)", (username,hash_password)
        )
        conn.commit()
        conn.close()
        return "Successfully create user"
    except Exception as e:
        conn.close()
        return "Database error: " + str(e)

def create_chat(username, chat_name):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        user_id = get_userId(username)
        if not user_id:
            return "User not exist"
        cursor.execute("INSERT INTO secret_chats (owner_id, chat_name) VALUES (%s, %s) RETURNING chat_uuid;", (user_id[0][0], chat_name))
        chat_uuid = cursor.fetchone()[0]
        conn.commit()
        chat_id = get_chatId(chat_uuid)
        cursor.execute("INSERT INTO chat_participants (user_id, chat_id) VALUES (%s, %s);", (user_id[0][0], chat_id[0][0]))
        conn.commit()
        conn.close()
        return chat_uuid
    except Exception as e:
        conn.close()
        return "Database error: " + str(e)
    

def chat_add_user(owner_username,chat_uuid, username):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        chat_id = get_chatId(chat_uuid)
        if not chat_id:
            conn.close()
            return 'Chat not found'
        user_id = get_userId(username)
        if not user_id:
            conn.close()
            return 'User not found'
        owner_id = get_userId(owner_username)
        cursor.execute("SELECT 1 FROM secret_chats WHERE owner_id = %s and chat_id = %s" , (owner_id[0][0], chat_id[0][0]))
        right = cursor.fetchall()
        if not right:
            return 'Forbidden'
        cursor.execute("SELECT 1 FROM chat_participants WHERE user_id=%s and chat_id=%s", (user_id[0][0], chat_id[0][0]))
        participate = cursor.fetchall()
        if participate:
            conn.close()
            return "User already in chat"
        cursor.execute("INSERT INTO chat_participants (user_id, chat_id) VALUES (%s, %s);", (user_id[0][0], chat_id[0][0]))
        conn.commit()
        conn.close()
        return "User added to chat successfully"
    except Exception:
        conn.close()
        return "Database error:"


def chat_remove_user(owner_username, chat_uuid, username):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        chat_id = get_chatId(chat_uuid)
        if not chat_id:
            conn.close()
            return 'Chat not found'
        user_id = get_userId(username)
        if not user_id:
            conn.close()
            return 'User not found'
        owner_id = get_userId(owner_username)
        cursor.execute("SELECT 1 FROM secret_chats WHERE owner_id = %s and chat_id = %s" , (owner_id[0][0], chat_id[0][0]))
        right = cursor.fetchall()
        if not right:
            return 'Forbidden'
        cursor.execute("SELECT 1 FROM chat_participants WHERE user_id=%s and chat_id=%s", (user_id[0][0], chat_id[0][0]))
        participate = cursor.fetchall()
        if not participate:
            conn.close()
            return "User not in chat"
        cursor.execute("DELETE FROM chat_participants WHERE user_id = %s AND chat_id = %s", (user_id[0][0], chat_id[0][0]))
        conn.commit()
        conn.close()
        return "User removed from chat successfully"        

                        
    except Exception as e:
        conn.close()
        print(e)
        return "Database error: "
    

def save_message(chat_uuid, message, username):
    conn = dbConnect()
    cursor = conn.cursor()
    try:
        chat_id = get_chatId(chat_uuid)
        if not chat_id:
            return 'Chat is not exist'
        user_id = get_userId(username)
        if not user_id:
            return 'User is not exist'
        cursor.execute("INSERT INTO messages (chat_id, content, sender_id) VALUES (%s, %s, %s);", (chat_id[0][0], message, user_id[0][0]))
        conn.commit()

        return 'OK'
    except Exception as e:
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def get_messages(chat_uuid):
    conn = dbConnect()
    cursor = conn.cursor()

    try:
        chat_id = get_chatId(chat_uuid)
        cursor.execute("""
            SELECT m.content, m.timestamp, u.username 
            FROM messages m 
            LEFT JOIN users u ON m.sender_id = u.user_id 
            WHERE m.chat_id = %s
            ORDER BY m.timestamp ASC;
            """, (chat_id[0][0],))
        messages = cursor.fetchall()
        return messages
        
    except Exception as e:
        return 'Database error'

    finally:
        cursor.close()
        conn.close()

def get_userId(username):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username, ))
    user_id = cursor.fetchall()
    conn.close()
    return user_id


def get_chatId(chat_uuid):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM secret_chats WHERE chat_uuid = %s", (str(chat_uuid), ))
    chat_id = cursor.fetchall()
    conn.close()
    return chat_id


def check_access(username, chat_uuid):
    conn = dbConnect()
    cursor = conn.cursor()
    chat_id = get_chatId(chat_uuid)    
    if not chat_id:
        return 'Not exist chat'
    user_id = get_userId(username)
    if not user_id:
        return "Not exist user"
    cursor.execute("SELECT 1 FROM chat_participants WHERE user_id = %s and chat_id = %s ", (user_id[0][0], chat_id[0][0]))
    right = cursor.fetchall()
    if not right:
        return "no access"


def get_chatName(chat_uuid):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_name FROM secret_chats WHERE chat_uuid = %s ", (str(chat_uuid), ))
    chat_name = cursor.fetchall()[0][0]
    conn.close()
    return chat_name


def get_userChats(username):
    conn = dbConnect()
    cursor = conn.cursor()
    user_id = get_userId(username)
    cursor.execute("""SELECT s.chat_name, s.chat_uuid
           FROM chat_participants c 
           LEFT JOIN secret_chats s ON s.chat_id = c.chat_id
           WHERE user_id = %s;""",(user_id[0][0],))
    chats = cursor.fetchall()
    return chats


def get_usersInChat(username, chat_uuid):
    conn = dbConnect()
    cursor = conn.cursor()
    user_id = get_userId(username)
    chat_id = get_chatId(chat_uuid)
    cursor.execute("SELECT 1 FROM chat_participants WHERE user_id = %s and chat_id = %s", (user_id[0][0], chat_id[0][0]))
    right = cursor.fetchall()
    if not right:
        return 'no access'
    cursor.execute("""SELECT u.username
                   FROM chat_participants c
                   LEFT JOIN users u ON u.user_id = c.user_id
                   WHERE chat_id = %s""", (chat_id[0][0],))
    users = cursor.fetchall()
    return users


def get_users():
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    return users