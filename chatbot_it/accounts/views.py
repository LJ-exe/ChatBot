"""Vues pour l'authentification et la gestion des utilisateurs."""
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import SignUpForm, UserUpdateForm


def signup_view(request):
    """Inscription d'un nouvel utilisateur."""
    if request.user.is_authenticated:
        return redirect('chat:dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.full_name} ! Votre compte a été créé.")
            return redirect('chat:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Connexion utilisateur."""
    if request.user.is_authenticated:
        return redirect('chat:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bon retour, {user.full_name} !")
                # Rediriger les admins vers le panneau d'administration
                if user.is_admin_role:
                    return redirect('chat:admin_dashboard')
                return redirect('chat:dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    # Ajout des classes Bootstrap aux champs
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Déconnexion."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Affichage et modification du profil."""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
