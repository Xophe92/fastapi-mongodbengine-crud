#CRUD with SimpleAPI & Mongosbengine

## Installation & lancement
* Installer localement mongodb
* création d'un environnement ```python3 -m virtualenv env```
* activation ```. env/bin/activate``` ou ```env\Script\activatebat``` 
* installation des dépendances ```pip install -r requirements.txt```
* lancer l'api ```uvicorn main:app --reload```

## tester la solution
C'est un CRUD.

Une documentation [swagger](http://localhost:8000/docs) est automatiquement générée.

Je recherche actuellement comment éviter les redondances entre les modèles (mongodbengine) et les types (pydantics).


