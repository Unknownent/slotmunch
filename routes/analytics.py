from flask import Blueprint, jsonify
from extensions import get_db_connection

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics', methods=['GET'])
def get_analytics():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS count FROM orders 
                WHERE DATE(order_time) = CURDATE()
            """)
            orders_today = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM orders 
                WHERE DATE(order_time) = CURDATE()
            """)
            revenue_today = float(cursor.fetchone()['revenue'])

            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM orders")
            total_revenue = float(cursor.fetchone()['revenue'])

            cursor.execute("SELECT COUNT(*) AS count FROM orders")
            total_orders = cursor.fetchone()['count']

            cursor.execute("""
                SELECT status, COUNT(*) AS count FROM orders GROUP BY status
            """)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

            cursor.execute("""
                SELECT m.name, SUM(oi.quantity) as total_qty
                FROM order_items oi
                JOIN menu_items m ON oi.item_id = m.item_id
                GROUP BY m.name
                ORDER BY total_qty DESC
                LIMIT 5
            """)
            top_items = [{'name': row['name'], 'quantity': row['total_qty']} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT DATE(order_time) as day, COALESCE(SUM(total_amount), 0) as revenue
                FROM orders
                WHERE order_time >= CURDATE() - INTERVAL 7 DAY
                GROUP BY day
                ORDER BY day ASC
            """)
            revenue_by_day = [{'day': str(row['day']), 'revenue': float(row['revenue'])} for row in cursor.fetchall()]

        return jsonify({
            'orders_today': orders_today,
            'revenue_today': revenue_today,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'status_counts': status_counts,
            'top_items': top_items,
            'revenue_by_day': revenue_by_day
        }), 200
    finally:
        conn.close()