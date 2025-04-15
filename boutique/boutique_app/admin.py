from django.contrib import admin
from .models import Categorie, Produit, Commande, DetailCommande, Taille

admin.site.register(Categorie)
admin.site.register(Taille)
admin.site.register(Produit)
admin.site.register(Commande)
admin.site.register(DetailCommande)
