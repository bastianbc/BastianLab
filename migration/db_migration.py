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
        SampleLib = apps.get_model("sample_lib", "SampleLib")
        NA_SL_LINK = apps.get_model("sample_lib", "NA_SL_LINK")
        Barcode = apps.get_model("barcodeset", "Barcode")
        Method = apps.get_model("method", "Method")
        NucAcids = apps.get_model("libprep", "NucAcids")

        # Fetch SampleLibs from the source database
        sample_libs = SampleLib.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for sample_lib in sample_libs:
                # Check if the SampleLib already exists
                existing_sample_lib = SampleLib.objects.using(target_db).filter(name=sample_lib.name).first()
                if existing_sample_lib:
                    self.stdout.write(f"SampleLib {sample_lib.name} already exists, skipping.")
                    continue

                # Get the related Barcode and Method
                barcode = None
                if sample_lib.barcode:
                    barcode = Barcode.objects.using(target_db).filter(name=sample_lib.barcode.name).first()
                    if not barcode:
                        self.stdout.write(f"Barcode {sample_lib.barcode.name} not found, skipping SampleLib {sample_lib.name}.")
                        continue

                method = None
                if sample_lib.method:
                    method = Method.objects.using(target_db).filter(name=sample_lib.method.name).first()
                    if not method:
                        self.stdout.write(f"Method {sample_lib.method.name} not found, skipping SampleLib {sample_lib.name}.")
                        continue

                # Create the SampleLib object in the target database
                new_sample_lib = SampleLib.objects.using(target_db).create(
                    name=sample_lib.name,
                    barcode=barcode,
                    date=sample_lib.date,
                    method=method,
                    qubit=sample_lib.qubit,
                    shear_volume=sample_lib.shear_volume,
                    qpcr_conc=sample_lib.qpcr_conc,
                    pcr_cycles=sample_lib.pcr_cycles,
                    amount_in=sample_lib.amount_in,
                    amount_final=sample_lib.amount_final,
                    vol_init=sample_lib.vol_init,
                    vol_remain=sample_lib.vol_remain,
                    notes=sample_lib.notes,
                )
                self.stdout.write(f"Created SampleLib {new_sample_lib.name}.")

        # Fetch NA_SL_LINK from the source database
        na_sl_links = NA_SL_LINK.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for link in na_sl_links:
                # Check if the link already exists
                existing_link = NA_SL_LINK.objects.using(target_db).filter(
                    nucacid__name=link.nucacid.name, sample_lib__name=link.sample_lib.name
                ).first()
                if existing_link:
                    self.stdout.write(f"NA_SL_LINK for NucAcid {link.nucacid.name} and SampleLib {link.sample_lib.name} already exists, skipping.")
                    continue

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



