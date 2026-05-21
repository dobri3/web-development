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

    if not isinstance(movie_id, int) or isinstance(movie_id, bool):
        return None, validation_error("movie_id must be a number")

    validated_data = {
        "type": ugc_type,
        "text": text.strip(),
        "rating": rating,
        "movie_id": movie_id,
    }

    return validated_data, None