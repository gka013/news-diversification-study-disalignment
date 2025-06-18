import csv,sys,os
project_dir = "C:/xampp/htdocs/NewsResearch/KnowledgeBased_NoLabel/" # This might need changing
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Labels_Nudges.settings'
import django

django.setup()
from .models import ClimateNews
data = csv.reader(open("C:/xampp/htdocs/NewsResearch/KnowledgeBased_NoLabel/twp_corpus_climate_imageOKnew2.csv"),delimiter=",")

for row in data:
	if row[0] != 'id':
            unit = ClimateNews()
            unit.id = row[0]
            unit.article_url = row[1]
            unit.title = row[2]
            unit.type = row[3]
            unit.category = row[4]
            unit.subcategory = row[5]
            unit.text = row[6]
            unit.image_url = row[7]
            unit.subtype = row[8]
            unit.save()