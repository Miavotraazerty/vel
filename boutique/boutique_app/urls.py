from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('produits/', liste_produits, name='liste_produits'),
    path('produits/<int:produit_id>/', detail_produit, name='detail_produit'),
    path('', acceuil, name='acceuil'),
    path('panier/', voir_panier, name='voir_panier'),
    path('ajouter-au-panier/<int:produit_id>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('passer-commande/', passer_commande, name='passer_commande'),
    path('confirmation-commande/', confirmation_commande, name='confirmation_commande'),
    path('supprimer-du-panier/<int:detail_id>/', supprimer_du_panier, name='supprimer_du_panier'),
    path('inscription/', inscription, name='inscription'),
    path('connexion/', LoginView.as_view(template_name='boutique_app/connexion.html'), name='connexion'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    path('espace-utilisateur/', espace_utilisateur, name='espace_utilisateur'),
    path('modifier-profil/', modifier_profil, name='modifier_profil'),
    path('favoris/', liste_favoris, name='liste_favoris'),
    path('favori/ajouter/<int:produit_id>/', ajouter_favori, name='ajouter_favori'),
    path('favori/supprimer/<int:produit_id>/', supprimer_favori, name='supprimer_favori'),
    path('profils/', profil, name='profil'),
    path('image/<int:produit_id>/', afficher_image, name='afficher_image'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
