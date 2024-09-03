from django.shortcuts import render

from .forms import DemandeForm , InscriptionForm
# Create your views here.


def home(request):
    return render(request, 'home.html')

from django.shortcuts import render , redirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required

from .forms import DemandeForm , DevisForm ,ConnexionForm


def demande_view(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST, user=request.user)
        if form.is_valid():
            # Traitez les données du formulaire
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            motif = form.cleaned_data['motif']
            contenu = form.cleaned_data['contenu']
            email = form.cleaned_data['email']

            # Envoyer l'email
            sujet = f"Nouvelle demande de {nom} {prenom}"
            message = f"Motif: {motif}\n\nContenu:\n{contenu}\n\nEmail de l'utilisateur: {email}"
            from_email = 'lebib07@live.fr'  # Remplacez par votre email d'envoi
            recipient_list = ['lebib07@live.fr']  # Adresse du destinataire

            send_mail(sujet, message, from_email, recipient_list)

            # Afficher une page de succès ou rediriger
            return render(request, 'form_success.html', {'form': form})
    else:
        if request.user.is_authenticated:
            initial_data = {
                'nom': request.user.first_name,
                'prenom': request.user.last_name,
                'email': request.user.email,
            }
            form = DemandeForm(initial=initial_data, user=request.user)
        else:
            form = DemandeForm()

    return render(request, 'demande_form.html', {'form': form})

def devis_view(request):
    if request.method == 'POST':
        form = DevisForm(request.POST)
        if form.is_valid():
            # Traitez les données du formulaire
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            contenu = form.cleaned_data['contenu']

            # Envoyer l'email
            sujet = f"Nouvelle demande de devis de {nom}"
            message = f"Nom: {nom}\nEmail: {email}\n\nContenu du devis:\n{contenu}"
            from_email = 'lebib07@live.fr'  # Remplacez par votre email d'envoi
            recipient_list = ['lebib07@live.fr']  # Adresse du destinataire

            send_mail(sujet, message, from_email, recipient_list)

            # Afficher une page de succès ou rediriger
            return render(request, 'devis_success.html', {'form': form})
    else:
        form = DevisForm()

    return render(request, 'devis_form.html', {'form': form})


def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()  # Cette ligne suffit à enregistrer l'utilisateur, car le mot de passe est déjà haché dans le formulaire
            username = user.username
            return render(request, 'inscription_success.html', {'username': username})
    else:
        form = InscriptionForm()

    return render(request, 'inscription_form.html', {'form': form})


def connexion_view(request):
    form = ConnexionForm(request, data=request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Rediriger vers la page d'accueil après connexion réussie
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")  # Ajout d'une erreur non liée à un champ spécifique

    # Ici, la vue renvoie toujours le formulaire, même s'il n'est pas valide ou lors de la première requête GET.
    return render(request, 'connexion.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')