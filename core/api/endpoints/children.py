from flask import jsonify, request, current_app
from datetime import datetime
from .. import api_bp
from ..middleware.auth import require_parent_auth


@api_bp.route('/children', methods=['GET'])
@require_parent_auth
def list_children():
    """List children with real data"""
    try:
        orchestrator = current_app.orchestrator

        if orchestrator and hasattr(orchestrator, 'child_repository'):
            # استخدم البيانات الحقيقية
            children = orchestrator.child_repository.find_by_parent(
                request.parent_id)
            children_data = [child.to_dict() for child in children]
        else:
            # Mock data للتطوير
            children_data = [{
                "id": "child_1",
                "name": "أحمد",
                "age": 7
            }]

        return jsonify({"children": children_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/children', methods=['POST'])
@require_parent_auth
def create_child():
    """Create new child profile"""
    try:
        data = request.json
        name = data.get('name')
        age = data.get('age')
        preferences = data.get('preferences', {})

        if not name or not age:
            return jsonify({"error": "Name and age required"}), 400

        # Mock creation - replace with actual database insert
        child = {
            "id": f"child_{name.lower()}",
            "name": name,
            "age": age,
            "preferences": preferences,
            "created_at": datetime.utcnow().isoformat()
        }

        return jsonify({"child": child, "created": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/children/<child_id>', methods=['PUT'])
@require_parent_auth
def update_child(child_id):
    """Update child profile"""
    try:
        data = request.json

        # Mock update - replace with actual database update
        updated_child = {
            "id": child_id,
            "updated": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        return jsonify(updated_child), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
