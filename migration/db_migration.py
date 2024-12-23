from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Gene data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for Gene...")

        # Get the Gene model
        Gene = apps.get_model("gene", "Gene")

        # Fetch Gene records from the source database
        gene_records = Gene.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for gene in gene_records:
                # Create the Gene object in the target database
                Gene.objects.using(target_db).create(
                    gene_id=gene.gene_id,
                    name=gene.name,
                    full_name=gene.full_name,
                    chr=gene.chr,
                    start=gene.start,
                    end=gene.end,
                    hg=gene.hg,
                    nm_canonical=gene.nm_canonical,
                )
                self.stdout.write(f"Created Gene {gene.name}.")

        self.stdout.write("Data copy for Gene completed.")




def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



