import subprocess

scripts = [
    "setup.install_requirements",
    "setup.init_postgres",
    "setup.init_mongodb"
]

def run_script(module_path):
    print(f"\n==> Running {module_path}...")
    result = subprocess.run(["python", "-m", module_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"ERROR: {module_path} failed.")

def main():
    print("  Starting project setup...\n")
    for script in scripts:
        run_script(script)
    print("\nSUCCESS: All setup steps completed.")

if __name__ == "__main__":
    main()
