### Attaque HTTPS interception


L'attaque HTTPS interception consiste à intercepter le traffic entre un client et un serveur, en présentant un certificat différent au client. L'attaquant positionné en homme du milieu joue le rôle de proxy entre le client et le serveur.

----------------------------------------------

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.


Voici la [topologie](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/topology) des machines mise en place :

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


Cette topologie n'est pas forcément réaliste car rare sont les cas où l'attaquant est dans le réseau du client attaqué.

Toutes les configurations initiales des machines se trouvent dans le fichier __"start.sh"__ de chaque dossier correspondant aux machines.

## Machine "grave" (147.210.13.2)

Cette machine utilise l'environnement graphique de la distribution Linux Alpine. Le navigateur firefox est utilisé pour la démonstration.

Au lancement de la machine, il faut l'autorité de certification dans firefox. Se reporter au fichier [start.sh](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/grave/start.sh)

## Machine "opeth" (147.210.12.1)

Cette machine héberge un serveur HTTP(s) Nginx sur le port 80 et 443. Le certificat utilisé pour les connexions HTTPS a été généré avec les scripts [create-ca.sh](https://github.com/t00sh/mastercsi-ter/tree/master/CA/create-ca.sh) et [new-cert.sh](https://github.com/t00sh/mastercsi-ter/tree/master/CA/new-cert.sh) de la façon suivante :

```
$ cd CA
$ ./create-ca.sh
$ ./new-cert.sh
```

Le serveur héberge deux pages :

  - une page [index.php](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/opeth/www/index.php), présentant un formulaire de login.

  - une page [secure.php](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/opeth/www/secure.php) affichant l'identité de la personne.

## Machine "immortal" (147.210.12.2 - 147.210.13.1)

C'est sur cette machine que se trouve le PoC de l'attaque, dans le fichier [/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/tree/master-b64c24f/https-interception/immortal/attack.sh).

Cette VM est configuré pour forwarder les paquets entre opeth et grave.

------------------------------------------------------

# Démo

Pour lancer l'environnement de test, il faut lancer la commande suivante (on aura récupéré au préalable le dépôt qemunet) :

```
$ ./qemunet/qemunet.sh -x -S https-interception
```

À partir de là, les trois machines sont lancées.

## Étape 1 : avant l'attaque

Avant que l'attaque soit lancée, nous pouvons accéder à la page de login de manière sécurisée. La machine immortal n'est pas capable de comprendre la communication entre le client (grave) et le serveur (opeth) :

![screen1](../medias/https-interception/screen1.png?raw=true)

Ici, on voit que c'est bien le certificat du serveur qui est présenté au navigateur :

![screen2](../medias/https-interception/screen2.png?raw=true)

Nous voici sur la page secure.php, nos données ont transitées de manière chiffrées entre le client et le serveur :

![screen3](../medias/https-interception/screen3.png?raw=true)

## Etape 2 : lancement de l'attaque

Comme expliqué précédement, pour lancer l'attaque, il suffit d'exécuter le fichier __[/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/immortal/attack.sh)__ depuis immortal.
Voici son contenu :

```
PROXY_PORT=4242

iptables -t nat -F
iptables -t nat -A PREROUTING -d 147.210.12.1 -p tcp --dport 443 -j REDIRECT --to-port $PROXY_PORT
/mnt/host/https-interception.py $PROXY_PORT
```

On peut constater que les flux TCP à destination du port 443 (HTTPS) sont redirigées vers le port d'écoute du proxy qui est chargé d'analyser et traiter les requêtes.

Sur la machine immortal, nous lançons le script de l'attaque :

![screen4](../medias/https-interception/screen4.png?raw=true)

### Explication du code du proxy
Le code du proxy est dans le fichier [https-interception](https://github.com/t00sh/mastercsi-ter/blob/master/https-interception/immortal/https-interception.py)

<!--- PARLER ICI DES options de la création des sockets --->

## Etape 3 : pendant l'attaque

Lorsque l'attaque est en cours, le certificat présenté au client n'est plus celui d'opeth, mais celui du Proxy, signé par l'autorité de certification. À noter qu'ici si l'autorité de certification du proxy n'avait pas été dans présent dans le navigateur, celui-ci aurait émis une alerte.

Ci-dessous on voit que le certificat présenté est celui du proxy (immortal), et non plus celui du serveur. On voit bien que les empreintes SHA256 sont différentes.

![screen6](../medias/https-interception/screen6.png?raw=true)

Si le certificat est accepté par le client et que nous essayons de nous enregistrer :

![screen7](../medias/https-interception/screen1.png?raw=true)

Nous arrivons bien sur la page secure.php, et notre connection est bien effectuée en HTTPS. Le client n'a constaté aucuns changement au niveau de sa navigation.

![screen8](../medias/https-interception/screen3.png?raw=true)

Par contre, la machine immortal a jouée le rôle d'un proxy et a été capable de récupérer la communication en clair. Ici on voit que le nom d'utilisateur, le mot de passe ainsi que le cookie de session ont pût être capturés :

![screen9](../medias/https-interception/screen9.png?raw=true)
