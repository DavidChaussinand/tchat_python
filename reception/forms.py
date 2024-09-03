from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class DemandeForm(forms.Form):
    nom = forms.CharField(label='Nom', max_length=100)
    prenom = forms.CharField(label='Prénom', max_length=100)
    motif = forms.CharField(label='Motif', max_length=200)
    email = forms.EmailField(label='Votre email', max_length=100)
    contenu = forms.CharField(label='Contenu de la demande', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DemandeForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['nom'].widget.attrs['readonly'] = True
            self.fields['prenom'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True

class DevisForm(forms.Form):
    nom = forms.CharField(label='Nom', max_length=100)
    email = forms.EmailField(label='Adresse Email')
    contenu = forms.CharField(label='Contenu du devis', widget=forms.Textarea)


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super(InscriptionForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    

    
class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label='Nom d\'utilisateur')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)