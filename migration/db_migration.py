from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth.models import User

TABLES_TO_COPY = [
    "auth_group",
]

class Command(BaseCommand):
    help = "Copy data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        for table_name in TABLES_TO_COPY:
            self.stdout.write(f"Copying data for table: {table_name}...")

            try:
                if table_name == "auth_user_permissions":
                    model = User.user_permissions.through
                elif table_name == "django_content_type":
                    app_label, model_name = "contenttypes", "ContentType"
                    model = apps.get_model(app_label, model_name)
                else:
                    app_label, model_name = table_name.split("_", 1)
                    model_name = model_name.capitalize()
                    model = apps.get_model(app_label, model_name)

                source_objects = model.objects.using(source_db).all()

                with transaction.atomic(using=target_db):
                    for obj in source_objects:
                        try:
                            # Skip duplicates
                            if table_name == "django_content_type":
                                model.objects.using(target_db).get(
                                    app_label=obj.app_label, model=obj.model
                                )
                            elif table_name == "auth_user":
                                model.objects.using(target_db).get(username=obj.username)
                            else:
                                model.objects.using(target_db).get(pk=obj.pk)
                            continue
                        except model.DoesNotExist:
                            obj.id = None  # Reset PK for insertion
                            obj.save(using=target_db)

                self.stdout.write(f"Successfully copied {source_objects.count()} records.")
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



