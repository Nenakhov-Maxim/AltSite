from django import forms

class ProjectForm(forms.Form):
    consumer_name = forms.CharField(label='Ваше имя', max_length=100, required=True, widget=forms.TextInput(attrs={
            'id': 'feedback-contact-name-input',
            'placeholder': 'Ваше имя'
        }))
    consumer_email = forms.EmailField(label='Электронная почта', max_length=100, required=True, widget=forms.TextInput(attrs={
            'id': 'feedback-contact-email-input',
            'placeholder': 'Электронная почта'
        }))
    consumer_tel = forms.CharField(label='Номер телефона', max_length=100, required=True, widget=forms.TextInput(attrs={
            'id': 'feedback-contact-phone-input',
            'placeholder': 'Номер телефона'
        }))
    consumer_message = forms.CharField(label='Ваше сообщение', widget=forms.Textarea(attrs={
            'id': 'feedback-message-textarea',
            'placeholder': 'Ваше сообщение'
        }))
    consent_personal_data = forms.BooleanField(label='Я согласен на передачу и обработку моих персональных данных', required=True, widget=forms.CheckboxInput(attrs={
            'id': 'feedback-consent-personal-data-checkbox'
        }))
    
    