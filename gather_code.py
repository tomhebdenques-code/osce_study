import os

output_file = "project_context.txt"
exclude_dirs = {'venv', '.git', '__pycache__'}

with open(output_file, "w") as f:
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(".py") or file.endswith(".html") or file.endswith(".css"):
                file_path = os.path.join(root, file)
                f.write(f"\n--- FILE: {file_path} ---\n")
                try:
                    with open(file_path, "r") as code_f:
                        f.write(code_f.read())
                except Exception as e:
                    f.write(f"Error reading file: {e}")
                f.write("\n")

print(f"Done! Your code is ready in {output_file}")
