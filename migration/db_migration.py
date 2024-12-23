from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Area data from labdb to labdbproduction using direct DB connection and a custom query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for Areas...")

        try:
            # Get the target Area model
            Area = apps.get_model("areas", "Area")
            Block = apps.get_model("blocks", "Block")
            AreaType = apps.get_model("areatype", "AreaType")

            # Open a connection to the source database
            with connections[source_db].cursor() as source_cursor:
                # Execute the provided query
                source_cursor.execute("""
                    SELECT a.*, b.name AS block, at.name AS area_type
                    FROM areas a
                    LEFT JOIN blocks b ON b.bl_id = a.block
                    LEFT JOIN area_type at ON at.id = a.area_type
                """)
                rows = source_cursor.fetchall()

                # Fetch column names
                column_names = [col[0] for col in source_cursor.description]

            with transaction.atomic(using=target_db):
                for row in rows:
                    area_data = dict(zip(column_names, row))

                    # Get the related Block object
                    block = None
                    if area_data["block"]:
                        block = Block.objects.using(target_db).filter(name=area_data["block"]).first()
                        if not block:
                            self.stdout.write(f"Block {area_data['block']} not found, skipping Area {area_data['name']}.")
                            continue

                    # Get the related AreaType object
                    area_type = None
                    if area_data["area_type"]:
                        area_type = AreaType.objects.using(target_db).filter(name=area_data["area_type"]).first()
                        if not area_type:
                            self.stdout.write(f"AreaType {area_data['area_type']} not found, skipping Area {area_data['name']}.")
                            continue

                    # Check if an Area with the same `name` already exists in the target database
                    if Area.objects.using(target_db).filter(name=area_data["name"]).exists():
                        self.stdout.write(f"Area {area_data['name']} already exists, skipping.")
                        continue

                    # Insert the Area into the target database
                    Area.objects.using(target_db).create(
                        name=area_data["name"],
                        block=block,
                        area_type=area_type,
                        image=area_data.get("image"),
                        notes=area_data.get("notes"),
                        collection=area_data.get("collection", "SC"),
                    )

            self.stdout.write(f"Successfully copied {len(rows)} Areas from {source_db} to {target_db}.")

        except Exception as e:
            self.stdout.write(f"Error copying Area data: {e}")

        self.stdout.write("Data copy for Areas completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



