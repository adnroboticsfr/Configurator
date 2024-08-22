# Configurator

Tester sur une version Yumios 1.1.0 

## Install :

git clone https://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@github.com/adnroboticsfr/Configurator.git


chmod +x Configurator/scripts/install.sh


./Configurator/scripts/install.sh

Le script d'installation lance automatiquement le programme dans le dossier Configurator/main.py


Pour lancer le programme en mode console, après la connexion ssh

python3 Configurator/main.py

Si l'application ne démarre pu et il y a le message suivant:

c'est que la variable d'installation est passeé "setup_mode_enabled = False" car toutes les étapes d'installation a été réalisé et désactive le lancement du programme. il faut modifier la valeur à "setup_mode_enabled = true" dans la section [main] le fichier de configuration dans le dossier Configurator/config/config.conf.

# Test de calibration

Lance des commandes standards et générique à toutes imprimantes. Grâce bouton possibilité de sélectionner le test qu'on veut :

- Test ventilo
- Test des axes
- Test de vitesse (Attention!!! pour ce teste la taille du plateau doit être 230x230 environ) 

Attention!!! Se tenir près appuyer sur le bouton pour éteindre l'imprimante au cas ou en cas de problème lors du test. Tester sur d12-230 avant tout!

