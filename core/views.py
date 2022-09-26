from django.shortcuts import render

def error_404(request,exception):
    status_code = 404
    message = "Page not found"
    return render(request, "error-404.html", locals())

def error_403(request,exception):
    status_code = 403
    message = "You are not authorized to access this page"
    return render(request, "error-403.html", locals())

def error_500(request):
    status_code = 500
    message = "Unexpected error"
    return render(request, "error-500.html", locals())
