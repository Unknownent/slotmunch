from flask import Blueprint, request, jsonify
from extensions import get_db_connection

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    staff_id = data.get('staff_id')
    items = data.get('items')
    notes = data.get('notes', '')

    if not staff_id or not items:
        return jsonify({'error': 'Missing required fields'}), 400

    total = sum(item['price'] * item['quantity'] for item in items)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (staff_id, total_amount, notes) VALUES (%s, %s, %s)",
                (staff_id, total, notes)
            )
            order_id = cursor.lastrowid

            for item in items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                    (order_id, item['item_id'], item['quantity'], item['price'])
                )

        conn.commit()
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id,
            'total': total
        }), 201
    finally:
        conn.close()


@orders_bp.route('/orders', methods=['GET'])
def get_all_orders():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT o.order_id, o.staff_id, s.full_name, o.order_time, 
                       o.status, o.total_amount, o.payment_status, o.notes
                FROM orders o
                JOIN staff s ON o.staff_id = s.staff_id
                ORDER BY o.order_time DESC
            """)
            orders = cursor.fetchall()

            result = []
            for order in orders:
                cursor.execute("""
                    SELECT m.name, oi.quantity, oi.unit_price
                    FROM order_items oi
                    JOIN menu_items m ON oi.item_id = m.item_id
                    WHERE oi.order_id = %s
                """, (order['order_id'],))
                items = cursor.fetchall()

                items_list = [
                    {'name': i['name'], 'quantity': i['quantity'], 'price': float(i['unit_price'])}
                    for i in items
                ]

                result.append({
                    'order_id': order['order_id'],
                    'staff_id': order['staff_id'],
                    'staff_name': order['full_name'],
                    'order_time': str(order['order_time']),
                    'status': order['status'],
                    'total_amount': float(order['total_amount']),
                    'payment_status': order['payment_status'],
                    'notes': order['notes'],
                    'items': items_list
                })

        return jsonify(result), 200
    finally:
        conn.close()


@orders_bp.route('/orders/<staff_id>', methods=['GET'])
def get_orders(staff_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM orders WHERE staff_id = %s ORDER BY order_time DESC",
                (staff_id,)
            )
            orders = cursor.fetchall()

            result = []
            for order in orders:
                cursor.execute("""
                    SELECT m.name, oi.quantity, oi.unit_price
                    FROM order_items oi
                    JOIN menu_items m ON oi.item_id = m.item_id
                    WHERE oi.order_id = %s
                """, (order['order_id'],))
                items = cursor.fetchall()

                items_list = [
                    {'name': i['name'], 'quantity': i['quantity'], 'price': float(i['unit_price'])}
                    for i in items
                ]

                result.append({
                    'order_id': order['order_id'],
                    'order_time': str(order['order_time']),
                    'status': order['status'],
                    'total_amount': float(order['total_amount']),
                    'payment_status': order['payment_status'],
                    'notes': order['notes'],
                    'items': items_list
                })

        return jsonify(result), 200
    finally:
        conn.close()


@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    status = data.get('status')
    payment_status = data.get('payment_status')
    validated_by = data.get('validated_by')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE orders 
                   SET status = COALESCE(%s, status),
                       payment_status = COALESCE(%s, payment_status),
                       validated_by = COALESCE(%s, validated_by)
                   WHERE order_id = %s""",
                (status, payment_status, validated_by, order_id)
            )
        conn.commit()
        return jsonify({'message': 'Order updated successfully'}), 200
    finally:
        conn.close()