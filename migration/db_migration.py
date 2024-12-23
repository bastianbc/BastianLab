from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy NucAcids data from labdb to labdbproduction using direct DB connection and a custom query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for NucAcids...")

        try:
            # Get the target NucAcids model
            NucAcids = apps.get_model("libprep", "NucAcids")
            Method = apps.get_model("method", "Method")

            # Open a connection to the source database
            with connections[source_db].cursor() as source_cursor:
                # Execute the query to fetch data for NucAcids
                source_cursor.execute("""
                    SELECT na.*, m.name AS method
                    FROM nuc_acids na
                    LEFT JOIN method m ON m.id = na.method_id
                """)
                rows = source_cursor.fetchall()

                # Fetch column names
                column_names = [col[0] for col in source_cursor.description]

            with transaction.atomic(using=target_db):
                for row in rows:
                    nucacid_data = dict(zip(column_names, row))

                    # Check if the NucAcid already exists
                    if NucAcids.objects.using(target_db).filter(name=nucacid_data["name"]).exists():
                        self.stdout.write(f"NucAcid {nucacid_data['name']} already exists, skipping.")
                        continue

                    # Create the NucAcid object
                    NucAcids.objects.using(target_db).create(
                        name=nucacid_data["name"],
                        date=nucacid_data.get("date"),
                        na_type=nucacid_data.get("na_type"),
                        conc=nucacid_data.get("conc", 0),
                        vol_init=nucacid_data.get("vol_init", 0),
                        vol_remain=nucacid_data.get("vol_remain", 0),
                        notes=nucacid_data.get("notes"),
                    )
                    self.stdout.write(f"Created NucAcid {nucacid_data['name']}.")

            self.stdout.write(f"Successfully copied {len(rows)} NucAcids from {source_db} to {target_db}.")

        except Exception as e:
            self.stdout.write(f"Error copying NucAcids data: {e}")

        self.stdout.write("Data copy for NucAcids completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



