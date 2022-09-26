from django.shortcuts import render,redirect
from .models import User
from django.contrib.auth.decorators import login_required,permission_required
from .forms import CreateAccountForm, EditAccountForm
from django.contrib import messages
from django.conf import settings

@permission_required("account.view_user",raise_exception=True)
def accounts(request):
    return render(request,"account_list.html",locals())

@permission_required("account.add_user",raise_exception=True)
def new_account(request):
    if request.method=="POST":
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Account was created successfully")
            return redirect('/account')
        else:
            messages.error(request,"Account wasn't created!")
    else:
        form = CreateAccountForm()
    return render(request,"account.html",locals())

@permission_required("account.change_user",raise_exception=True)
def edit_account(request,id):
    instance = User.objects.get(id=id)
    if request.method=="POST":
        form = EditAccountForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Account was updated successfully")
            return redirect('/account')
        else:
            messages.error(request,"Account wasn't updated!")
    else:
        form = EditAccountForm(instance=instance)
    return render(request,"account.html",locals())

@permission_required("account.delete_user",raise_exception=True)
def delete_account(request,id):
    try:
        instance = User.objects.get(id=id)
        instance.delete()
        messages.success(request, "Account was deleted successfully")
        return redirect('/account')
    except Exception as e:
        messages.error(request, "Account wasn't deleted!")
    return redirect(coming_url)

@permission_required("account.view_user",raise_exception=True)
def filter_accounts(request):
    from .serializers import AccountSerializer
    from django.http import JsonResponse

    patients = User().query_by_args(**request.GET)
    serializer = AccountSerializer(patients['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    result['draw'] = patients['draw']
    result['recordsTotal'] = patients['total']
    result['recordsFiltered'] = patients['count']

    return JsonResponse(result)

@permission_required("account.change_user",raise_exception=True)
def reset_password(request,id):
    user = User.objects.get(id=id)
    user.reset_password()
    messages.success(request,"Account's Password was reseted ")
    return redirect("/account")
