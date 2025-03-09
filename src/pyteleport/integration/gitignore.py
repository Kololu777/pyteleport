import os

def read_gitignore(path: str) -> tuple[list[str], list[str]]:
    if os.path.isdir(path):
        path = os.path.join(path, ".gitignore")  # i.e.: ("./", "./src")
    elif not os.path.isfile(path):
        raise FileNotFoundError(
            f"gitignore file not found: {path}"
        )  # i.e.: ("./src/.gitignore", "./gitignore")

    include_set = set()
    exclude_set = set()
    with open(path, "r") as f:
        for line in f:
            # Ignore comment and empty line
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue

            if line.startswith("!"):
                exclude_set.add(line[1:])
            else:
                include_set.add(line)

    return list(include_set), list(exclude_set)


if __name__ == "__main__":
    include_list, exclude_list = read_gitignore("./")
    print(include_list)
    print(exclude_list)
