from django.db import connections
from django.apps import apps
from django.core.management.base import BaseCommand

# List of tables to copy
TABLES_TO_COPY = ["auth_group"]

class Command(BaseCommand):
    help = "Copy data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        # Loop through tables to copy
        for table_name in TABLES_TO_COPY:
            self.stdout.write(f"Copying data for table: {table_name}...")

            # Get the model
            app_label, model_name = table_name.split("_", 1)
            model = apps.get_model(app_label, model_name)

            # Fetch data from source database
            source_objects = model.objects.using(source_db).all()

            # Copy data to target database
            for obj in source_objects:
                obj.id = None  # Reset primary key for insertion
                obj.save(using=target_db)

            self.stdout.write(f"Successfully copied {source_objects.count()} records from {source_db} to {target_db}.")

        self.stdout.write("Data copy completed.")


if __name__ == "__main__":
    print("start")
    c = Command()
    c.handle()
    print("end")
