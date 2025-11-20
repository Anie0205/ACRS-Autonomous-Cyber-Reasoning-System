import tempfile
with tempfile.NamedTemporaryFile(delete=True) as f:
    f.write(b"test")
