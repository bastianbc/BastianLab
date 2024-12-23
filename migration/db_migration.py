from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy CapturedLib and SL_CL_LINK data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for CapturedLib and SL_CL_LINK...")

        # Get the models
        CapturedLib = apps.get_model("capturedlib", "CapturedLib")
        SL_CL_LINK = apps.get_model("capturedlib", "SL_CL_LINK")
        Bait = apps.get_model("bait", "Bait")
        Buffer = apps.get_model("buffer", "Buffer")
        SampleLib = apps.get_model("samplelib", "SampleLib")

        # Fetch CapturedLibs from the source database
        captured_libs = CapturedLib.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for captured_lib in captured_libs:
                # Check if the CapturedLib already exists
                existing_captured_lib = CapturedLib.objects.using(target_db).filter(name=captured_lib.name).first()
                if existing_captured_lib:
                    self.stdout.write(f"CapturedLib {captured_lib.name} already exists, skipping.")
                    continue

                # Get the related Bait and Buffer
                bait = None
                if captured_lib.bait:
                    bait = Bait.objects.using(target_db).filter(name=captured_lib.bait.name).first()
                    if not bait:
                        self.stdout.write(f"Bait {captured_lib.bait.name} not found, skipping CapturedLib {captured_lib.name}.")
                        continue

                buffer = None
                if captured_lib.buffer:
                    buffer = Buffer.objects.using(target_db).filter(name=captured_lib.buffer.name).first()
                    if not buffer:
                        self.stdout.write(f"Buffer {captured_lib.buffer.name} not found, skipping CapturedLib {captured_lib.name}.")
                        continue

                # Create the CapturedLib object in the target database
                CapturedLib.objects.using(target_db).create(
                    name=captured_lib.name,
                    date=captured_lib.date,
                    bait=bait,
                    frag_size=captured_lib.frag_size,
                    conc=captured_lib.conc,
                    amp_cycle=captured_lib.amp_cycle,
                    buffer=buffer,
                    nm=captured_lib.nm,
                    vol_init=captured_lib.vol_init,
                    vol_remain=captured_lib.vol_remain,
                    pdf=captured_lib.pdf,
                    notes=captured_lib.notes,
                )
                self.stdout.write(f"Created CapturedLib {captured_lib.name}.")

        # Fetch SL_CL_LINK from the source database
        sl_cl_links = SL_CL_LINK.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for link in sl_cl_links:
                # Get the related CapturedLib and SampleLib in the target database
                captured_lib = CapturedLib.objects.using(target_db).filter(name=link.captured_lib.name).first()
                if not captured_lib:
                    self.stdout.write(f"CapturedLib {link.captured_lib.name} not found, skipping SL_CL_LINK.")
                    continue

                sample_lib = SampleLib.objects.using(target_db).filter(name=link.sample_lib.name).first()
                if not sample_lib:
                    self.stdout.write(f"SampleLib {link.sample_lib.name} not found, skipping SL_CL_LINK.")
                    continue

                # Check if the SL_CL_LINK already exists
                if SL_CL_LINK.objects.using(target_db).filter(captured_lib=captured_lib, sample_lib=sample_lib).exists():
                    self.stdout.write(f"SL_CL_LINK for CapturedLib {captured_lib.name} and SampleLib {sample_lib.name} already exists, skipping.")
                    continue

                # Create the SL_CL_LINK object in the target database
                SL_CL_LINK.objects.using(target_db).create(
                    captured_lib=captured_lib,
                    sample_lib=sample_lib,
                    volume=link.volume,
                    date=link.date,
                )
                self.stdout.write(f"Created SL_CL_LINK for CapturedLib {captured_lib.name} and SampleLib {sample_lib.name}.")

        self.stdout.write("Data copy for CapturedLib and SL_CL_LINK completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



