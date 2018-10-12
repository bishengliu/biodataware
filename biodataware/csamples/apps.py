from django.apps import AppConfig


class CsamplesConfig(AppConfig):
    name = 'csamples'

    # auto create minial required sample attr
    def ready(self):
        from .models import CSampleMinimalAttr
        mini_string_attrs = ["storage_date", "name", "date_out", "date_in", "color", "occupied", "vposition", "hposition"]
        mini_integer_attr = ["csample_type_id", "box_id"]

        for sattr in mini_string_attrs:
            sample_attr = CSampleMinimalAttr.objects.all().filter(attr_name___exact=sattr)
            if not sample_attr:
                CSampleMinimalAttr.objects.create(attr_required=False,
                                                  attr_name=sattr,
                                                  attr_label=sattr,
                                                  attr_value_type=0,
                                                  attr_value_text_max_length=0,  # no limit
                                                  attr_value_decimal_total_digit=0,  # not needed
                                                  attr_value_decimal_point=0)  # no needed
        for iattr in mini_integer_attr:
            sample_attr = CSampleMinimalAttr.objects.all().filter(attr_name___exact=iattr)
            if not sample_attr:
                pass