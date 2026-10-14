## trying to standardize how sim directories are handled

from os import PathLike
from pathlib import Path
import re
from pathlib import Path

_PLACEHOLDER = re.compile(r"%(\w+)%")


def fill_template(src, dest, /, **values):
    """Copy src to dest, replacing %name% placeholders with values[name].

    Raises ValueError (without writing dest) if any placeholder has no
    value, or if any keyword argument doesn't match a placeholder.
    """
    text = Path(src).read_text()
    missing = set()
    used = set()

    def _sub(match):
        name = match.group(1)
        if name in values:
            used.add(name)
            return str(values[name])
        missing.add(name)
        return match.group(0)

    result = _PLACEHOLDER.sub(_sub, text)
    unused = set(values) - used

    problems = []
    if missing:
        problems.append(
            "no value given for: " + ", ".join(f"%{n}%" for n in sorted(missing))
        )
    if unused:
        problems.append(
            "keywords not found in file: " + ", ".join(sorted(unused))
        )
    if problems:
        raise ValueError(f"{src}: " + "; ".join(problems))

    Path(dest).write_text(result)
    

def make_sim_folder(dest:PathLike, folder_name: None|str=None) -> Path:
    if folder_name is None: # increment sim1, sim2, etc. if folder_name is None
        i = 1
        while True:
            uniqueDir = Path(dest) / f"sim{i}"
            if not uniqueDir.exists():
                break
            i += 1
    else:
        uniqueDir = Path(dest) / folder_name
    
    dest = Path(dest)
    if not dest.exists():
        dest.mkdir(parents=True)
    elif not dest.is_dir():
        raise ValueError(f"{dest} exists but is not a directory")
    else:
        print(f"Directory {dest} already exists")
    
    Path(uniqueDir).mkdir()
    Path(uniqueDir, "input").mkdir()
    Path(uniqueDir, "output").mkdir()
    
    return uniqueDir


