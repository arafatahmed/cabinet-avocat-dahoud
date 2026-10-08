# Cabinet Dahoud — site et espace client

Le site vitrine trilingue existant est servi à `/`. Le portail Django, à `/espace-client/`, permet aux clients authentifiés de consulter leurs dossiers, suivre les étapes communiquées par le cabinet, échanger des messages, déposer et télécharger des documents privés et demander un rendez-vous.

L'espace de gestion éditoriale, à `/gestion/`, est distinct de Django Admin. Les membres du cabinet autorisés peuvent y mettre à jour les textes français/arabe/anglais, les coordonnées, les domaines d'expertise, les photographies, l'équipe, les publications et les rendez-vous. Les dossiers et les comptes clients restent gérés à `/admin/`.

Les comptes clients sont créés par le cabinet; il n'y a pas d'inscription publique. Chaque dossier est associé à un profil client; les vues vérifient cette association avant d'afficher un dossier ou de servir un fichier. Les fichiers déposés sont stockés dans `private_uploads/`, hors du répertoire statique, et ne sont jamais servis directement par l'URL média.

## Installation (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Renseignez `SECRET_KEY`, `DB_NAME`, `DB_USER` et `DB_PASSWORD` dans l'environnement de l'application, puis créez la base MySQL `cabinet_dahoud` en `utf8mb4`. Sous PowerShell, les variables peuvent être définies pour la session courante, par exemple :

```powershell
$env:SECRET_KEY = "une-cle-aleatoire-longue-et-secrete"
$env:DB_NAME = "cabinet_dahoud"
$env:DB_USER = "cabinet_user"
$env:DB_PASSWORD = "votre-mot-de-passe-mysql"
```

Le fichier `.env` copié depuis `.env.example` est chargé au démarrage par `python-dotenv`. Remplacez-y les valeurs d'exemple avant de démarrer le site.

Pour une vérification locale sans serveur MySQL, sélectionnez SQLite :

```powershell
$env:DB_ENGINE = "sqlite"
```

Puis initialisez l'application et créez le premier compte de l'équipe. Il sera habilité à ouvrir les deux espaces de gestion :

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visitez `http://127.0.0.1:8000/` pour le site public, `http://127.0.0.1:8000/espace-client/` pour la connexion client, `http://127.0.0.1:8000/gestion/` pour la gestion éditoriale du site et `http://127.0.0.1:8000/admin/` pour la gestion des comptes/dossiers.

## Création d'un accès client

Dans Django Admin, créez d'abord un utilisateur actif avec une adresse e-mail renseignée, puis créez son profil client lié à cet utilisateur. Ajoutez ensuite ses dossiers depuis l'administration. Un client connecté ne voit que les dossiers associés à son profil. Les événements, messages et documents peuvent être gérés depuis la fiche de dossier.

Les réinitialisations de mot de passe utilisent SMTP si `EMAIL_HOST` est renseigné. Avant la mise en production, configurez un vrai serveur SMTP, une `SECRET_KEY` aléatoire, les hôtes autorisés, HTTPS et `DEBUG=False`. Gardez `private_uploads/` hors de toute configuration de fichiers statiques/publics et sauvegardez les données conformément aux obligations de confidentialité du cabinet.

Pour lancer le site derrière Gunicorn, installez les dépendances de `requirements.txt` et exécutez `python manage.py collectstatic --noinput` avant de démarrer Gunicorn. WhiteNoise sert les fichiers statiques collectés ; les documents des clients restent privés et ne sont pas servis par WhiteNoise. Configurez le serveur applicatif en HTTPS et définissez `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` et `SECRET_KEY` pour l’adresse utilisée.

## Vérifications

```powershell
$env:DB_ENGINE = "sqlite"
python manage.py check
python manage.py test portal
```

## Images

Les photos d'architecture et de bibliothèque actuellement publiées sont des fichiers statiques locaux. Elles proviennent d'Unsplash : `photo-1584551246679-0daf3d275d0f`, `photo-1519817650390-64a93db51149` et `photo-1505664194779-8beaceb93744`. Les personnes ne font pas partie des photos publiées par défaut. Dans la gestion de la galerie, privilégiez des visuels d'architecture, de motifs géométriques, de livres ou des locaux, sans personnes.
