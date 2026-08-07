from flask import Blueprint, request, jsonify
from extensions import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    staff_id = data.get("staff_id")
    password = data.get("password")

    if not staff_id or not password:
        return jsonify({"error": "staff_id and password are required"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
            staff = cursor.fetchone()

        if not staff:
            return jsonify({"error": "Staff ID not found"}), 404

        if not staff["password"] or not check_password_hash(staff["password"], password):
            return jsonify({"error": "Invalid staff ID or password"}), 401

        return jsonify({
            "staff_id": staff["staff_id"],
            "role": staff["role"],
            "full_name": staff["full_name"]
        }), 200
    finally:
        conn.close()


@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    """
    Temporary/admin route to set a password for an existing staff record.
    """
    data = request.get_json()
    staff_id = data.get("staff_id")
    new_password = data.get("password")

    if not staff_id or not new_password:
        return jsonify({"error": "staff_id and password are required"}), 400

    hashed_pw = generate_password_hash(new_password)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE staff SET password = %s WHERE staff_id = %s",
                (hashed_pw, staff_id)
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Staff ID not found"}), 404
        conn.commit()
        return jsonify({"message": "Password set successfully"}), 200
    finally:
        conn.close()