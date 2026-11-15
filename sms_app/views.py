from django.shortcuts import render


def home(request):
    """
    Renders the preliminary dashboard shell.
    In Milestone 2, this view will be augmented with the SMS composition form
    and in Milestone 4 with recent message history logs.
    """
    return render(request, 'sms_app/home.html')
