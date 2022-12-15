from django.db.models.fields import FloatField, IntegerField

def custom_update(model,pk,parameters):
    try:
        obj = model.objects.get(pk=pk)

        for key in parameters:
            if not key == "pk" and type(obj._meta.get_field(key)) == FloatField:
                parameters[key] = float(parameters[key])
            setattr(obj, key, parameters[key])

        obj.save()
        return obj
    # except model_class.DoesNotExist:
    except Exception as e:
        print("%s in %s" % (str(e),__file__))
        return None
