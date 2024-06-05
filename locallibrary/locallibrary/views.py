from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse
from .forms import CustomUserCreationForm

def register(request):  
    if request.method == 'POST':  
        form = CustomUserCreationForm(request.POST)  
        if form.is_valid():  
            user = form.save()
            login(request, user)
            return redirect('/')  # Ensure 'home' is the correct URL name
    else:  
        form = CustomUserCreationForm()  
    context = {  
        'form': form  
    }  
    return render(request, 'registration/register.html', context)
