# Generated by Django 5.1.7 on 2025-04-01 16:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Taille',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_commande', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('expédiée', 'Expédiée'), ('livrée', 'Livrée')], default='en_attente', max_length=20)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='produits/')),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boutique_app.categorie')),
                ('taille', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boutique_app.taille')),
            ],
        ),
        migrations.CreateModel(
            name='DetailCommande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.PositiveIntegerField(default=1)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boutique_app.commande')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boutique_app.produit')),
            ],
        ),
        migrations.AddField(
            model_name='commande',
            name='produits',
            field=models.ManyToManyField(through='boutique_app.DetailCommande', to='boutique_app.produit'),
        ),
    ]
