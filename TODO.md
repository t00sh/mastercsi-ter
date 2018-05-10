# TODO LIST

## Commentaires de Aurélien, ce qu'il reste à faire :

* la présentation de l'environnement pour sslstrip2 me semble plus détaillé que pour sslstrip... faire plutôt l'inverse ?

* page 31-32 : sslstrip2 "avant l'attaque", il faudrait plutôt montrer l'effet de HSTS et s'appuyer sur la section précédente pour le reste...

de manière plus générale :

* pour sslstrip > sslstrip2 > sslstrip2 hsts, il y aurait moyen d'être plus concis dans la description des attaques en s'appuyant explicitement sur l'attaque précédente et détaillant uniquement ce qui change... y'a quand même pas mal de répétition / redondance dans le texte entre ces trois sections... // J'ai essayé de factoriser, en créant un chapitre pour l'environnement, et en spécifiant seulement les changements dans les différentes attaques. Je ne sais pas si c'est mieux maintenant...

* pour améliorer votre rapport, rajouter une petite subsection par attaque indiquant les limitations de vos attaques... comme il s'agit de preuve de concept (volontairement minimaliste), nous avons fait des hypothèses simplificatrices, qu'il faudrait préciser...

* page 51, conclusion : je rajouterais un truc à la fin du genre : un soin particulier a été apporté pour rendre ces démos minimalistes et reproductibles grâce à un environnement basé sur des scripts bash & python dans des réseau de machines virtuelles Qemu... tout le code est disponible sur github...
