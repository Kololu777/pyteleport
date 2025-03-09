from pathlib import Path

def mkdir(path: str, parents:bool=True):
    """
    Make a directory.
    """
    Path(path).mkdir(parents=parents, exist_ok=True)


def touch(path: str):
    """
    Touch a file.
    """
    Path(path).touch(exist_ok=True)

if __name__ == "__main__":
    mkdir("./test/m/a/b")
    touch("./test/m/a/c")
    mkdir("./test/m/d")