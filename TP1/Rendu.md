

# TP-1 Docker – Compte rendu

## 1. Installation de Docker

J’ai installé **Docker Desktop** sur Windows via le site officiel [docs.docker.com](https://docs.docker.com/get-docker/).
Pour vérifier, j’ai lancé :

```powershell
docker --version
```

👉 Résultat : `Docker version 28.0.4, build b8034c0` 

- installation OK .

Au tout début, j’ai quand même eu une erreur de connexion au démon Docker (`error during connect… pipe not found`). J’ai dû relancer Docker Desktop et ensuite la commande a bien fonctionné.

 

## 2. Objectif du TP

L’idée générale était de se familiariser avec :

* Les bases de Docker (images, conteneurs).
* Les commandes principales (`pull`, `run`, `ps`, `rm`).
* Le déploiement rapide d’un serveur web dans un conteneur.

 

## 3. Exercice 1 – Manipulation de base

### Vérification de la version

```powershell
docker -v
```

→ La version s’affiche correctement.

### Liste des images locales

```powershell
docker images
```

J’avais déjà une image `n8nio/n8n` qui traînait d’un autre essai (1,2GB…).

### Téléchargement de l’image *hello-world*

```powershell
docker pull hello-world
```

→ Image récupérée sans problème.

### Lancement du conteneur *hello-world*

```powershell
docker run hello-world
```

Résultat attendu : le fameux message *“Hello from Docker!”* ✨.
Ça confirme que mon installation fonctionne.

### Vérification des conteneurs

* `docker ps` → rien (logique, car `hello-world` se termine direct).
* `docker ps -a` → j’ai vu le conteneur `hello-world` arrêté + l’ancien `n8n`.

### Suppression d’un conteneur

```powershell
docker rm d556854871aa
```

→ Conteneur supprimé avec succès.


 

## 4. Exercice 2 – Serveur web Nginx

### Téléchargement de Nginx

```powershell
docker pull nginx
```

→ L’image s’est bien téléchargée.

### Lancement du serveur

```powershell
docker run -d -p 8080:80 --name mon_nginx nginx
```

→ Le conteneur tourne en arrière-plan.

### Vérification

```powershell
docker ps
```

→ Le conteneur `mon_nginx` est bien actif, mappé sur le port 8080.

### Accès via navigateur

En allant sur [http://localhost:8080](http://localhost:8080), j’ai bien obtenu la page d’accueil par défaut de Nginx 🎉.

### Arrêt et suppression

* `docker stop mon_nginx` → arrêt OK.
* `docker rm mon_nginx` → conteneur supprimé proprement.

 ## 5. Exercice 4-5 : Flask + MongoDB (multi-conteneurs)

La dernière étape consistait à faire communiquer Flask avec une base MongoDB.

J’ai d’abord créé un réseau Docker :

```powershell
docker network create appnet
```

Puis lancé MongoDB :

```powershell
docker run -d --name mongo --network appnet -p 27017:27017 mongo:6.0
```

Ensuite, j’ai rebuild mon app Flask, cette fois avec `pymongo` installé, et un endpoint `/db` qui envoie un `ping` à Mongo :

```powershell
docker build -t flask-mongo-app .
docker run -d --name app --network appnet -p 5000:5000 -e MONGO_URI="mongodb://mongo:27017" flask-mongo-app
```

Difficultés rencontrées :

* Plusieurs fois, j’ai eu des conflits de noms (`/app` ou `/mongo` déjà existants). J’ai appris à régler ça avec :

  ```powershell
  docker stop app && docker rm app
  docker stop mongo && docker rm mongo
  ```
* Parfois, j’oubliais le réseau ou la variable d’environnement → ce qui cassait la connexion. Une fois corrigé, l’app répondait bien.

Résultat :

* Sur `/` → Hello World animé.
* Sur `/db` → message *“MongoDB OK (ping réussi)”*.


## Bilan

* J’ai validé que Docker fonctionnait sur ma machine avec `hello-world`.
* J’ai appris à **lister, lancer, arrêter et supprimer** des conteneurs.
* J’ai réussi à déployer un serveur **Nginx** et à l’atteindre via mon navigateur.
* J’ai aussi eu une petite erreur de connexion au début (daemon non dispo), mais après redémarrage de Docker Desktop, tout est rentré dans l’ordre.
* Construire une image personnalisée avec Flask.

* Faire communiquer deux conteneurs via un réseau Docker (Flask + Mongo).


### Copie du shell
```bash
Windows PowerShell
Copyright (C) Microsoft Corporation. Tous droits réservés.

Installez la dernière version de PowerShell pour de nouvelles fonctionnalités et améliorations ! https://aka.ms/PSWindows

PS C:\Users\adame> docker -v
Docker version 28.0.4, build b8034c0
PS C:\Users\adame> docker --version
Docker version 28.0.4, build b8034c0
PS C:\Users\adame> docker images
error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": open //./pipe/dockerDesktopLinuxEngine: Le fichier spécifié est introuvable.
PS C:\Users\adame> docker images
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
n8nio/n8n    latest    f8fd85104e5a   3 months ago   1.2GB
PS C:\Users\adame> docker pull hello-world
Using default tag: latest
latest: Pulling from library/hello-world
17eec7bbc9d7: Pull complete
Digest: sha256:a0dfb02aac212703bfcb339d77d47ec32c8706ff250850ecc0e19c8737b18567
Status: Downloaded newer image for hello-world:latest
docker.io/library/hello-world:latest
PS C:\Users\adame> docker run hello-world

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

PS C:\Users\adame> docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
PS C:\Users\adame> docker ps -a
CONTAINER ID   IMAGE              COMMAND                  CREATED         STATUS                          PORTS                              NAMES
d556854871aa   hello-world        "/hello"                 2 minutes ago   Exited (0) About a minute ago                                      silly_yalow
26bb031dcdf8   n8nio/n8n:latest   "tini -- /docker-ent…"   3 months ago    Exited (255) 13 hours ago       5678/tcp, 0.0.0.0:8000->8000/tcp   N8N
PS C:\Users\adame> docker rm d556854871aa
d556854871aa
PS C:\Users\adame> docker ps -a
CONTAINER ID   IMAGE              COMMAND                  CREATED        STATUS                      PORTS                              NAMES
26bb031dcdf8   n8nio/n8n:latest   "tini -- /docker-ent…"   3 months ago   Exited (255) 13 hours ago   5678/tcp, 0.0.0.0:8000->8000/tcp   N8N
PS C:\Users\adame> docker pull nginx
Using default tag: latest
latest: Pulling from library/nginx
c3741b707ce6: Pull complete
716cdf61af59: Pull complete
a2da0c0f2353: Pull complete
14e422fd20a0: Pull complete
b1badc6e5066: Pull complete
e5d9bb0b85cc: Pull complete
14a859b5ba24: Pull complete
Digest: sha256:33e0bbc7ca9ecf108140af6288c7c9d1ecc77548cbfd3952fd8466a75edefe57
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest
PS C:\Users\adame> docker run -d -p 8080:80 --name mon_nginx nginx
3ba188964c86005aabe747031933bfc4971b8e760b2ac2aa237ed9603f30b49c
PS C:\Users\adame> docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                  NAMES
3ba188964c86   nginx     "/docker-entrypoint.…"   6 seconds ago   Up 5 seconds   0.0.0.0:8080->80/tcp   mon_nginx
PS C:\Users\adame> docker stop mon_nginx
mon_nginx
PS C:\Users\adame> docker rm mon_nginx
mon_nginx

PS C:\Users\adame\Desktop\Flask pour docker>  docker network create appnet

PS C:\Users\adame\Desktop\Flask pour docker>  build -t flask-mongo-app .
docker run -d --name app --network appnet -p 5000:5000 -e MONGO_URI="mongodb://mongo:27017" flask-mongo-app

PS C:\Users\adame\Desktop\Flask pour docker> docker build -t flask-mongo-app .
>> docker run -d --name app --network appnet -p 5000:5000 -e MONGO_URI="mongodb://mongo:27017" flask-mongo-app
[+] Building 1.6s (10/10) FINISHED     
```




