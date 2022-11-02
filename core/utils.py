def custom_update(model,pk,parameters):
    try:
        obj = model.objects.get(pk=pk)
        print(obj)
        for key in parameters:
            print("%s:%s" % (key,parameters[key]))
            setattr(obj, key, parameters[key])

        obj.save()
        return obj
    # except model_class.DoesNotExist:
    except Exception as e:
        print("%s in %s" % (str(e),__file__))
        return None
