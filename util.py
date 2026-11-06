import re
import requests
import subprocess


# 17.25.2-r11b9cbe3 -> 17.25.2
def strip_build_id(tag) -> str:
    return tag.split('-', 1)[0]


# 17.25.2-r11b9cbe3-2 -> 17.25.2-r11b9cbe3; unmodified otherwise
def strip_force_suffix(tag) -> str:
    return re.sub(r"-\d{1,2}$", "", tag)


# gets last tag of GitHub project
def get_last_github_tag(project_name) -> str:
    releases_url = f"https://api.github.com/repos/{project_name}/releases/latest"
    r = requests.get(releases_url)
    r.raise_for_status()
    releases = r.json()
    # TODO: don't assume order
    last_release = releases["tag_name"]
    return last_release


# gets last tag of Morphida
def get_last_morphida_tag() -> str:
    last_morphida_tag = get_last_github_tag('1013503897/Morphida')
    print(f"Last Morphida tag: {last_morphida_tag}")
    return last_morphida_tag


# gets last tag of whole project
def get_last_project_tag() -> str:
    last_tag = get_last_tag([])
    print(f"Last project tag: {last_tag}")
    return last_tag


# compare tag segments: numeric < r<hex> < anything else
def tag_sort_key(tag: str):
    key = []
    for part in re.split(r"[\.-]", tag):
        if part.isdigit():
            key.append((0, int(part)))
        elif re.fullmatch(r"r[0-9a-f]+", part):
            key.append((1, int(part[1:], 16)))
        else:
            key.append((2, 0))
    return key


# properly sort tags (e.g. 1.11 > 1.9)
def sort_tags(tags: [str]) -> [str]:
    tags = tags.copy()
    tags.sort(key=tag_sort_key)
    return tags


# gets last tag from filter
def get_last_tag(filter_args: [str]) -> str:
    tags = exec_git_command(["tag", "-l"] + filter_args).splitlines()
    last_tag = "" if len(tags) < 1 else sort_tags(tags)[-1]
    return last_tag


# executes a git command
def exec_git_command(command_with_args: [str]) -> str:
    result = subprocess.run(["git"] + command_with_args,
                            capture_output=True).stdout
    return result.decode()


# counts how many builds were released for a given Morphida frida version
def count_build_tags(frida_tag: str) -> int:
    tags = exec_git_command(["tag", "-l", f"{frida_tag}-r*"]).splitlines()
    return len(tags)


# gets next tag for a force release: 17.25.2-r11b9cbe3-2, ...-3, ...
def get_next_force_tag(morphida_tag: str) -> str:
    i = 2
    while True:
        new_tag = f"{morphida_tag}-{i}"
        if get_last_tag([new_tag]) == '':
            break
        i += 1
    return new_tag
