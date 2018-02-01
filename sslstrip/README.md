### Attaque SSLstrip

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
$ /mnt/host/sslstrip.py
```
