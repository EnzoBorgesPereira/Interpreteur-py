# Interpreteur python
Show stack :  python Interpreteur.py --show--stack

## Améliorations :
1. Fonctions void ✅
2. Fonction return avec coupe circuit ✅
3. Gérer les elif ✅
4. Scope ✅
5. Fonctions avec return et scope des variables et gestion de la pile d’exécution ✅
6. Les tableaux (suivant degré d’aboutissement : push, pop, len, printTab, init) ✅
7. le POO (suivant degré d’aboutissement)
8. Gérer le passage des paramètres par référence et les pointeurs (suivant degré
   d’aboutissement)
9. Coder une fonction eval ou exec (à la python)
10. Optimiser l’interprétation de fonctions récursives terminales (sur la taille de la pile)
11. Gérer les imports

## Petites ameliorations :
1. Gestion des erreurs (variable non initialisée, …) ✅
2. Gérer la déclaration explicite des variables
3. Gestion du type chaine de caractères (et extension d’autant de l’instruction d’affichage)
4. Gestion des variables globales ✅
5. affectations multiples à la python : a, b = 2, 3 ✅
6. comparaison multiples à la python : 1<2<3 (déconseillé)
7. print multiples : print(x+2, « toto ») ; ✅
8. incrémentation et affectation élargie : x++, x+=1 ✅
9. possibilités de mettre des commentaires dans le code (et génération automatique d’une
docString) ✅
10. printString ✅
11. input utilisateur

Groupe :

- BORGES PEREIRA Enzo
- BACHER Téo

## Utilisation

Pour lancer l'interpreteur, il suffit de lancer le fichier `Interpreteur.py` avec python3.

```bash
py Interpreteur.py
```

Il est possible de faire afficher la pile d'exécution à chaque étape en ajoutant l'option `--show-stack`.

```bash
py Interpreteur.py --show-stack
```
