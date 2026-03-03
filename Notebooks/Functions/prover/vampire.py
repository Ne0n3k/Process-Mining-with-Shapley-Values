"""
Vampire prover integration.
"""

import subprocess
import shutil
import os
from pathlib import Path
try:
    from Functions.utils.imports import *
    from Functions.utils.constants import VAMPIRE_TIME_LIMIT_S, VAMPIRE_EXTRA_ARGS
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.utils.imports import *
    from Functions.utils.constants import VAMPIRE_TIME_LIMIT_S, VAMPIRE_EXTRA_ARGS


def _find_vampire() -> str:
    """Find vampire binary path."""
    p = shutil.which("vampire")
    if p:
        return p

    candidates = [
        "~/.local/bin/vampire",
        "~/vampire/bin/vampire",
        "~/vampire/bin/vampire_rel",
        "~/vampire",
    ]
    for c in candidates:
        cp = Path(os.path.expanduser(c))
        if cp.exists() and os.access(cp, os.X_OK):
            return str(cp)

    raise FileNotFoundError("No 'vampire'. Try better.")


def run_vampire(tptp_file_path: str, verbose: bool = False):
    """
    Run vampire prover on a TPTP file.
    
    Args:
        tptp_file_path: Path to TPTP file
        verbose: Whether to print output
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    tptp = Path(tptp_file_path).expanduser()
    if not tptp.exists():
        if verbose:
            print(f"Plik TPTP nie istnieje: {tptp.resolve()}")
        return False, ""

    try:
        vampire_bin = _find_vampire()
        env = os.environ.copy()
        vdir = str(Path(vampire_bin).parent)
        env["PATH"] = vdir + os.pathsep + env.get("PATH", "")

        result = subprocess.run(
            [vampire_bin, "--input_syntax", "tptp", str(tptp)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        if verbose:
            print("Vampire Result:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)

        return True, result.stdout

    except subprocess.CalledProcessError as e:
        if verbose:
            print("Error during vampire run:")
            print(f"Exit code: {e.returncode}")
            print(f"Out:\n{e.stdout}")
            print(f"Errors:\n{e.stderr}")
        return False, e.stdout if e.stdout else ""

    except FileNotFoundError as e:
        if verbose:
            print(f"No file: {e}")
        return False, ""


def parse_vampire_status(raw_output: str) -> str:
    """Parse SZS status from vampire output."""
    import re
    m = re.search(r"SZS status\s+([A-Za-z]+)", raw_output)
    return m.group(1) if m else "Unknown"

