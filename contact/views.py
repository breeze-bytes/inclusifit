from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages
from django.conf import settings

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # ✅ Email to YOU (site admin)
            subject = f"New Contact Message: {contact.subject}"
            message = f"""
            You have a new message from {contact.name} ({contact.email}):

            {contact.message}
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # your inbox
                fail_silently=False,
            )

            # ✅ Auto-reply to the USER
            user_subject = "We received your message – Inclusifit Shop"
            user_message = f"""
            Hi {contact.name},

            Thanks for reaching out to Inclusifit Shop! 
            We’ve received your message and will get back to you shortly.

            --- Your Message ---
            {contact.message}

            Best regards,
            Inclusifit Shop Team
            """
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email],  # recipient is the user
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent. Check your email for confirmation!")

            return redirect('contact')  # or show a success page
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})
