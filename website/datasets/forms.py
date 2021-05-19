from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class NewDatasetForm(forms.Form):
	ds_name = forms.CharField()
	ds_channel_no = forms.IntegerField()
	ds_shutter_speed = forms.FloatField()
	ds_photo_no = forms.IntegerField()

	def clean_ds_channel_no(self):
		data = self.cleaned_data['ds_channel_no']
		print("input channel no: " + str(data))
		if data > 15:
			raise ValidationError(_('Invalid channel number! - channel number must be less than 16'))
		elif data < 1:
			raise ValidationError(_('Invalid channel number! - channel number must be larger than 0'))
		return data
		
	def clean_ds_shutter_speed(self):
		data = self.cleaned_data['ds_shutter_speed']
		print("input shutter speed: " + str(data))
		if data > 1000000:
			raise ValidationError(_('Invalid shutter speed! - shutter speed must be less than 10^6'))
		elif data < 1:
			raise ValidationError(_('Invalid shutter speed! - shutter speed must be at least 1'))
		return data
		
		
	def clean_ds_photo_no(self):
		data = self.cleaned_data['ds_photo_no']
		print("input photo no: " + str(data))
		if data > 1000:
			raise ValidationError(_('Invalid number of photos! - number of photos must be at most 10^3'))
		elif data < 1:
			raise ValidationError(_('Invalid number of photos! - number of photos must be at least 1'))
		return data
		
		
	def clean_ds_name(self):
		#print("Executing Clean_name func")
		data = self.cleaned_data['ds_name']
		print("input name: " + data)
		#some tests of data
		if "invalid" in data:
			raise ValidationError(_('Invalid name! - "invalid" must not be contained'))
		return data
	
	
	
	
class RunCalibrationForm(forms.Form):
	
	ds_channel_no = forms.IntegerField()
	
	def clean_ds_channel_no(self):
		data = self.cleaned_data['ds_channel_no']
		print("cleaned input channel no: " + str(data))
		if data > 15:
			raise ValidationError(_('Invalid channel number! - channel number must be less than 16'))
		elif data < 1:
			raise ValidationError(_('Invalid channel number! - channel number must be larger than 0'))
		return data
		
		
		




