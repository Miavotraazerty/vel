from django.db import models
from django.contrib.auth.models import User  # Utilisation du système d'authentification de Django
from django.core.files.base import ContentFile
from PIL import Image
import io

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom
    
class Taille(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    taille = models.ForeignKey('Taille', on_delete=models.CASCADE)
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE)
    image = models.BinaryField(blank=True, null=True)  # Stockage en BLOB
    date_ajout = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if hasattr(self, 'image') and self.image:  # Vérifier si une image a été fournie
            img = Image.open(self.image)

            # Redimensionner l'image si trop grande
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))

            # Convertir en binaire
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=70, optimize=True)
            self.image_blob = img_io.getvalue()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom




class Commande(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produits = models.ManyToManyField(Produit, through='DetailCommande')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('expédiée', 'Expédiée'),
            ('livrée', 'Livrée'),
        ],
        default='en_attente'
    )

    def __str__(self):
        return f"Commande {self.id} - {self.utilisateur.username}"

class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.produit.nom}"
    

class Favori(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('utilisateur', 'produit')  # Un produit ne peut être ajouté qu'une seule fois

    def __str__(self):
        return f"{self.utilisateur.username} - {self.produit.nom}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
