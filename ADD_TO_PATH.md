# How to Add SemanticQuark to Python Path

## ✅ Option 1: Install in Development Mode (RECOMMENDED)
```bash
cd /Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark
pip install -e .
```
**Status:** ✅ Already installed!

This makes the package importable from anywhere:
```python
from semantic_layer.api.app import create_app
from semantic_layer.query.query import Query
```

---

## Option 2: PYTHONPATH Environment Variable

### Temporary (Current Terminal Session)
```bash
export PYTHONPATH="/Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark:$PYTHONPATH"
```

### Permanent (Add to Shell Profile)
Add to `~/.zshrc` (or `~/.bashrc` for bash):
```bash
export PYTHONPATH="/Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark:$PYTHONPATH"
```

Then reload:
```bash
source ~/.zshrc
```

---

## Option 3: sys.path in Python Code

Add at the top of your Python scripts (like test scripts do):

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent  # Adjust based on file location
sys.path.insert(0, str(project_root))

# Now you can import
from semantic_layer.api.app import create_app
```

**Example from existing code:**
- `scripts/test_api_functionality.py` (line 9)
- `scripts/test_migration.py` (line 9)

---

## Option 4: Create .pth File

Create a `.pth` file in your site-packages directory:

```bash
# Find site-packages
python -c "import site; print(site.getsitepackages())"

# Create .pth file (replace with actual site-packages path)
echo "/Users/vkataria/vipin_github/community_contribution/semantic_quark/semanticquark" > /path/to/site-packages/semanticquark.pth
```

---

## Option 5: Virtual Environment Setup

If using a virtual environment, activate it first:

```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .
```

---

## Verification

Test that it works:
```python
python -c "from semantic_layer.api.app import create_app; print('✅ Import successful!')"
```

---

## Current Status

✅ **Package is installed in development mode** - You can import from anywhere!

```python
# These will all work now:
from semantic_layer.api.app import create_app
from semantic_layer.query.query import Query
from semantic_layer.models.cube import Cube
```

