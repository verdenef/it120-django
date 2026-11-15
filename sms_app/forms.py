import re
from django import forms


class SMSComposeForm(forms.Form):
    """
    Form for composing and validating outbound SMS messages.
    Enforces mobile phone number regex rules and message constraints.
    """

    phone_number = forms.CharField(
        label='Recipient Phone Number',
        required=True,
        error_messages={
            'required': 'Recipient phone number is required.',
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +639171234567 or 09171234567',
            }
        ),
    )

    message = forms.CharField(
        label='Message',
        required=True,
        max_length=160,
        error_messages={
            'required': 'Message body cannot be empty.',
        },
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': '160',
                'placeholder': 'Type your message here...',
            }
        ),
    )

    def clean_phone_number(self):
        raw_phone = self.cleaned_data.get('phone_number', '')
        if not raw_phone:
            raise forms.ValidationError('Recipient phone number is required.')

        phone_stripped = raw_phone.strip()

        # Reject characters other than digits, leading '+', spaces, or hyphens
        # Ensure optional '+' is only at index 0
        if not re.match(r'^\+?[\d\s\-]+$', phone_stripped):
            raise forms.ValidationError(
                'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).'
            )

        # Sanitize by stripping spaces and hyphens
        cleaned_phone = re.sub(r'[\s\-]+', '', phone_stripped)

        # Validate format: Philippine mobile (09XXXXXXXXX) or standard E.164 (^\+?[1-9]\d{8,14}$)
        if not re.match(r'^(09\d{9}|\+?[1-9]\d{8,14})$', cleaned_phone):
            raise forms.ValidationError(
                'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).'
            )

        return cleaned_phone

    def clean_message(self):
        msg = self.cleaned_data.get('message', '')
        msg = msg.strip()

        if not msg:
            raise forms.ValidationError('Message body cannot be empty.')

        if len(msg) > 160:
            raise forms.ValidationError('Message cannot exceed 160 characters.')

        return msg
