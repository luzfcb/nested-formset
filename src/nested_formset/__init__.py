from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
    ModelForm)


class BaseNestedFormset(BaseInlineFormSet):

    def add_fields(self, form, index):

        # allow the super class to create the fields as usual
        super(BaseNestedFormset, self).add_fields(form, index)

        form.nested = self.nested_formset_class(
            instance=form.instance,
            data=form.data if self.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                self.nested_formset_class.get_default_prefix(),
            ),
        )

    def is_valid(self):

        result = super(BaseNestedFormset, self).is_valid()

        if self.is_bound:
            # look at any nested formsets, as well
            for form in self.forms:
                if not self._should_delete_form(form):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseNestedFormset, self).save(commit=commit)

        for form in self.forms:
            if not self._should_delete_form(form):
                form.nested.save(commit=commit)

        return result


def nested_formset_factory(parent_model, child_model, grandchild_model,
                           child_form=ModelForm,
                           child_formset=BaseNestedFormset, child_fk_name=None,
                           child_fields=None, child_exclude=None,
                           child_extra=3, child_can_order=False, child_can_delete=True, child_max_num=None,
                           child_formfield_callback=None,
                           grandchild_form=ModelForm,
                           grandchild_formset=BaseNestedFormset, grandchild_fk_name=None,
                           grandchild_fields=None, grandchild_exclude=None,
                           grandchild_extra=3, grandchild_can_order=False, grandchild_can_delete=True, grandchild_max_num=None,
                           grandchild_formfield_callback=None):

    parent_child = inlineformset_factory(
        parent_model,
        child_model,
        form=child_form,
        formset=child_formset,
        fk_name=child_fk_name,
        fields=child_fields,
        exclude=child_exclude,
        extra=child_extra,
        can_order=child_can_order,
        can_delete=child_can_delete,
        max_num=child_max_num,
        formfield_callback=child_formfield_callback,
    )

    parent_child.nested_formset_class = inlineformset_factory(
        child_model,
        grandchild_model,
        form=grandchild_form,
        #formset=grandchild_formset,
        fk_name=grandchild_fk_name,
        fields=grandchild_fields,
        exclude=grandchild_exclude,
        extra=grandchild_extra,
        can_order=grandchild_can_order,
        can_delete=grandchild_can_delete,
        max_num=grandchild_max_num,
        formfield_callback=grandchild_formfield_callback,
    )

    return parent_child
