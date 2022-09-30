import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent



STYLE_CHOICES = [(x,x.capitalize()) for x in os.listdir(os.path.join(
                BASE_DIR, 'crossref/templates/crossref/styles'))]

