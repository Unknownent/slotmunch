from flask import Blueprint, request, jsonify
from extensions import get_db_connection

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/menu', methods=['GET'])
def get_menu():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM menu_items WHERE is_available = TRUE")
            items = cursor.fetchall()

        menu = [
            {
                'item_id': item['item_id'],
                'name': item['name'],
                'category': item['category'],
                'price': float(item['price']),
                'description': item['description']
            }
            for item in items
        ]
        return jsonify(menu), 200
    finally:
        conn.close()


@menu_bp.route('/menu/all', methods=['GET'])
def get_all_menu_items():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM menu_items")
            items = cursor.fetchall()

        menu = [
            {
                'item_id': item['item_id'],
                'name': item['name'],
                'category': item['category'],
                'price': float(item['price']),
                'is_available': bool(item['is_available']),
                'description': item['description']
            }
            for item in items
        ]
        return jsonify(menu), 200
    finally:
        conn.close()


@menu_bp.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    description = data.get('description', '')

    if not name or not price:
        return jsonify({'error': 'Name and price are required'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO menu_items (name, category, price, description) VALUES (%s, %s, %s, %s)",
                (name, category, price, description)
            )
        conn.commit()
        return jsonify({'message': 'Menu item added successfully'}), 201
    finally:
        conn.close()


@menu_bp.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    is_available = data.get('is_available')
    description = data.get('description')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE menu_items 
                   SET name = COALESCE(%s, name),
                       price = COALESCE(%s, price),
                       category = COALESCE(%s, category),
                       is_available = COALESCE(%s, is_available),
                       description = COALESCE(%s, description)
                   WHERE item_id = %s""",
                (name, price, category, is_available, description, item_id)
            )
        conn.commit()
        return jsonify({'message': 'Menu item updated successfully'}), 200
    finally:
        conn.close()


@menu_bp.route('/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM menu_items WHERE item_id = %s", (item_id,))
        conn.commit()
        return jsonify({'message': 'Menu item deleted successfully'}), 200
    finally:
        conn.close()