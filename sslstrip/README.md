### Attaque SSLstrip

## Configuration du serveur

Pour générer le certificat côté serveur, on peut utiliser openssl :

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```


## Démo

Pour lancer l'attaque, il faut démarrer tout d'abords l'environnement de test de la façon suivante :

```
$ ./qemunet/qemunet.sh -x -S sslstrip
```

À partir de là, trois machines sont lancées :

- grave, la machine cliente

- opeth, la machine serveur

- immortal, la machine de l'attaquant, positionnée en homme du milieu.

Ensuite, sur immortal il faut lancer le script d'attaque comme suit :

```
$ /mnt/host/attack.sh
```
