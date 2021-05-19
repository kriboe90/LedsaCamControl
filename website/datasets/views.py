from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from .models import Dataset
from .forms import *
#from django.template import loader
#from django.http import Http404
from django.urls import reverse
from django.views import generic


# Create your views here.

def index(request):
	latest_set_list = Dataset.objects.order_by('-pk')[:15]
	context = {
		'latest_set_list' : latest_set_list, 
	}
	return render(request, 'datasets/index.html', context)

def detail(request, dataset_id):
	dataset = get_object_or_404(Dataset, pk=dataset_id)
	return render(request, 'datasets/detail.html', {'dataset': dataset})
	
def create(request):
	print("create_function")
	if request.method == 'POST':
		form = NewDatasetForm(request.POST)
		if form.is_valid():
			print("\nValid\n")
			d = Dataset(name = form.cleaned_data['ds_name'], channel_no = form.cleaned_data['ds_channel_no'], shutter_speed = form.cleaned_data['ds_shutter_speed'], no_of_photos = form.cleaned_data['ds_photo_no'])
			d.save()
			return render(request, 'datasets/detail.html', {'dataset': d})
		else: 
			print("\nNOT Valid\n")
			d = Dataset(name = "NOT VALID")
			
	else:	
		print("\nNOT POST\n")
		#not the POST method -> return default form
		ds_name = "standard_name"
		form = NewDatasetForm(initial ={'ds_name':ds_name})
		d = Dataset(name = ds_name)
	context = {
		'form':form,
		'dataset': d,
	}
	print("going to index")
	return render(request, 'datasets/form_errors.html', context)
	
def run(request, dataset_id):
	print("run calibration function on dataset no.", dataset_id)
	if request.method == 'POST':
		d = get_object_or_404(Dataset, pk=dataset_id)
		form = RunCalibrationForm(request.POST)
		if form.is_valid():
			print("\nValid\n")
			calibration_channel = form.cleaned_data['ds_channel_no']
			
			
			
			
			
			#-----------------------------------------------------------------------------------------------------
			#
			# Hier die Kalibration für Channel "calibration_channel" einfügen
			# d ist das dataset und enthält d.name, shutterspeed, no_of_photos
			#
			#-----------------------------------------------------------------------------------------------------
			print(d.name, d.channel_no, d.shutter_speed, d.no_of_photos)
			
			
			
			
			
			
			
			
			return render(request, 'datasets/detail.html', {'dataset': d})
		else: 
			print("\nNOT Valid\n")
			d = Dataset(name = "NOT VALID")
			
	else:	
		print("\nNOT POST\n")
		#not the POST method -> return default form
		ds_name = "standard_name"
		form = NewDatasetForm(initial ={'ds_name':ds_name})
		d = Dataset(name = ds_name)
	context = {
		'form':form,
		'dataset': d,
	}
	print("going to index")
	return render(request, 'datasets/form_errors.html', context)
	






