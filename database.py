import sqlite3

DB_NAME = "anon_bot.db"


def init_db():
    """Создаёт таблицы, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Таблица для связи ссылка -> владелец бота
    cur.execute("""
                CREATE TABLE IF NOT EXISTS links
                (
                    link_key
                    TEXT
                    PRIMARY
                    KEY,
                    owner_id
                    INTEGER
                    NOT
                    NULL
                )
                """)

    # Таблица для анонимных сообщений
    cur.execute("""
                CREATE TABLE IF NOT EXISTS messages
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    link_key
                    TEXT
                    NOT
                    NULL,
                    from_user_id
                    INTEGER
                    NOT
                    NULL,
                    message_text
                    TEXT,
                    reply_to
                    INTEGER
                    DEFAULT
                    NULL
                )
                """)

    conn.commit()
    conn.close()


def save_link(key, owner_id):
    """Сохраняет уникальную ссылку за владельцем"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO links VALUES (?, ?)", (key, owner_id))
    conn.commit()
    conn.close()


def get_owner_by_key(key):
    """Кому принадлежит ссылка"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT owner_id FROM links WHERE link_key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def save_message(key, from_user_id, text, reply_to=None):
    """Сохраняет сообщение"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (link_key, from_user_id, message_text, reply_to) VALUES (?, ?, ?, ?)",
        (key, from_user_id, text, reply_to)
    )
    conn.commit()
    conn.close()


def get_last_message_by_user(link_key, from_user_id):
    """Получить последнее сообщение пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, message_text FROM messages WHERE link_key = ? AND from_user_id = ? ORDER BY id DESC LIMIT 1",
        (link_key, from_user_id)
    )
    row = cur.fetchone()
    conn.close()
    return row