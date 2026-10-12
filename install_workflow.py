"""Run locally only after uploading all other files; this creates the required GitHub path."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
target=root/'.github/workflows/monthly-dart.yml'
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(root/'automation/monthly-dart.yml',target)
print('Created .github/workflows/monthly-dart.yml. Commit and push this file.')
