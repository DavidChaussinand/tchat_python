from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import DemandeForm, DevisForm, ConnexionForm, InscriptionForm  # Import correct des formulaires
from django.db.models import Q 




def home(request):
    return render(request, 'home.html')

def demande_view(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
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
            form = DemandeForm(initial=initial_data)
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
            user = form.save()  # Enregistrer l'utilisateur
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

    return render(request, 'connexion.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


def chat_view(request):
    users = User.objects.all()

    # Messages du chat général (recipient null uniquement)
    general_messages = Message.objects.filter(recipient__isnull=True).order_by('timestamp')

    # Modifier les messages pour ajouter ":" après le nom d'utilisateur
    for message in general_messages:
        message.content = f"{message.user.username}: {message.content}"

    return render(request, 'home.html', {
        'users': users,
        'general_messages': general_messages,  # Passer les messages du chat général
    })



def info_view(request, username):
    users = User.objects.exclude(username=request.user.username)
    selected_user = get_object_or_404(User, username=username)
    
    # Récupérer uniquement les messages entre les deux utilisateurs pour le chat privé
    messages = Message.objects.filter(
        (Q(user=request.user) & Q(recipient=selected_user)) | 
        (Q(user=selected_user) & Q(recipient=request.user))
    ).order_by('timestamp')
    
    return render(request, 'info.html', {
        'users': users,
        'selected_user': selected_user,
        'messages': messages,  # Passer les messages du chat privé
    })
