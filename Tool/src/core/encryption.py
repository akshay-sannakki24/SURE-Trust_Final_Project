import os
import mmap
import struct
import hashlib
import multiprocessing as mp
from Crypto.Cipher import Blowfish

# ============================================================
# Optimized for Intel i5 (4 cores / 8 threads)
# ============================================================
CHUNK_SIZE = 64 * 1024 * 1024   # 32 MB sweet spot for i5
WORKERS = 4                     # physical cores only (ignore HT)

# ---------------- Worker functions ----------------

def _encrypt_worker(args):
    """
    Encrypt a single chunk.
    Each worker creates its own cipher ONCE per task.
    """
    index, data, key = args
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)

    # PKCS-style padding to 8 bytes
    pad = 8 - (len(data) % 8)
    data += bytes([pad]) * pad

    return index, cipher.encrypt(data)


def _decrypt_worker(args):
    """
    Decrypt a single chunk.
    """
    index, data, key = args
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    return index, cipher.decrypt(data)


# ---------------- Main class ----------------

class BlowfishEncryptor:
    def __init__(self):
        # Fixed to physical cores for i5
        self.workers = WORKERS

    # ---------- ENCRYPT ----------
    def encrypt_file(self, path, password, keep_name=True, secure_delete=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # Derive Blowfish key (max 56 bytes)
        key = hashlib.sha256(password).digest()[:56]
        size = os.path.getsize(path)

        # Output naming
        if keep_name:
            out_base = os.path.splitext(path)[0]
        else:
            out_base = hashlib.sha256(os.path.basename(path).encode()).hexdigest()[:12]
        out_path = out_base + ".aa"

        with open(path, "rb") as f_in, open(out_path, "wb") as f_out:
            # Memory-map input for zero-copy reads
            mm = mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ)

            # Write original size header (8 bytes)
            f_out.write(struct.pack(">Q", size))

            jobs = []
            idx = 0
            for offset in range(0, size, CHUNK_SIZE):
                jobs.append((idx, mm[offset:offset + CHUNK_SIZE], key))
                idx += 1

            # Parallel encryption
            with mp.Pool(self.workers) as pool:
                # map preserves order only by index sorting
                encrypted_chunks = pool.map(_encrypt_worker, jobs)

            # Write in correct order
            for _, enc in sorted(encrypted_chunks, key=lambda x: x[0]):
                f_out.write(enc)

            mm.close()

        if secure_delete:
            self._secure_delete(path)

        return out_path

    # ---------- DECRYPT ----------
    def decrypt_file(self, path, password, secure_delete=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        key = hashlib.sha256(password).digest()[:56]

        with open(path, "rb") as f_in:
            orig_size = struct.unpack(">Q", f_in.read(8))[0]
            encrypted_data = f_in.read()

        jobs = []
        idx = 0
        for offset in range(0, len(encrypted_data), CHUNK_SIZE):
            jobs.append((idx, encrypted_data[offset:offset + CHUNK_SIZE], key))
            idx += 1

        with mp.Pool(self.workers) as pool:
            decrypted_chunks = pool.map(_decrypt_worker, jobs)

        # Reassemble and trim padding
        plaintext = b"".join(d for _, d in sorted(decrypted_chunks, key=lambda x: x[0]))
        plaintext = plaintext[:orig_size]

        out_path = path.replace(".aa", ".dec")
        with open(out_path, "wb") as f_out:
            f_out.write(plaintext)

        if secure_delete:
            self._secure_delete(path)

        return out_path

    # ---------- INTEGRITY (simple existence check here) ----------
    # Your project already maintains hash tables elsewhere
    def verify_file(self, path):
        return os.path.exists(path)

    # ---------- SECURE DELETE ----------
    def _secure_delete(self, path):
        try:
            size = os.path.getsize(path)
            with open(path, "wb") as f:
                f.write(os.urandom(size))
            os.remove(path)
        except Exception:
            pass
