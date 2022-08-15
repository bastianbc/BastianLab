from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms.models import inlineformset_factory
from lab.models import Patients, Blocks, Areas
from django.urls import reverse_lazy, reverse
BlockFormset = inlineformset_factory(
    Patients, Blocks, fields=('block_id', 'body_site')
)

class BlockCreate(CreateView):
    model = Patients
    fields = ["pat_id", 'sex', 'race', 'source', 'project']

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["blocks"] = BlockFormset(self.request.POST)
        else:
            data["blocks"] = BlockFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        blocks = context["blocks"]
        self.object = form.save()
        if blocks.is_valid():
            blocks.instance = self.object
            blocks.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("patients-list")