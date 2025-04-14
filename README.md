
![logo de poulpus davinkus](https://github.com/GiantLionTurtle/Poulpus_Davinkus/blob/main/Poulpus%20Davinkus.jpg)

# Poulpus_Davinkus

Poulpus Davinkus est un projet de robot delta convergent ayant la capacité de reproduire des dessins et images à l'aide d'une sélection d'étampes et de couleurs.


https://github.com/user-attachments/assets/7dc46223-dcc0-4c87-9199-7f3be7e44d6c


## Logiciel de contrôle

Un logiciel de contôle en python permet de

* Dessiner avec les étampes disponnibles
![UI avec dessin](https://github.com/user-attachments/assets/10824f6a-2dc5-4245-ba1c-f53f62e6b350)


* Analyser une image pour générer un chemin d'étampes

![UI avec image analysée](https://github.com/user-attachments/assets/7c4ce48b-6f0e-404e-b099-750486722817)


Et de générer les chemins appropriés pour le robot.

L'interface est intuitif et permet de voir le statut du robot. Il peut être lancé à partir de 

```
UI/Paint.py
```

Les dépendences de l'interface sont:

* pyqt6 (interface)
* opencv-python (analyse d'image)
* matplotlib (affichage des résultats de l'analyse d'image)
* paramiko (connexion ssh avec le robot)

## Électronique de bord

Toute l'électronique de bord est alimentée par une alimentation d'ordinateur qui fournit 12v pour les moteurs (pas à pas et ventilateurs) et 5v pour les contrôleurs (Raspberry Pi 5 et Arduino Uno).

Le Raspberry Pi 5 est alimenté par un fil usb-c modifié et alimente la carte Arduino avec un cable usb qui sert également à la communication série entre les deux contrôleurs. Le chapeau "CNC Shield V3" est placé sur la carte Arduino et alimentée à 12v pour contrôler les moteurs. Les pilotes de moteurs sur le chapeau sont du modèle DRV2285 configurés pour ne laisser passer que 1A et avoir 16 niveaux de micro-pas.

## Microcode

Le microcode de l'imprimante à étampe est une version modifiée de Klipper qui supporte notre model cinématique de delta convergent. Elle peut être trouvée comme sous-module dans kinematics/ ou à https://github.com/GiantLionTurtle/klipper_convergentDelta

Dans kinematics/ se trouve aussi le fichier konfig.cfg qui est le fichier de configuration à donner à Klipper pour que le robot fonctionne comme prévu.

La cinématique du robot a l'enveloppe de travail suivante qui peut être approximée à un cylindre de 130mm de hauteur et 170mm de rayon:

![Enveloppe de travail théorique](https://github.com/user-attachments/assets/24533acc-ba2f-4e40-961d-0771242fff89)

Klipper est lancé au démarrage en utilisant l'utilitaire crontab et écoute le port série virtuel à /tmp/printer/. L'interface utilisateurice pousse des lignes de gcode dans le port série en utilisant la commande

```
echo 'G28' >> /tmp/printer/
```

via une connexion SSH et en modifiant la commande entre simple guillemets.

## Mécanique

La forme du robot est inspirée par le robot de Jakub Kaminski: https://jakub-kaminski.com/delta-robot/

L'assemblage mécanique du robot consiste en 3 actuateurs linéaires identiques qui fonctionnent sur un principe de double bobinne enroulant un fil de pêche

![Schema d'un actuateur linéaire](https://github.com/user-attachments/assets/de4955a6-caf5-48b7-9229-1a179b3c22e8)

Les 3 actuateurs se rassemblent à la pointe de la pyramide inversée.

La boite de succion a 3 ventilateurs qui permettent un maintien de la feuille en place.

Les pièces à fabriquer sont les suivantes

* Barre en L en acier doux avec des trous de 3.2 mm troués avec les guides imprimés x3
* Tiges en aluminum 3/16" de 350mm x6
* Joints sphériques liés avec du JB-weld x12
    * Bille d'acier 1/2"
    * Vis M3x10
* Pièces imprimées

Quincaillerie
* Écrous M3 (6x tensionneurs; 12x assemblage chariots 6x fixation de la pointe; 9x fixation de cornerlink au plafond) x35
* Vis M3x40 (6x tensionneurs; 9x fixation de cornerlink au plafond) x15
* Vis M3x10 (12x joints sphériques; 6x fixation des poulies de fin de course) x18
* Vis M3x16 (6x fixation des barres en L à la pointe; 6x fixation des barres en L aux cornerlinks) x12
* Vis M3x18 (12x fixation des ventilateur à la boite de succion) x12
* Écrous M2 (6x fixation des interrupteurs de fin de course) x6
* Vis M2x10 (6x fixation des interupteurs de fin de course) x6
* Vis UNC 4-40 (12x fixation des moteurs par à pas) x12


