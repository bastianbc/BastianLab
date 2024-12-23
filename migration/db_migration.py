from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy NucAcids and AREA_NA_LINK data from labdb to labdbproduction using direct DB connection and a custom query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for NucAcids and AREA_NA_LINK...")

        try:
            # Get the target models
            NucAcids = apps.get_model("libprep", "NucAcids")
            AREA_NA_LINK = apps.get_model("libprep", "AREA_NA_LINK")
            Method = apps.get_model("method", "Method")
            Area = apps.get_model("areas", "Area")

            # Open a connection to the source database
            with connections[source_db].cursor() as source_cursor:
                # Execute the provided query
                source_cursor.execute("""
                    SELECT na.*, m.name as method, a.name as area
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

                    # Get the related Method object
                    method = None
                    if nucacid_data["method"]:
                        method = Method.objects.using(target_db).filter(name=nucacid_data["method"]).first()
                        if not method:
                            self.stdout.write(f"Method {nucacid_data['method']} not found, skipping NucAcid {nucacid_data['name']}.")
                            continue

                    # Check if the NucAcid already exists
                    nucacid, created = NucAcids.objects.using(target_db).get_or_create(
                        name=nucacid_data["name"],
                        defaults={
                            "date": nucacid_data.get("date"),
                            "method": method,
                            "na_type": nucacid_data.get("na_type"),
                            "conc": nucacid_data.get("conc", 0),
                            "vol_init": nucacid_data.get("vol_init", 0),
                            "vol_remain": nucacid_data.get("vol_remain", 0),
                            "notes": nucacid_data.get("notes"),
                        }
                    )

                    if created:
                        self.stdout.write(f"Created NucAcid {nucacid_data['name']}.")
                    else:
                        self.stdout.write(f"NucAcid {nucacid_data['name']} already exists, skipping.")

                    # Get the related Area object
                    area = None
                    if nucacid_data["area"]:
                        area = Area.objects.using(target_db).filter(name=nucacid_data["area"]).first()
                        if not area:
                            self.stdout.write(f"Area {nucacid_data['area']} not found, skipping AREA_NA_LINK for NucAcid {nucacid_data['name']}.")
                            continue

                    # Check if the AREA_NA_LINK already exists
                    if area and not AREA_NA_LINK.objects.using(target_db).filter(nucacid=nucacid, area=area).exists():
                        AREA_NA_LINK.objects.using(target_db).create(
                            nucacid=nucacid,
                            area=area,
                            input_vol=nucacid_data.get("input_vol"),
                            input_amount=nucacid_data.get("input_amount"),
                            date=nucacid_data.get("date"),
                        )
                        self.stdout.write(f"Created AREA_NA_LINK for NucAcid {nucacid_data['name']} and Area {nucacid_data['area']}.")
                    elif area:
                        self.stdout.write(f"AREA_NA_LINK for NucAcid {nucacid_data['name']} and Area {nucacid_data['area']} already exists, skipping.")

            self.stdout.write(f"Successfully copied {len(rows)} NucAcids and AREA_NA_LINK records from {source_db} to {target_db}.")

        except Exception as e:
            self.stdout.write(f"Error copying NucAcids and AREA_NA_LINK data: {e}")

        self.stdout.write("Data copy for NucAcids and AREA_NA_LINK completed.")




def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



