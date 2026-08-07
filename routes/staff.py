from flask import Blueprint, request, jsonify
from extensions import get_db_connection
from werkzeug.security import generate_password_hash
from functools import wraps

staff_bp = Blueprint('staff', __name__)


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        requester_id = request.headers.get('X-Staff-Id')
        if not requester_id:
            return jsonify({'error': 'Not authenticated'}), 401

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT role FROM staff WHERE staff_id = %s", (requester_id,))
                requester = cursor.fetchone()
        finally:
            conn.close()

        if not requester or requester['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)
    return wrapper


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
@require_admin
def add_staff():
    data = request.get_json()
    staff_id = data.get('staff_id')
    full_name = data.get('full_name')
    department = data.get('department')
    role = data.get('role')
    email = data.get('email')
    floor_number = data.get('floor_number')
    password = data.get('password')

    if not staff_id or not full_name or not role:
        return jsonify({'error': 'Staff ID, full name and role are required'}), 400

    hashed_pw = generate_password_hash(password) if password else ''

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO staff (staff_id, full_name, department, role, email, floor_number, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (staff_id, full_name, department, role, email, floor_number, hashed_pw)
            )
        conn.commit()
        return jsonify({'message': 'Staff member added successfully'}), 201
    finally:
        conn.close()


@staff_bp.route('/staff/<staff_id>', methods=['PUT'])
@require_admin
def update_staff(staff_id):
    data = request.get_json()
    full_name = data.get('full_name')
    department = data.get('department')
    role = data.get('role')
    email = data.get('email')
    floor_number = data.get('floor_number')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if password:
                hashed_pw = generate_password_hash(password)
                cursor.execute(
                    """UPDATE staff 
                       SET full_name = COALESCE(%s, full_name),
                           department = COALESCE(%s, department),
                           role = COALESCE(%s, role),
                           email = COALESCE(%s, email),
                           floor_number = COALESCE(%s, floor_number),
                           password = %s
                       WHERE staff_id = %s""",
                    (full_name, department, role, email, floor_number, hashed_pw, staff_id)
                )
            else:
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
@require_admin
def delete_staff(staff_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
        conn.commit()
        return jsonify({'message': 'Staff member deleted successfully'}), 200
    finally:
        conn.close()