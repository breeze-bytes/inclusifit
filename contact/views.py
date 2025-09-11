from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from django.conf import settings

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # Send email
            subject = f"New Contact Message: {contact.subject}"
            message = f"""
            You have a new message from {contact.name} ({contact.email}):

            {contact.message}
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # receiver email
                fail_silently=False,
            )

            return redirect('contact')  # refresh page or redirect to a "thank you" page
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})
