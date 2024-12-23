from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy NA_SL_LINK data from labdb to labdbproduction using a custom query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for NA_SL_LINK...")

        # Get the models
        SampleLib = apps.get_model("samplelib", "SampleLib")
        NucAcids = apps.get_model("libprep", "NucAcids")
        NA_SL_LINK = apps.get_model("samplelib", "NA_SL_LINK")

        # Open a connection to the source database
        with connections[source_db].cursor() as source_cursor:
            # Execute the query to fetch data for NA_SL_LINK
            source_cursor.execute("""
                SELECT nsl.*, sl.name AS sample_lib, n.name AS nuc_acid 
                FROM na_sl_link nsl
                LEFT JOIN sample_lib sl ON sl.id = nsl.sample_lib_id
                LEFT JOIN nuc_acids n ON nsl.nucacid_id = n.nu_id
            """)
            rows = source_cursor.fetchall()

            # Fetch column names
            column_names = [col[0] for col in source_cursor.description]

        with transaction.atomic(using=target_db):
            for row in rows:
                link_data = dict(zip(column_names, row))

                # Fetch the related SampleLib and NucAcids from the target database
                sample_lib = SampleLib.objects.using(target_db).filter(name=link_data["sample_lib"]).first()
                if not sample_lib:
                    self.stdout.write(f"SampleLib {link_data['sample_lib']} not found, skipping NA_SL_LINK.")
                    continue

                nucacid = NucAcids.objects.using(target_db).filter(name=link_data["nuc_acid"]).first()
                if not nucacid:
                    self.stdout.write(f"NucAcid {link_data['nuc_acid']} not found, skipping NA_SL_LINK.")
                    continue

                # Check if the NA_SL_LINK already exists
                if NA_SL_LINK.objects.using(target_db).filter(nucacid=nucacid, sample_lib=sample_lib).exists():
                    self.stdout.write(f"NA_SL_LINK for NucAcid {nucacid.name} and SampleLib {sample_lib.name} already exists, skipping.")
                    continue

                # Create the NA_SL_LINK object in the target database
                NA_SL_LINK.objects.using(target_db).create(
                    nucacid=nucacid,
                    sample_lib=sample_lib,
                    input_vol=link_data.get("input_vol"),
                    input_amount=link_data.get("input_amount"),
                    date=link_data.get("date"),
                )
                self.stdout.write(f"Created NA_SL_LINK for NucAcid {nucacid.name} and SampleLib {sample_lib.name}.")

        self.stdout.write("Data copy for NA_SL_LINK completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



