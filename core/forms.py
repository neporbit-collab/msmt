from django import forms


class InquiryForm(forms.Form):
    name = forms.CharField(max_length=120, label="Name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=40, required=False, label="Phone (optional)")
    subject = forms.CharField(max_length=160, label="Subject")
    message = forms.CharField(widget=forms.Textarea, label="Message")
    company = forms.CharField(required=False, widget=forms.HiddenInput)
