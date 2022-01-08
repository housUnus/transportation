from django.forms.models import modelformset_factory
from django.http import request
from django.shortcuts import get_object_or_404
from django.forms.formsets import BaseFormSet
#extra
import enum


#------------------------ CRUD TYPE ------------------------------
class ViewType(enum.Enum):
    create=1
    detail=2
    update=3
    delete=4
    list=5

# ----------------------------------------------------------------
def get_object_by_id(MainModel,id):
    #Used for backend
    obj = get_object_or_404(MainModel,id=id)
    return obj

def get_object_by_slug(MainModel,slug):
    #Used for frontend
    obj = get_object_or_404(MainModel,slug=slug)
    return obj

def get_object_by_user_active(request,MainModel,id):
    user_id = request.user.id
    obj = get_object_or_404(MainModel,id=id,user_id=user_id)
    return obj

# ----------------------------------------------------------------

def get_childs_forms_of_type(self,child_model,child_model_form):
    childsFormSet = modelformset_factory(child_model, form=child_model_form, extra=1)
    childs = child_model.objects.none()
    if self.view_type is ViewType.update: 
        childs = self.MainObject.get_childs_of_type(child_model)
    childsForm = childsFormSet(self.request.POST or None, queryset=childs)
    return childsForm


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

#---------------------------------------
def save_set(formset,MainObject):
    for form_child in formset:
        child = form_child.save(commit=False)
        if child.recipe is None:
            child.recipe = MainObject
        form_child.save()
    return formset