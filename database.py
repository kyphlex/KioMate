import sqlite3
from datetime import datetime
import json
from contextlib import contextmanager

DATABASE_PATH = "kiomate.db"


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                business_id TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                business_type TEXT NOT NULL,
                location TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)

        # Insights history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                customer_profile TEXT,
                peak_hours TEXT,
                pricing_strategy TEXT,
                quick_wins TEXT,
                competition_insight TEXT,
                growth_opportunity TEXT,
                generated_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES users(business_id)
            )
        """)

        # API usage tracking (for future monetization)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES users(business_id)
            )
        """)

        conn.commit()


def save_user(business_id, business_name, business_type, location):
    """Save new user to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (business_id, business_name, business_type, location, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (business_id, business_name, business_type, location, datetime.now().isoformat()))
        conn.commit()

        return {
            'business_id': business_id,
            'business_name': business_name,
            'business_type': business_type,
            'location': location,
            'created_at': datetime.now().isoformat()
        }


def get_user(business_id):
    """Retrieve user by business ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE business_id = ?
        """, (business_id,))

        row = cursor.fetchone()
        if row:
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE business_id = ?
            """, (datetime.now().isoformat(), business_id))
            conn.commit()

            return dict(row)
        return None


def save_insight(business_id, insights):
    """Save generated insights to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO insights (
                business_id, customer_profile, peak_hours, pricing_strategy,
                quick_wins, competition_insight, growth_opportunity, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id,
            insights['customer_profile'],
            insights['peak_hours'],
            insights['pricing_strategy'],
            json.dumps(insights['quick_wins']),
            insights['competition_insight'],
            insights['growth_opportunity'],
            datetime.now().isoformat()
        ))
        conn.commit()


def get_user_insights(business_id, limit=10):
    """Get insights history for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM insights 
            WHERE business_id = ? 
            ORDER BY generated_at DESC 
            LIMIT ?
        """, (business_id, limit))

        rows = cursor.fetchall()
        insights_list = []
        for row in rows:
            insight = dict(row)
            # Parse quick_wins JSON string back to list
            try:
                insight['quick_wins'] = json.loads(insight['quick_wins'])
            except:
                insight['quick_wins'] = []
            insights_list.append(insight)

        return insights_list


def track_api_usage(business_id, action):
    """Track API usage for analytics"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_usage (business_id, action, timestamp)
            VALUES (?, ?, ?)
        """, (business_id, action, datetime.now().isoformat()))
        conn.commit()


def get_user_stats(business_id):
    """Get user statistics"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total insights generated
        cursor.execute("""
            SELECT COUNT(*) as count FROM insights WHERE business_id = ?
        """, (business_id,))
        insights_count = cursor.fetchone()['count']

        # User info
        cursor.execute("""
            SELECT created_at, last_login FROM users WHERE business_id = ?
        """, (business_id,))
        user_info = dict(cursor.fetchone())

        return {
            'insights_count': insights_count,
            'member_since': user_info['created_at'],
            'last_login': user_info['last_login']
        }


# For migration/backup
def export_user_data(business_id):
    """Export all user data as JSON"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get user info
        cursor.execute("SELECT * FROM users WHERE business_id = ?", (business_id,))
        user = dict(cursor.fetchone())

        # Get all insights
        cursor.execute("SELECT * FROM insights WHERE business_id = ?", (business_id,))
        insights = [dict(row) for row in cursor.fetchall()]

        return {
            'user': user,
            'insights': insights,
            'exported_at': datetime.now().isoformat()
        }


# Initialize database when module is imported
init_database()