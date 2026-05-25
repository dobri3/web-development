import os
from datetime import datetime, timezone
import logging
from integrations import check_movie_exists
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from validation import validate_ugc_payload, validate_movie_id_query, validate_status_payload
from auth import jwt_required
from permissions import roles_required

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

db = SQLAlchemy()


class UGC(db.Model):
    __tablename__ = "ugc"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text)
    rating = db.Column(db.Float)
    status = db.Column(db.String(20), nullable=False, default="pending")
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint("type IN ('review', 'comment', 'rating')", name="check_ugc_type"),
        CheckConstraint("status IN ('active', 'hidden', 'pending')", name="check_ugc_status"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 10)", name="check_ugc_rating"),
    )

    def to_dict(self) -> dict:
        created_at = self.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "rating": self.rating,
            "status": self.status,
            "movie_id": self.movie_id,
            "user_id": self.user_id,
            "created_at": created_at.isoformat().replace("+00:00", "Z"),
        }


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.getenv("FLASK_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "sqlite:///ugc.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.route("/ugc/", methods=["POST"])
    @jwt_required
    def create_ugc():
        data = request.get_json(silent=True)
        validated_data, error = validate_ugc_payload(data)
        if error:
            return jsonify(error), 400

        exists, django_available = check_movie_exists(validated_data["movie_id"])

        if not django_available:
            return jsonify({
                "error": "DJANGO_SERVICE_UNAVAILABLE",
                "detail": "Cannot verify movie existence. Try again later.",
            }), 503

        if django_available:
            return jsonify({
                "error": "MOVIE_NOT_FOUND",
                "detail": f"Movie with id {validated_data['movie_id']} not found"
            }), 404

        ugc = UGC(
            type=validated_data["type"],
            text=validated_data["text"],
            rating=validated_data["rating"],
            movie_id=validated_data["movie_id"],
            user_id=g.current_user["id"],
            status="pending",
        )
        db.session.add(ugc)
        db.session.commit()
        return jsonify({"data": ugc.to_dict()}), 201

    @app.route("/ugc/", methods=["GET"])
    def list_active_ugc():
        movie_id, error = validate_movie_id_query(request.args.get("movie_id"))
        if error:
            return jsonify(error), 400

        ugc_items = (
            UGC.query.filter_by(movie_id=movie_id, status="active")
            .order_by(UGC.created_at.desc())
            .all()
        )
        return jsonify({"data": [ugc.to_dict() for ugc in ugc_items]}), 200

    @app.route("/ugc/<int:ugc_id>/status", methods=["PATCH"])
    @jwt_required
    @roles_required("admin", "moderator")
    def update_ugc_status(ugc_id):
        ugc = db.session.get(UGC, ugc_id)
        if ugc is None:
            return jsonify({"error": "NOT_FOUND", "detail": f"UGC with id {ugc_id} not found"}), 404

        data = request.get_json(silent=True)
        status, error = validate_status_payload(data)
        if error:
            return jsonify(error), 400

        ugc.status = status
        db.session.commit()
        return jsonify({"data": ugc.to_dict()}), 200

    @app.route("/ugc/<int:ugc_id>/hide", methods=["PATCH"])
    @jwt_required
    def hide_own_ugc(ugc_id):
        ugc = UGC.query.get(ugc_id)

        if ugc is None:
            return jsonify({
                "error": "UGC_NOT_FOUND",
                "detail": "UGC item not found",
            }), 404

        current_user_id = g.current_user["id"]

        if ugc.user_id != current_user_id:
            return jsonify({
                "error": "FORBIDDEN",
                "detail": "You can hide only your own UGC",
            }), 403

        ugc.status = "hidden"
        db.session.commit()

        return jsonify({
            "data": ugc.to_dict()
        })

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    debug = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=port, debug=debug)