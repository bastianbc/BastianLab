from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Barcodeset and Barcode data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Barcodeset and Barcode...")

        try:
            # Get the models
            Barcodeset = apps.get_model("barcode", "Barcodeset")
            Barcode = apps.get_model("barcode", "Barcode")

            # Fetch all Barcodeset from the source database
            source_barcodesets = Barcodeset.objects.using(source_db).all()

            # Map source Barcodeset IDs to target Barcodeset objects
            barcodeset_mapping = {}

            with transaction.atomic(using=target_db):
                # Copy Barcodeset
                for barcodeset in source_barcodesets:
                    try:
                        # Check if the Barcodeset already exists in the target database using the name
                        target_barcodeset = Barcodeset.objects.using(target_db).get(name=barcodeset.name)
                        barcodeset_mapping[barcodeset.id] = target_barcodeset
                    except Barcodeset.DoesNotExist:
                        # Create the Barcodeset in the target database
                        target_barcodeset = Barcodeset.objects.using(target_db).create(
                            name=barcodeset.name,
                            active=barcodeset.active,
                            date=barcodeset.date,
                        )
                        barcodeset_mapping[barcodeset.id] = target_barcodeset

                # Fetch all Barcode from the source database
                source_barcodes = Barcode.objects.using(source_db).all()

                # Copy Barcode
                for barcode in source_barcodes:
                    # Get the corresponding target Barcodeset
                    target_barcodeset = barcodeset_mapping.get(barcode.barcode_set_id)

                    if not target_barcodeset:
                        self.stdout.write(
                            f"Skipping Barcode '{barcode.name}' because its Barcodeset is missing."
                        )
                        continue

                    # Check if the Barcode already exists in the target database using name and Barcodeset
                    if not Barcode.objects.using(target_db).filter(
                        name=barcode.name, barcode_set=target_barcodeset
                    ).exists():
                        Barcode.objects.using(target_db).create(
                            barcode_set=target_barcodeset,
                            name=barcode.name,
                            i5=barcode.i5,
                            i7=barcode.i7,
                            date=barcode.date,
                        )

            self.stdout.write(
                f"Successfully copied {len(source_barcodesets)} Barcodesets and {len(source_barcodes)} Barcodes from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data: {e}")

        self.stdout.write("Data copy for Barcodeset and Barcode completed.")






def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



