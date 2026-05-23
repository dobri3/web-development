ALLOWED_UGC_TYPES = {"review", "comment", "rating"}


def validation_error(detail: str) -> dict:
    return {
        "error": "VALIDATION_ERROR",
        "detail": detail,
    }


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_ugc_payload(data: dict):
    if not isinstance(data, dict):
        return None, validation_error("request body must be a JSON object")

    ugc_type = data.get("type")
    text = data.get("text")
    rating = data.get("rating")
    movie_id = data.get("movie_id")

    if text is None or not isinstance(text, str) or not text.strip():
        return None, validation_error("text cannot be empty")

    if len(text) > 1000:
        return None, validation_error(
            "text cannot be longer than 1000 characters"
        )

    if not is_number(rating):
        return None, validation_error("rating must be a number from 1 to 10")

    if rating < 1 or rating > 10:
        return None, validation_error("rating must be a number from 1 to 10")

    if ugc_type not in ALLOWED_UGC_TYPES:
        return None, validation_error(
            "type must be one of: review, comment, rating"
        )

    if movie_id is None:
        return None, validation_error("movie_id is required")

    if movie_id <= 0:
        return None, validation_error("movie_id must be a positive number")

    if not isinstance(movie_id, int) or isinstance(movie_id, bool):
        return None, validation_error("movie_id must be a number")

    validated_data = {
        "type": ugc_type,
        "text": text.strip(),
        "rating": rating,
        "movie_id": movie_id,
    }

    return validated_data, None

def validate_movie_id_query(raw_movie_id: str | None):
    if raw_movie_id is None:
        return None, validation_error("movie_id is required")

    try:
        movie_id = int(raw_movie_id)
    except (TypeError, ValueError):
        return None, validation_error("movie_id must be a number")

    if movie_id <= 0:
        return None, validation_error("movie_id must be a positive number")

    return movie_id, None

ALLOWED_STATUSES = {"active", "hidden", "pending"}

def validate_status_payload(data):
    if not isinstance(data, dict):
        return None, validation_error("request body must be a JSON object")

    status = data.get("status")

    if not status or not isinstance(status, str):
        return None, validation_error("status is required")

    if status not in ALLOWED_STATUSES:
        return None, validation_error("status must be one of: active, hidden, pending")

    return status, None