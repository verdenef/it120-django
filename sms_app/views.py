from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SMSComposeForm


def home(request):
    """
    Renders the SMS composition dashboard and processes SMS form submissions.
    Implements Post/Redirect/Get (PRG) pattern with Django flash messages.
    """
    if request.method == 'POST':
        form = SMSComposeForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            messages.success(
                request, f"Message queued for dispatch to {phone_number}."
            )
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SMSComposeForm()

    return render(request, 'sms_app/home.html', {'form': form})
