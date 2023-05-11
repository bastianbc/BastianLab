from django.shortcuts import render

def variants(request):
    return render(request,"variants.html",locals())

def variant_calls(request):
    return render(request,"variants.html",locals())

def g_variants(request):
    return render(request,"variants.html",locals())

def c_variants(request):
    return render(request,"variants.html",locals())

def p_variants(request):
    return render(request,"variants.html",locals())
