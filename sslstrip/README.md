# Attaque SSLstrip

L'attaque SSLstrip a été présentée pour la première fois par Moxie à la Blackhat de 2009. Cette attaque consiste à remplacer dans les requêtes HTTP, toutes les références à des URL pointant vers des liens HTTPS par leurs version HTTP. Cette attaque était efficace notamment lorsque seule la page de login était sécurisée en HTTPS mais que le reste du site utilisait le protocole HTTP.

----------------------------------------------

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.

## Machine "grave"

Cette machine utilise l'environnement graphique de la distribution Linux Alpine. Le navigateur firefox est utilisé pour la démonstration.

## Machine "opeth"

Cette machine héberge un serveur HTTP(s) Nginx sur le port 80 et 443. Le certificat utilisé pour les connections HTTPS a été généré avec openssl :

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Cette machine a l'adresse IPv4 : 147.210.12.1.

## Machine "immortal"

C'est sur cette machine que se trouve le PoC de l'attaque, dans le fichier "/mnt/host/attack.sh". Cette VM est configuré pour forwarder les paquets entre opeth et grave.

------------------------------------------------------

# Démo

Pour lancer l'environnement de test, il faut lancer la commande suivante (on aura récupéré au préalable le dépôt qemunet) :

```
$ ./qemunet/qemunet.sh -x -S sslstrip
```

À partir de là, les trois machines sont lancées.

## Étape 1 : avant l'attaque

Lorsque l'attaque n'est pas encore lancée, nous pouvons voir sur la machine grave, que tout se passe normalement et que la requête POST passe bien en HTTPS (immortal est donc incapable de voir les identifiants envoyés) :

![screen1](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen1.png)

![screen2](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen2.png)

![screen3](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen3.png)

## Etape 2 : lancement de l'attaque

Nous pouvons maintenant lancer l'attaque depuis la machine immortal :

```
$ /mnt/host/attack.sh
```

![screen4](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen4.png)

## Etape 3 : pendant l'attaque

Lorsque l'attaque est lancée, on peut voir que tous les liens https:// sont remplacés par http://. La machine immortal voit donc tout le trafic en clair et a pût capturer les identifiants de la machine grave :

![screen5](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen5.png)

![screen6](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen6.png)

![screen7](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen7.png)