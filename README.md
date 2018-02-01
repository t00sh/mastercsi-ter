Projet de TER du master 1 CSI, proposé par Aurélien Esnard.

------------------------------------------------

### Attaque man-in-the-middle de HTTPS

Le but de ce projet est d’effectuer un état de l’art des attaques HTTPS.
En particulier, on se concentrera sur l’attaque SSLStrip dont on détaillera précisément le fonctionnement. En outre,
il est demandé de réaliser une démonstration simplifiée de cette attaque en Python, à la manière d’un tutoriel pas à
pas. Afin de mettre en place cette démo, un environnement réseau virtualisé sera mis à disposition des étudiants.

Référence :

- [https://moxie.org/software/sslstrip/](https://moxie.org/software/sslstrip/)

### Attaques implémentées

- SSLstrip (voir sslstrip/README.md)

- HTTPS interception (en cours d'implémentation)

- SSLstrip+ (en cours d'implémentation)

Afin de démontrer les attaques dans les meilleures conditions, nous utilisons l'outil [qemunet](https://gitlab.inria.fr/qemunet/core) afin de simuler un environnement vulnérable.

### Auteurs

- Amélie Risi

- Simon Duret

- Brendan Guevel
