from flask import Blueprint, request, jsonify
from extensions import get_db_connection

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/staff', methods=['GET'])
def get_staff():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM staff")
            staff_list = cursor.fetchall()

        result = [
            {
                'staff_id': staff['staff_id'],
                'full_name': staff['full_name'],
                'department': staff['department'],
                'role': staff['role'],
                'email': staff['email'],
                'floor_number': staff.get('floor_number')
            }
            for staff in staff_list
        ]
        return jsonify(result), 200
    finally:
        conn.close()


@staff_bp.route('/staff', methods=['POST'])
def add_staff():
    data = request.get_json()
    staff_id = data.get('staff_id')
    full_name = data.get('full_name')
    department = data.get('department')
    role = data.get('role')
    email = data.get('email')
    floor_number = data.get('floor_number')

    if not staff_id or not full_name or not role:
        return jsonify({'error': 'Staff ID, full name and role are required'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO staff (staff_id, full_name, department, role, email, floor_number) VALUES (%s, %s, %s, %s, %s, %s)",
                (staff_id, full_name, department, role, email, floor_number)
            )
        conn.commit()
        return jsonify({'message': 'Staff member added successfully'}), 201
    finally:
        conn.close()


@staff_bp.route('/staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    data = request.get_json()
    full_name = data.get('full_name')
    department = data.get('department')
    role = data.get('role')
    email = data.get('email')
    floor_number = data.get('floor_number')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE staff 
                   SET full_name = COALESCE(%s, full_name),
                       department = COALESCE(%s, department),
                       role = COALESCE(%s, role),
                       email = COALESCE(%s, email),
                       floor_number = COALESCE(%s, floor_number)
                   WHERE staff_id = %s""",
                (full_name, department, role, email, floor_number, staff_id)
            )
        conn.commit()
        return jsonify({'message': 'Staff member updated successfully'}), 200
    finally:
        conn.close()


@staff_bp.route('/staff/<staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
        conn.commit()
        return jsonify({'message': 'Staff member deleted successfully'}), 200
    finally:
        conn.close()