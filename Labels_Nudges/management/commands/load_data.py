import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from Labels_Nudges.models import News_article

class Command(BaseCommand):
    help = 'Load data into the News_article model from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # uses the header row for keys
                count = 0
                for row in reader:
                    # CSV columns:
                    #   aid, title, author, image_url, published_date,
                    #   article_url, category, raw_text, text, is_manipulated

                    # 1) Parse the date
                    date_str = row['published_date'].strip()
                    published_date = parse_date(date_str) if date_str else None

                    # 2) Create or update the News_article object
                    #    (Here we do create; if you want to avoid duplicates,
                    #     use .update_or_create(...) or .get_or_create(...))
                    News_article.objects.create(
                        aid=row['aid'].strip(),
                        title=row['title'].strip(),
                        author=row['author'].strip(),
                        image_url=row['image_url'].strip(),
                        published_date=published_date,
                        article_url=row['article_url'].strip(),
                        category=row['category'].strip(),
                        raw_text=row['raw_text'],
                        text=row['text'],
                        is_manipulated=row['is_manipulated'].strip()
                    )
                    count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Successfully loaded {count} articles from {file_path}."
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f"File not found: {file_path}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"An error occurred: {e}"
            ))
