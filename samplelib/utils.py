from libprep.models import NucAcids
from django.db.models import Min, F

def get_smallest_amount_nucleic_acid():
    return NucAcids.objects.order_by(F("qubit") * F("vol_init")).first()
