# ocfp10_Metro_Quentin
OCfp10 - Créez une API sécurisée RESTful en utilisant Django REST

## LIRE AVEC ATTENTION ET EN ENTIER AVANT DE TENTER QUOI QUE CE SOIT:
API de gestion de projets et de suivi des problèmes, utilisant Django REST

## Prérequis, installation, déploiement:
- Pour télécharger la dernière version, cliquer ci-dessus: Code -> Download ZIP
- apres avoir téléchargé et extraire le ZIP dans un nouveau dossier
- assurer d'avoir une version à jour de 'python'
- Ouvrir un terminal de commandes et placez-vous dans le dossier du projet
- lancer l'environnement virtuel `.\env\Scripts\activate`
- lancer la commande `pip install -r requirements.txt` afin d'installer les packages nécessaire
- lancer la commande `python .\SoftDesk_Project_API\manage.py migrate` pour initialiser la base de données
- lancer la commande `python .\SoftDesk_Project_API\manage.py loaddata db.json` pour initialiser des données dans la base
- puis la commande `python .\SoftDesk_Project_API\manage.py runserver` pour lancer le serveur.


## Utilisation et documentation
Vous pouvez accéder à cette API via des logiciels tels que POSTMAN ou via des request HTTP.
Une documentation POSTMAN est disponible :"https://documenter.getpostman.com/view/27220651/2s93ebTB9p"