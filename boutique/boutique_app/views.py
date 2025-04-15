from .models import *
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Produit, Commande, DetailCommande
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfilForm
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.db.models import Min, Max

def liste_produits(request):
    produits = Produit.objects.all()
    categories = Categorie.objects.all()

    prix_min = Produit.objects.aggregate(Min('prix'))['prix__min'] or 0
    prix_max = Produit.objects.aggregate(Max('prix'))['prix__max'] or 100000
    prix_max = prix_max + 1
    # Récupérer les filtres
    categorie_id = request.GET.get('categorie')
    min_prix = request.GET.get('min_prix', prix_min)
    max_prix = request.GET.get('max_prix', prix_max)
    taille = request.GET.get('taille')
    query = request.GET.get('q')

    # Filtrer par catégorie
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)

    # Filtrer par prix
    if min_prix:
        produits = produits.filter(prix__gte=min_prix)
    if max_prix:
        produits = produits.filter(prix__lte=max_prix)

    # Filtrer par taille (ex: "S", "M", "L", "XL")
    if taille:
        produits = produits.filter(description__icontains=taille)  

    if query:
        produits = produits.filter(nom__icontains=query)

    context = {
        'produits': produits,
        'categories': categories,
        'query': query,
        'prix_min': prix_min,
        'prix_max': prix_max,
        'min_prix': min_prix,
        'max_prix': max_prix,
    }
    return render(request, 'boutique_app/liste_produits.html', context)


def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    return render(request, 'boutique_app/detail_produits.html', {'produit': produit})


def acceuil(request):
    produits = cache.get('produits_accueil')
    recommandations = []
    if request.user.is_authenticated:
        recommandations = recommandations_utilisateur(request.user)

        produits = Produit.objects.all()
        return render(request, "boutique_app/acceuil.html", {"produits": produits, "recommandations": recommandations})
    elif not produits:
        produits = Produit.objects.all()[:10]
        cache.set('produits_accueil', produits, timeout=60*10)  # Cache 10 minutes

        return render(request, 'boutique_app/acceuil.html', {'produits': produits})


@login_required
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    commande, created = Commande.objects.get_or_create(utilisateur=request.user, statut='en attente')
    detail, created = DetailCommande.objects.get_or_create(commande=commande, produit=produit)

    return redirect('voir_panier')

@login_required
def voir_panier(request):
    commande = Commande.objects.filter(utilisateur=request.user, statut="en attente").first()
    details = DetailCommande.objects.filter(commande=commande) if commande else []

    return render(request, 'boutique_app/panier.html', {
        'details': details
    })

@login_required
def passer_commande(request):
    commande = Commande.objects.filter(utilisateur=request.user, statut='en attente').first()
    if commande:
        commande.statut = 'validée'
        commande.save()
    
    return redirect('confirmation_commande')


@login_required
def confirmation_commande(request):
    return render(request, 'boutique_app/confirmation.html')


@login_required
def supprimer_du_panier(request, detail_id):
    detail = get_object_or_404(DetailCommande, id=detail_id, commande__utilisateur=request.user)
    detail.delete()
    return redirect('voir_panier')

def inscription(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('liste_produits')
    else:
        form = UserCreationForm()
    return render(request, 'boutique_app/inscription.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('liste_produits')


@login_required
def espace_utilisateur(request):
    commandes = Commande.objects.filter(utilisateur=request.user).prefetch_related('detailcommande_set__produit').order_by('-date_commande')
    return render(request, 'boutique_app/espace_utilisateur.html', {'commandes': commandes})



@login_required
def modifier_profil(request):
    if request.method == "POST":
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('espace_utilisateur')
    else:
        form = ProfilForm(instance=request.user)

    return render(request, 'boutique_app/modifier_profil.html', {'form': form})

@login_required
def ajouter_favori(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    favori, created = Favori.objects.get_or_create(utilisateur=request.user, produit=produit)
    
    if created:
        return JsonResponse({'status': 'added'})
    else:
        return JsonResponse({'status': 'exists'})

@login_required
def supprimer_favori(request, produit_id):
    favori = Favori.objects.filter(utilisateur=request.user, produit_id=produit_id)
    
    if favori.exists():
        favori.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'not_found'})

@login_required
def liste_favoris(request):
    favoris = Favori.objects.filter(utilisateur=request.user).select_related('produit')
    return render(request, 'boutique_app/favoris.html', {'favoris': favoris})


def envoyer_notification_commande(user: User, message: str):
    Notification.objects.create(user=user, message=message)

def profil(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'boutique_app/profil.html', {'notifications': notifications})

def notifier_favori_stock(produit, user):
    if produit.stock == 0:
        message = f"Le produit '{produit.nom}' que vous avez mis en favori est en rupture de stock."
        Notification.objects.create(user=user, message=message)

def envoyer_notification(user, message):
    """Envoie une notification à un utilisateur"""
    Notification.objects.create(user=user, message=message)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send_notification",
            "message": message,
        },
    )

def recommandations_utilisateur(user):
    # Récupérer toutes les commandes de l'utilisateur
    commandes = Commande.objects.filter(utilisateur=user)

    # Trouver les produits achetés
    produits_achetes = set()
    for commande in commandes:
        for produit in commande.produits.all():
            produits_achetes.add(produit)

    # Trouver les catégories des produits achetés
    categories_preferees = set(produit.categorie for produit in produits_achetes)

    # Trouver d'autres produits dans ces catégories
    recommandations = Produit.objects.filter(categorie__in=categories_preferees).exclude(id__in=[p.id for p in produits_achetes])

    return recommandations

def afficher_image(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if produit.image:
        return HttpResponse(produit.image, content_type="image/jpeg")
    return HttpResponse("Image non disponible", status=404)

