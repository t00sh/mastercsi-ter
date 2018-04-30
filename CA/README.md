Ensemble de scripts basés sur l'outil _openssl_ et permettant de générer des certificats.

------------------------------------

# create-ca.sh

Ce script permet de créer une autorité de certification auto-signée. Le script va créer deux fichiers :

- _root-ca.key_ : la clef privée de l'autorité de certification ;

- _root-ca.pem_ la clef publique, à installer chez les clients.


Utilisation :

```bash
./create-ca.sh
```
# new-cert.sh

Une fois l'autorité de certification créée, ce script permet de générer un certificat signé par celle-ci. Le script va créer deux fichiers :

- _cert.pem_ : la clef publique du serveur ;

- _cert.key_ : la clef privée du serveur.

Les deux fichiers sont à installer sur le serveur Web.

Utilisation :

```bash
./new-cert.sh
```
