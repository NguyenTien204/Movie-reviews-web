import os

# Các từ khóa con thường xuất hiện trong thư mục cần loại
EXCLUDED_KEYWORDS = [
    '.venv', 'venv', 'env', '__pycache__', '.git', 'node_modules',
    '.idea', '.pytest_cache', '.mypy_cache', '.cache', '.next', '.vscode'
]

# Các phần mở rộng file cần loại
EXCLUDED_EXTENSIONS = {'.pyc', '.pyo', '.log', '.sqlite3'}

def should_exclude(name, is_dir):
    lower = name.lower()
    if any(keyword in lower for keyword in EXCLUDED_KEYWORDS):
        return True
    if not is_dir:
        _, ext = os.path.splitext(name)
        return ext in EXCLUDED_EXTENSIONS
    return False

def print_tree(path, prefix=""):
    try:
        entries = os.listdir(path)
    except PermissionError:
        print(prefix + "└── [Permission Denied]")
        return

    entries = [e for e in entries if not should_exclude(e, os.path.isdir(os.path.join(path, e)))]
    entries.sort()

    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(full_path, prefix + extension)

# Dùng thử
print_tree(".")

# Gọi hàm:
print_tree("D:\WorkSpace\Do-an-2\Data_Pipeline")  # Hoặc thay "." bằng đường dẫn thư mục dự án
