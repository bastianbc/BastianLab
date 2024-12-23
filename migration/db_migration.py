from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps

# Update TABLES_TO_COPY to include the area_type table
TABLES_TO_COPY = [
    "area_type",  # area_type table from areatype app
]

class Command(BaseCommand):
    help = "Copy area_type data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        for table_name in TABLES_TO_COPY:
            self.stdout.write(f"Copying data for table: {table_name}...")

            try:
                # Handle app and model names
                app_label, model_name = "areatype", "AreaType"  # Explicitly define app and model
                model = apps.get_model(app_label, model_name)

                # Fetch all objects from the source database
                source_objects = model.objects.using(source_db).all()

                with transaction.atomic(using=target_db):
                    for obj in source_objects:
                        try:
                            # Check if the object already exists in the target database
                            model.objects.using(target_db).get(pk=obj.pk)
                            continue  # Skip if it already exists
                        except model.DoesNotExist:
                            obj.id = None  # Reset PK for insertion
                            obj.save(using=target_db)

                self.stdout.write(f"Successfully copied {source_objects.count()} records from {source_db} to {target_db}.")
            except Exception as e:
                self.stdout.write(f"Error copying data for {table_name}: {e}")

        self.stdout.write("Data copy completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



