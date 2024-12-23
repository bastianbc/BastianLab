from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Import Areas using a custom SQL query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data import for Areas...")

        try:
            # Get the models
            Area = apps.get_model("areas", "Area")
            Block = apps.get_model("blocks", "Block")
            AreaType = apps.get_model("areatype", "AreaType")

            # Open a connection to the source database
            with connections[source_db].cursor() as cursor:
                # Execute the custom query to fetch data for Areas
                cursor.execute("""
                    SELECT a.*, b.name AS block_name, at.name AS area_type_name
                    FROM areas a
                    LEFT JOIN blocks b ON b.id = a.block
                    LEFT JOIN areatype at ON at.id = a.area_type
                """)
                rows = cursor.fetchall()

                # Get column names
                columns = [col[0] for col in cursor.description]

            with transaction.atomic(using=target_db):
                for row in rows:
                    area_data = dict(zip(columns, row))

                    # Get or create related Block object
                    block = None
                    if area_data["block_name"]:
                        block = Block.objects.using(target_db).filter(name=area_data["block_name"]).first()
                        if not block:
                            self.stdout.write(f"Block {area_data['block_name']} not found, skipping Area {area_data['name']}.")
                            continue

                    # Get or create related AreaType object
                    area_type = None
                    if area_data["area_type_name"]:
                        area_type = AreaType.objects.using(target_db).filter(name=area_data["area_type_name"]).first()
                        if not area_type:
                            self.stdout.write(f"AreaType {area_data['area_type_name']} not found, skipping Area {area_data['name']}.")
                            continue

                    # Check if the Area already exists
                    if Area.objects.using(target_db).filter(name=area_data["name"]).exists():
                        self.stdout.write(f"Area {area_data['name']} already exists, skipping.")
                        continue

                    # Create the Area object
                    Area.objects.using(target_db).create(
                        name=area_data["name"],
                        block=block,
                        area_type=area_type,
                        image=area_data.get("image"),
                        notes=area_data.get("notes"),
                        collection=area_data.get("collection", "SC"),
                    )

            self.stdout.write("Successfully imported Areas.")

        except Exception as e:
            self.stdout.write(f"Error importing Areas: {e}")

        self.stdout.write("Data import for Areas completed.")




def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



