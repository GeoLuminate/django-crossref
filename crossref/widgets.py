# from django_select2.forms import Select2Mixin
from django import forms
from django.forms import widgets

class CrossRefWorkWidget():
    pass

class CrossRefFunderWidget():
    pass

class PagesWidget(widgets.MultiWidget):
	def __init__(self, *args, **kwargs):
		# attrs = {'style': 'width: 40px; text-align: center;'}
		super().__init__([widgets.NumberInput, widgets.NumberInput], *args, **kwargs)


	def format_output(self, rendered_widgets):
		to = ' <span style="vertical-align: middle;"> -- </span> '
		return rendered_widgets[0] + to + rendered_widgets[1]


	def decompress(self, value):
		if value:
			values = value.split('-')

			if len(values) > 1:
				return values
			if len(values) > 0:
				return [values[0], values[0]]
		return [None, None]