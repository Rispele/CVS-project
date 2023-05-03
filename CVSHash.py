import hashlib


def get_cvs_hash(content):
    return hashlib.sha1(content.encode("utf-8")).hexdigest()