from flask import Blueprint, request, jsonify
from extensions import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    staff_id = data.get("staff_id")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
            staff = cursor.fetchone()

        if not staff:
            return jsonify({"error": "Staff ID not found"}), 404

        # DictCursor returns column names as keys, so this reads more
        # safely than the old index-based staff[0] / staff[3] pattern.
        return jsonify({
            "staff_id": staff["staff_id"],
            "role": staff["role"],
            "full_name": staff["full_name"]
        }), 200
    finally:
        conn.close()