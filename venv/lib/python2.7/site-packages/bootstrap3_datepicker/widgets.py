# -*- coding: utf-8 -*-
from django.forms.util import flatatt
from django.forms.widgets import DateInput
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape


try:
    import json
except ImportError:
    from django.utils import simplejson as json
try:
    from django.utils.encoding import force_unicode as force_text
except ImportError:  # python3
    from django.utils.encoding import force_text


class DatePickerInput(DateInput):
    class Media:
        class JsFiles(object):
            def __iter__(self):
                yield 'bootstrap3_datepicker/js/bootstrap-datepicker.js'
                lang = translation.get_language()
                if lang:
                    lang = lang.lower()
                    #There is language name that length>2 *or* contains uppercase.
                    lang_map = {
                        'nl-be': 'nl-BE',
                        'pt-br': 'pt-BR',
                        'rs-latin': 'rs-latin',
                        'zh-cn': 'zh-CN',
                        'zh-tw': 'zh-TW',
                    }
                    if len(lang) > 2:
                        lang = lang_map.get(lang, 'en-us')
                    if lang not in ('en', 'en-us'):
                        yield 'bootstrap3_datepicker/js/locales/bootstrap-datepicker.%s.js' % (lang)

        js = JsFiles()
        css = {'all': ('bootstrap3_datepicker/css/datepicker3.css',), }

    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (('dd', r'%d'),
                  #('d', r'%d'), # no analogous python datetime format
                  ('DD', r'%A'),
                  ('D', r'%a'),
                  ('mm', r'%m'),
                  #('m', r'%m'), # no analogous python datetime format
                  ('MM', r'%B'),
                  ('M', r'%b'),
                  ('yyyy', r'%Y'),
                  ('yy', r'%y'))

    @classmethod
    def conv_date_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    html_template = '''
        <div%(div_attrs)s>
            <input%(input_attrs)s/>
            <span class="input-group-addon">
                <span%(icon_attrs)s></span>
            </span>
        </div>'''

    js_template = '''
        <script>
            (function(window) {
                var callback = function() {
                    $(function(){$("#%(picker_id)s").datepicker(%(options)s);});
                };
                if(window.addEventListener)
                    window.addEventListener("load", callback, false);
                else if (window.attachEvent)
                    window.attachEvent("onload", callback);
                else window.onload = callback;
            })(window);
        </script>'''

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'glyphicon glyphicon-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}

        super(DatePickerInput, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if options == False:  # datepicker will not be initalized only when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            self.options['language'] = translation.get_language()

            self.options['format'] = self.conv_date_format_py2js(self.format)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        input_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = dict([(key, conditional_escape(val)) for key, val in input_attrs.items()])  # python2.6 compatible
        if not self.picker_id:
            self.picker_id = input_attrs.get('id', '') + '_picker'
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = dict(
            [(key, conditional_escape(val)) for key, val in self.div_attrs.items()])  # python2.6 compatible
        icon_attrs = dict([(key, conditional_escape(val)) for key, val in self.icon_attrs.items()])
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if not self.options:
            js = ''
        else:
            js = self.js_template % dict(picker_id=picker_id,
                                         options=json.dumps(self.options or {}))
        return mark_safe(force_text(html + js))
