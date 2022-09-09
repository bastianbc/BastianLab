from .models import NucAcids

def custom_update(pk,parameters):
    try:
        obj = NucAcids.objects.get(pk=pk)
        for key in parameters:
            setattr(obj, key, parameters[key])
        print(obj.__dict__)
        obj.save()
        return obj
    # except model_class.DoesNotExist:
    except Exception as e:
        return None
