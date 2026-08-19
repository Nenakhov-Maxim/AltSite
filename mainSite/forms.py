from django import forms
from captcha.fields import CaptchaField


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
    privacy_policy_acknowledged = forms.BooleanField(label='Я ознакомлен с политикой обработки персональных данных', required=True, widget=forms.CheckboxInput(attrs={
        'id': 'feedback-privacy-policy-acknowledged-checkbox'
    }))
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'autocomplete': 'off',
        'tabindex': '-1',
    }))
    captcha = CaptchaField(
        label='Защита от спама',
        error_messages={
            'required': 'Введите код с изображения.',
            'invalid': 'Код с изображения введён неверно.',
        },
    )

    def clean_website(self):
        website = self.cleaned_data['website']
        if website:
            raise forms.ValidationError('Не удалось отправить форму.')
        return website
