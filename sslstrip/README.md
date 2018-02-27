# Attaque SSLstrip

L'attaque SSLstrip a été présentée pour la première fois par Moxie à la Blackhat de 2009. Cette attaque consiste à remplacer dans les requêtes HTTP, toutes les références à des URL pointant vers des liens HTTPS par leurs version HTTP. Cette attaque était efficace notamment lorsque seule la page de login était sécurisée en HTTPS mais que le reste du site utilisait le protocole HTTP.

----------------------------------------------

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.

Voici la topologie des machines mise en place :

```
### twolans
#
#  opeth - [s1] - immortal - [s2] - grave
#
#
#

# switches

SWITCH s1
SWITCH s2
HOST alpinex   grave    s2
HOST debian10  immortal s1 s2
HOST debian10  opeth    s1
```


Cette topologie n'est pas forcément réalise car rare sont les cas où l'attaquant est dans le réseau du client attaqué. 

Toutes les configurations initiales des machines se trouvent dans le fichier __"start.sh"__ de chaque dossier correspondant aux machines.

## Machine "grave" (147.210.13.2)

Cette machine utilise l'environnement graphique de la distribution Linux Alpine. Le navigateur firefox est utilisé pour la démonstration.

## Machine "opeth" (147.210.12.1)

Cette machine héberge un serveur HTTP(s) Nginx sur le port 80 et 443. Le certificat utilisé pour les connections HTTPS a été généré avec openssl :

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Le serveur héberge deux pages :

  - une page index.php que l'on accéde en HTTP et présentant un formulaire de login.

  - une page secure.php que l'on accéde en HTTPS depuis la page index.php.

## Machine "immortal" (147.210.12.2 - 147.210.13.1)

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

L'encadré rouge montre bien que le POST est effectué en HTTPS, sur la page secure.php.

![screen2](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen2.png)

Nous arrivons alors sur la page secure.php, en HTTPS : immortal n'a pas pût voir nos échanges sur cette page sécurisée.

![screen3](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen3.png)

## Etape 2 : lancement de l'attaque

Comme préciser précédement, pour lancer l'attaque, il faut lancer le fichier __"/mnt/host/attack.sh"__ depuis immortal. 
Voici son contenu :

```
PROXY_PORT=4242

iptables -t nat -F
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT

/mnt/host/sslstrip.py $PROXY_PORT
```
Il nous est nécessaire de rediriger tout le flux TCP sur le port d'écoute afin de traiter les requêtes.

Nous pouvons maintenant lancer l'attaque depuis la machine immortal :

![screen4](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen4.png)

## Etape 3 : pendant l'attaque

Lorsque l'attaque est lancée, on peut voir que tous les liens https:// sont remplacés par http://. La machine immortal est donc capable d'intercepter les échanges réalisés sur la page secure.php. Ici on voit dans l'encadré rouge, que le lien https:// a bien été remplacé par un lien non sécurisé http:// :

![screen5](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen5.png)

Nous constatons que nous arrivons sur la page secure.php en HTTP : notre navigation n'est pas sécurisée !

![screen6](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen6.png)

La machine immortal a été capable de capturer non seulement les identifiants du formulaire, mais également le cookie de session :

![screen7](https://repo.t0x0sh.org/images/mastercsi-ter/sslstrip/screen7.png)
