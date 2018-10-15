from django.apps import AppConfig


class CsamplesConfig(AppConfig):
    name = 'csamples'

    # # auto create minial required sample attr
    # def ready(self):
    #     from .models import CTypeMinimalAttr
    #     mini_string_attrs = ["storage_date", "name", "date_out", "date_in", "color", "occupied", "vposition", "hposition"]
    #     mini_integer_attr = ["ctype_id", "box_id"]
    #     not_required_attrs = ["storage_date", "date_out", "color"]
    #     for sattr in mini_string_attrs:
    #         sample_attr = CTypeMinimalAttr.objects.all().filter(attr_name__exact=sattr)
    #         if not sample_attr:
    #             if sattr in not_required_attrs:
    #                 CTypeMinimalAttr.objects.create(attr_required=False,
    #                                                 attr_name=sattr,
    #                                                 attr_label=sattr,
    #                                                 attr_value_type=0,  # string
    #                                                 attr_value_text_max_length=0,  # no limit
    #                                                 attr_value_decimal_total_digit=0,  # not needed
    #                                                 attr_value_decimal_point=0)  # not needed
    #             else:
    #                 CTypeMinimalAttr.objects.create(attr_required=True,
    #                                                 attr_name=sattr,
    #                                                 attr_label=sattr,
    #                                                 attr_value_type=0,  # string
    #                                                 attr_value_text_max_length=0,  # no limit
    #                                                 attr_value_decimal_total_digit=0,  # not needed
    #                                                 attr_value_decimal_point=0)  # not needed
    #     for iattr in mini_integer_attr:
    #         sample_attr = CTypeMinimalAttr.objects.all().filter(attr_name__exact=iattr)
    #         if not sample_attr:
    #             if iattr in not_required_attrs:
    #                 CTypeMinimalAttr.objects.create(attr_required=False,
    #                                                 attr_name=iattr,
    #                                                 attr_label=iattr,
    #                                                 attr_value_type=1,  # integer
    #                                                 attr_value_text_max_length=0,  # not needed
    #                                                 attr_value_decimal_total_digit=0,  # not needed
    #                                                 attr_value_decimal_point=0)  # not needed
    #             else:
    #                 CTypeMinimalAttr.objects.create(attr_required=True,
    #                                                 attr_name=iattr,
    #                                                 attr_label=iattr,
    #                                                 attr_value_type=1,  # integer
    #                                                 attr_value_text_max_length=0,  # not needed
    #                                                 attr_value_decimal_total_digit=0,  # not needed
    #                                                 attr_value_decimal_point=0)  # not needed

