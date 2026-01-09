
import hashlib

class SHA256Handler:
    @staticmethod
    def calculate_file_hash(file_path):
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8 * 1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
