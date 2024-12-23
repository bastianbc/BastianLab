from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy SampleLib and NA_SL_LINK data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for SampleLib and NA_SL_LINK...")

        # Get the models
        SampleLib = apps.get_model("samplelib", "SampleLib")
        NA_SL_LINK = apps.get_model("samplelib", "NA_SL_LINK")
        Barcode = apps.get_model("barcodeset", "Barcode")
        Method = apps.get_model("method", "Method")
        NucAcids = apps.get_model("libprep", "NucAcids")

        # Fetch NA_SL_LINK from the source database
        na_sl_links = NA_SL_LINK.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for link in na_sl_links:
                # Get the related NucAcid and SampleLib in the target database
                nucacid = NucAcids.objects.using(target_db).filter(name=link.nucacid.name).first()
                if not nucacid:
                    self.stdout.write(f"NucAcid {link.nucacid.name} not found, skipping NA_SL_LINK.")
                    continue

                sample_lib = SampleLib.objects.using(target_db).filter(name=link.sample_lib.name).first()
                if not sample_lib:
                    self.stdout.write(f"SampleLib {link.sample_lib.name} not found, skipping NA_SL_LINK.")
                    continue

                # Create the NA_SL_LINK object in the target database
                NA_SL_LINK.objects.using(target_db).create(
                    nucacid=nucacid,
                    sample_lib=sample_lib,
                    input_vol=link.input_vol,
                    input_amount=link.input_amount,
                    date=link.date,
                )
                self.stdout.write(f"Created NA_SL_LINK for NucAcid {nucacid.name} and SampleLib {sample_lib.name}.")

        self.stdout.write("Data copy for SampleLib and NA_SL_LINK completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



