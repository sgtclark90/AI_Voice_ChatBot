import os

# Base path for the public folder
# base_path = "public/"
base_path = ""

# List of files to process
files = [
    "main.py",
    "database_manager.py",
    "chatgpt_responder.py",
    "audio_manager.py",
    ".env",
]

def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"Error reading '{file_path}': {str(e)}"

def format_contents(files):
    formatted_output = ""
    for file in files:
        full_path = os.path.join(base_path, file)
        contents = read_file_contents(full_path)
        formatted_output += f"```\n{file}\n```\n{contents}\n```\n\n"
    return formatted_output.strip()

def write_output_to_file(output, filename="prompt.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(output)
        print(f"Output successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")

if __name__ == "__main__":
    output = format_contents(files)
    write_output_to_file(output)