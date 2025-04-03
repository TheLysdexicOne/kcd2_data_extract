# Notes

## VS Code Markdown

[https://code.visualstudio.com/docs/languages/markdown](https://code.visualstudio.com/docs/languages/markdown)

## Activate .venv

```powershell
.\.venv\Scripts\activate
```

## Working with .env file

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
workspace_dir = os.getenv("WORKSPACE_DIR")
kcd2_dir = os.getenv("KCD2_DIR")
```

## Using pip for requirements.txt

```powershell
pip freeze > requirements.txt
```

## Filter Notes

### Shields

Can filter with "Shield" in the clothing category, don't forget to filter out \_broken

### Weapons

- Clothing="Scabbard.\_" can be safely removed
- Model="manmade/common/decorations/flags/flag_table_pile_a.cgf" for some reason is in weapons when it is a decoration
- Don't forget torches
- Missile Weapons, look out for Name=".\*\_empty" or special/primitive_cylinder_nodraw

```text
Also, you can do look into this if needed
Model="manmade/weapons/daggers/
Model="manmade/weapons/shields/
Model="manmade/weapons/long_weapons/
Model="manmade/weapons/maces/
Model="manmade/weapons/axes/
Model="manmade/weapons/sabres/
Model="manmade/weapons/swords_long/
Model="manmade/weapons/war_hammers/
Model="manmade/weapons/swords_short/
Model="manmade/weapons/bows/
Model="manmade/weapons/crossbows/
Model="manmade/weapons/firearms/
```
