import hashlib


def get_token_hash(token: str):
    return hashlib.sha256(token.encode()).hexdigest()
