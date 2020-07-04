import os
import tempfile

database_path = os.path.join(
        os.environ.get("DATABASE_DIR", tempfile.mkdtemp()),
        "myproject.sqlite3.db")
large_tasks_size_threshold = 1000
