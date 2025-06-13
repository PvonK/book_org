# formatter.py

import subprocess
import os


def get_terminal_columns():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Fallback


def log(action, text, noprint=False):
    columns = get_terminal_columns()
    with open("logfile.txt", "a+") as logfile:
        logfile.write(f"{action} {text}\n")
    if noprint:
        return

    if action == "[SEPARATOR]":
        print(action, text[0]*(columns-12))
    else:
        print(action, text)


def print_selection(dict_list):
    if not dict_list:
        print("No items to display.")
        return

    columns = get_terminal_columns()

    show_image = can_display_images()

    for idx, item in enumerate(dict_list):
        print(f"\n\033[1m[{idx}]\033[0m")  # Bold index
        for key, value in item.items():
            if key == "image_url" and value:
                if show_image:
                    show_image_in_kitty(value)
            elif value:  # Skip empty fields for clarity
                print(f"  \033[94m{key.capitalize():<10}\033[0m: {value}")
        print("-"*columns)
    print("\nSelect an item by index")


def progress_bar(total, processed):
    columns = get_terminal_columns()
    if columns < 6:
        return

    progress_columns = columns-6

    if total == 0:
        print("100%", "#"*progress_columns)
        return

    bars_per_completed_file = progress_columns/total
    fill = processed * bars_per_completed_file

    empty = progress_columns-fill

    progress = "#"*int(fill) + " "*int(empty)

    percentage = f"{(processed / total) * 100:.1f}"
    print(f"{percentage.rjust(5)}% {progress}")


def can_display_images():
    # TODO check if terminal can display images
    return True


def show_image_in_kitty(image_path):
    try:
        subprocess.run([
            "kitty",
            "+kitten",
            "icat",
            "--align",
            "left",
            image_path,
            ])
    except Exception:
        pass
