from django.db.models.fields import FloatField, IntegerField, related

def custom_update(model,pk,parameters):
    # try:
    #
    # # except model_class.DoesNotExist:
    # except Exception as e:
    #     print("%s in %s" % (str(e),__file__))
    #     return None
    obj = model.objects.get(pk=pk)

    for key in parameters:
        if not key == "pk":
            if type(obj._meta.get_field(key)) == FloatField:
                parameters[key] = float(parameters[key])

            if obj._meta.get_field(key).related_model:
                parameters[key] = obj._meta.get_field(key).related_model.objects.get(pk=parameters[key])

            setattr(obj, key, parameters[key])

    obj.save()
    return obj
