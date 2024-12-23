from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Link existing NucAcids with Methods and AREA_NA_LINK data from labdb to labdbproduction using direct DB connection."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for NucAcids, Method, and AREA_NA_LINK...")

        # Get the target models
        NucAcids = apps.get_model("libprep", "NucAcids")
        Method = apps.get_model("method", "Method")
        Area = apps.get_model("areas", "Area")
        AREA_NA_LINK = apps.get_model("libprep", "AREA_NA_LINK")

        # Open a connection to the source database
        with connections[source_db].cursor() as source_cursor:
            # Execute the query to fetch data for NucAcids, Method, and AREA_NA_LINK
            source_cursor.execute("""
                SELECT na.*, m.name AS method, a.name AS area, l.input_vol, l.input_amount, l.date AS link_date
                FROM nuc_acids na
                LEFT JOIN method m ON m.id = na.method_id
                LEFT JOIN area_na_link l ON l.nucacid_id = na.nu_id
                LEFT JOIN areas a ON a.ar_id = l.area_id
            """)
            rows = source_cursor.fetchall()

            # Fetch column names
            column_names = [col[0] for col in source_cursor.description]

        with transaction.atomic(using=target_db):
            for row in rows:
                nucacid_data = dict(zip(column_names, row))

                # Fetch the existing NucAcid object
                nucacid = NucAcids.objects.using(target_db).filter(name=nucacid_data["name"]).first()
                if not nucacid:
                    self.stdout.write(f"NucAcid {nucacid_data['name']} not found in target database, skipping.")
                    continue

                # Get or create the Method object
                method = None
                if nucacid_data["method"]:
                    method, created = Method.objects.using(target_db).get_or_create(
                        name=nucacid_data["method"]
                    )
                    if created:
                        self.stdout.write(f"Created Method {method.name}.")

                # Update the method for the NucAcid
                if method and nucacid.method != method:
                    nucacid.method = method
                    nucacid.save(using=target_db)
                    self.stdout.write(f"Linked Method {method.name} to NucAcid {nucacid.name}.")

                # Get the related Area object
                area = None
                if nucacid_data["area"]:
                    area = Area.objects.using(target_db).filter(name=nucacid_data["area"]).first()
                    if not area:
                        self.stdout.write(f"Area {nucacid_data['area']} not found, skipping AREA_NA_LINK for NucAcid {nucacid_data['name']}.")
                        continue

                # Create the AREA_NA_LINK object
                if area:
                    if not AREA_NA_LINK.objects.using(target_db).filter(nucacid=nucacid, area=area).exists():
                        AREA_NA_LINK.objects.using(target_db).create(
                            nucacid=nucacid,
                            area=area,
                            input_vol=nucacid_data.get("input_vol"),
                            input_amount=nucacid_data.get("input_amount"),
                            date=nucacid_data.get("link_date"),
                        )
                        self.stdout.write(f"Created AREA_NA_LINK for NucAcid {nucacid.name} and Area {area.name}.")
                    else:
                        self.stdout.write(f"AREA_NA_LINK for NucAcid {nucacid.name} and Area {area.name} already exists, skipping.")

        self.stdout.write("Data copy for NucAcids, Method, and AREA_NA_LINK completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



