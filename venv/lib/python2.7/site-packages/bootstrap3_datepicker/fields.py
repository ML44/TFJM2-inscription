from django.forms import DateField

from widgets import DatePickerInput


class DatePickerField(DateField):
    widget = DatePickerInput

    def __init__(self, widget=None, input_formats=None, widget_attrs=None, widget_options=None, *args, **kwargs):
        widget = widget or self.widget

        # create widget instance with format and options applied
        if isinstance(widget, type):
            format = input_formats[0] if input_formats else None

            widget = widget(format=format, attrs=widget_attrs, options=widget_options)

        super(DatePickerField, self).__init__(widget=widget, input_formats=input_formats, *args, **kwargs)
