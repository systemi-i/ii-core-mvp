from pathlib import Path
from memory.polaris_memory import PolarisMemory

def load_memory():
    path = Path(r"C:\Users\fagua\OneDrive - i-i.earth\i-core\library\domains\urban_permitting\denpasar_v1")
    return PolarisMemory(path)
