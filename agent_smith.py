import openai
import fire
import difflib
import subprocess
import sys
import json
from termcolor import cprint


def run_script(script_name, script_args):
    script_args = [str(arg) for arg in script_args]
    try:
        result = subprocess.check_output(
            [sys.executable, script_name] + script_args,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), e.returncode
    return result.decode("utf-8"), 0


def run_black(script_name):
    try:
        result = subprocess.check_output(
            ["black", script_name], stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), e.returncode
    return result.decode("utf-8"), 0


def run_flake8(script_name):
    try:
        result = subprocess.check_output(
            ["flake8", script_name], stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), e.returncode
    return result.decode("utf-8"), 0


# function for sending request to OpenAI API
def send_request(
    prompt,
    model,
    max_tokens,
    temperature,
    top_p,
    frequency_penalty,
    presence_penalty
):
    # print(f"Sending request to OpenAI API..., prompt: {prompt}")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=1.0,
    )
    return response


# function for formatting the response
def format_response(response):
    return response.choices[0].message.content.strip()


# function for getting the response
def get_response(
    prompt,
    model,
    max_tokens,
    temperature,
    top_p,
    frequency_penalty,
    presence_penalty
):
    response = send_request(
        prompt,
        model,
        max_tokens,
        temperature,
        top_p,
        frequency_penalty,
        presence_penalty,
    )
    return format_response(response)


def load_lint_fix_initial_prompt():
    with open("./prompt/lint_fix.txt", "r") as f:
        prompt = f.read()
    # print(f"Loaded prompt: {prompt}")
    return prompt


def load_code_fix_initial_prompt():
    with open("./prompt/code_fix.txt", "r") as f:
        prompt = f.read()
    # print(f"Loaded prompt: {prompt}")
    return prompt


# read file with lines, and with the line number in front of each line as
# of line number: content
def read_file_with_lines(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    file_with_lines = ""
    for i, line in enumerate(lines):
        file_with_lines += f"{i+1}: {line}"
    return file_with_lines


# function for fix code for errors
def fix_code_errors(file_path, args, error_message, model):
    file_with_lines = read_file_with_lines(file_path)

    initial_prompt_text = load_code_fix_initial_prompt()
    prompt = (
        initial_prompt_text + "\n\n"
        "Here is the script that needs fixing:\n\n"
        f"{file_with_lines}\n\n"
        "Here are the arguments it was provided:\n\n"
        f"{args}\n\n"
        "Here is the error message:\n\n"
        f"{error_message}\n"
        "Please provide your suggested changes, and remember to stick to the "
        "exact format as described above."
    )
    response = get_response(prompt, model, 100, 0.9, 1, 0, 0)
    return response


# function for fix code for linting errors
def fix_lint_errors(file_path, args, error_message, model):
    file_with_lines = read_file_with_lines(file_path)

    initial_prompt_text = load_lint_fix_initial_prompt()
    prompt = (
        initial_prompt_text + "\n\n"
        "Here is the script that needs fixing:\n\n"
        f"{file_with_lines}\n\n"
        "Here are the arguments it was provided:\n\n"
        f"{args}\n\n"
        "Here is the flake8 lint error message:\n\n"
        f"{error_message}\n"
        "Please provide your suggested changes, and remember to stick to the "
        "exact format as described above."
    )
    response = get_response(prompt, model, 100, 0.9, 1, 0, 0)
    return response


def apply_changes(file_path, changes_json):
    # Read the original file lines
    with open(file_path, "r") as f:
        orig_lines = f.readlines()

    print(f"Applying changes based on {changes_json}...")
    # Parse the changes from the JSON string
    changes = json.loads(changes_json)

    # Extract the operation changes and explanations
    op_changes = [change for change in changes if "operation" in change]
    explanations = [
        change["explanation"] for change in changes if "explanation" in change
    ]

    # Sort the operation changes in reverse line order
    op_changes.sort(key=lambda x: x["line"], reverse=True)

    # Apply the operation changes to the file lines
    new_lines = orig_lines.copy()
    for change in op_changes:
        op = change["operation"]
        line_num = change["line"]
        content = change["content"]

        if op == "Replace":
            new_lines[line_num - 1] = content + "\n"
        elif op == "Delete":
            del new_lines[line_num - 1]
        elif op == "InsertAfter":
            new_lines.insert(line_num, content + "\n")

    # Write the modified file lines to the file
    with open(file_path, "w") as f:
        f.writelines(new_lines)

    # Print the explanations in blue
    cprint("Explanations:", "blue")
    for explanation in explanations:
        cprint(f"- {explanation}", "blue")

    # Print the changes in green or red using unified diff
    cprint("\nChanges:", "magenta")
    diff = difflib.unified_diff(orig_lines, new_lines, lineterm="")
    for line in diff:
        if line.startswith("+"):
            cprint(line, "green", end="")
        elif line.startswith("-"):
            cprint(line, "red", end="")
        else:
            print(line, end="")


def main(script_name, *script_args, model="gpt-4"):

    while True:
        output, returncode = run_script(script_name, script_args)

        if returncode == 0:
            cprint("Script ran successfully.", "blue")

            # run flake8 to check for PEP8 errors
            # run_black(script_name)
            flake8_output, flake8_returncode = run_flake8(script_name)

            if flake8_returncode != 0:
                print("PEP8 errors:", flake8_output)
                json_response = fix_lint_errors(
                    file_path=script_name,
                    args=script_args,
                    error_message=flake8_output,
                    model=model,
                )
                apply_changes(script_name, json_response)
                cprint("Changes applied. Rerunning...", "blue")
                continue
            else:
                cprint("Script passed lint check", "blue")

            print("Output:", output)
            break
        else:
            cprint("Script crashed. Trying to fix...", "blue")
            print("Output:", output)

            json_response = fix_code_errors(
                file_path=script_name,
                args=script_args,
                error_message=output,
                model=model,
            )
            apply_changes(script_name, json_response)
            cprint("Changes applied. Rerunning...", "blue")


if __name__ == "__main__":
    fire.Fire(main)
