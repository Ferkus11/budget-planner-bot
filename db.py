import sqlite3

# 🔧 Инициализация базы данных
def init_db():
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            category TEXT,
            amount INTEGER,
            record_type TEXT DEFAULT 'expense'
        )
    """)
    conn.commit()
    conn.close()

# ➕ Добавление записи (трата или доход)
def add_record(user_id: int, category: str, amount: int, record_type="expense"):
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (user_id, category, amount, record_type) VALUES (?, ?, ?, ?)",
        (user_id, category, amount, record_type)
    )
    conn.commit()
    conn.close()

# 🗑 Удаление последней записи
def delete_last_expense(user_id: int):
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM expenses
        WHERE id = (
            SELECT id FROM expenses WHERE user_id = ?
            ORDER BY id DESC LIMIT 1
        )
    """, (user_id,))
    conn.commit()
    conn.close()

# 🧹 Удаление всех записей по категории
def delete_category(user_id: int, category: str):
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM expenses WHERE user_id = ? AND category = ?",
        (user_id, category.lower())
    )
    conn.commit()
    conn.close()

# 📊 Получение статистики по тратам
def get_statistics(user_id: int):
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = ? AND record_type = 'expense'
        GROUP BY category
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()



    return rows
def get_income_statistics(user_id: int):
    conn = sqlite3.connect(".gitignore/expenses.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = ? AND record_type = 'income'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows