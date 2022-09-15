
def custom_update(model,pk,parameters):
    try:
        obj = model.objects.get(pk=pk)
        for key in parameters:
            setattr(obj, key, parameters[key])

        obj.save()
        return obj
    # except model_class.DoesNotExist:
    except Exception as e:
        return None
