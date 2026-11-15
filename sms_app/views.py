from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SMSComposeForm
from .services.textbee import send_sms


def home(request):
    """
    Renders the SMS composition dashboard and processes SMS form submissions.
    Implements Post/Redirect/Get (PRG) pattern with Django flash messages.
    """
    if request.method == 'POST':
        form = SMSComposeForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            message_text = form.cleaned_data['message']
            result = send_sms(phone_number, message_text)
            if result.success:
                batch_info = f" (ID: {result.message_id})" if result.message_id else ""
                messages.success(
                    request,
                    f"SMS dispatched successfully to {phone_number}{batch_info}!",
                )
            else:
                messages.error(request, f"Failed to send SMS: {result.error_message}")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SMSComposeForm()

    return render(request, 'sms_app/home.html', {'form': form})

