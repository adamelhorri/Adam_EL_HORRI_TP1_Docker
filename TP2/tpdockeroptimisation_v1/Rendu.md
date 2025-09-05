# Rendu du TP2 - Docker optimisation
## 1- Analyse préalable de performances

On mesure le temps necessaire pour build le dockerfile initial

```bash
Measure-Command { docker build -t app:baseline . }
```
Resultat : 

```bash
View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/6gc2og8hxfaepiyy9zfauyd7i

Days              : 0
Hours             : 0
Minutes           : 1
Seconds           : 4
Milliseconds      : 937
Ticks             : 649372912
TotalDays         : 0,000751589018518519
TotalHours        : 0,0180381364444444
TotalMinutes      : 1,08228818666667
TotalSeconds      : 64,9372912
TotalMilliseconds : 64937,2912

# environ 1 minute et 5 secondes
```
On run le dockerfile sur le localhost:3000 :

```html
<div>Hello world — serveur volontairement non optimisé mais fonctionnel</div>
```
Métadonnées de l'image : 

```bash
docker images | findstr app
docker history app:baseline
#Resultat :
app                 baseline   9d2900981ef7   4 minutes ago   1.73GB
```

On remarque que l'image est trop lourde 1,73GB 

On arrête le contenneur et supprime l'image 

```bash
docker stop app-baseline
docker rmi app:baseline
Untagged: app:baseline
Deleted: sha256:9d2900981ef7bec64f07b2dfa28dfced5391aa5d832aaaa4e32b2aa9bbcd6d34
```
## 2- Analyse de l'application Nodejs

Avant tout on installe les dépendances NPM
```bash
npm ci     
added 111 packages, and audited 112 packages in 2s
```
Le run reussit :

```html
<div>Hello world — serveur volontairement non optimisé mais fonctionnel</div>
```

## 3- Implementation du nouveau dockerfile

On garde l'ancien dockerfile (on le renomme dockerfile_old)
Le but maintenant est de créer un dockerfile optimisé permettant gain de performance et stockage

- On part d'une image 22-alpine
```dockerfile
FROM node:22-alpine AS builder
```
- On definit le variable d'environnement en evitant les dependance inutiles et en limitant la taille des logs aux warnings uniquement

```dockerfile
ENV NODE_ENV=production CI=true NPM_CONFIG_LOGLEVEL=warn
```
- On definit le repertoir comme precedement 

```dockerfile
WORKDIR /app
```
- On met les fichiers dependances en cache, ceci afin de permettre de les garder en cas d'update de server.js (gain temporel)

```dockerfile
COPY package*.json ./
```
- On installe les dependances en mode prod en utilisant `npm ci` au lieux de `npm install`, on omet les dependdances de dev (gain en stockage)
```dockerfile
RUN npm ci --omit=dev --no-audit --no-fund
```
- On copie le reste du projet 
```dockerfile
COPY . .
```
- On build 

```dockerfile
RUN npm run build
```
- On implemente un runner pour une finale sans les outils de build

```dockerfile
FROM node:22-alpine AS runner
```

- on implemente le nouvel environnement en mode prod et redefinit l'env de travail
```dockerfile
ENV NODE_ENV=production
WORKDIR /app
```
- on utilise un utilisateur non root (gain en securité)
```dockerfile
RUN addgroup -S appgrp && adduser -S app -G appgrp
```
- On copie uniquement ce qui est necessaire du builder 
```dockerfile
COPY --from=builder /app/. /app
```
- On redefinit le port à nouveau 
```dockerfile
EXPOSE 3000
```
- On fait tourner sur l'utilisateur app
```dockerfile
USER app
```
- On run lance le serveur

```dockerfile
CMD ["node", "server.js"]
```
## 4- Mesure des performances de l'image finale et comparaison
### 4-1- Mesure des performances
On mesure comme avant les performances et les metadonnés de la nouvelle image finale 

```bash
Measure-Command { docker build -t app:opt . }
```

Resultat : 
```bash
Days              : 0
Hours             : 0
Minutes           : 0
Seconds           : 18
Milliseconds      : 258
Ticks             : 182585146
TotalDays         : 0,000211325400462963
TotalHours        : 0,00507180961111111
TotalMinutes      : 0,304308576666667
TotalSeconds      : 18,2585146
TotalMilliseconds : 18258,5146

```
étant donné qu'on travaille avec un builder + runner et que les fichiers configuration, on relance le build de l'image après avoir changé les contenu de `server.js`

```js
res.send('Hello world — serveur volontairement non optimisé mais fonctionnel');
//devient
res.send('Hello world — serveur optimisé et fonctionnel');

```

On lance le serveur : 
```bash
docker run -d --rm -p 3000:3000 --name app-opt app:opt
```

Mesure de preformances : 
```bash
View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/w8mfuwbffm5sjcba0uib1e4tf


Days              : 0
Hours             : 0
Minutes           : 0
Seconds           : 5
Milliseconds      : 488
Ticks             : 54882548
TotalDays         : 6,35214675925926E-05
TotalHours        : 0,00152451522222222
TotalMinutes      : 0,0914709133333333
TotalSeconds      : 5,4882548
TotalMilliseconds : 5488,2548
```

Metadonnées :

```bash
docker images | findstr app:opt
docker images

REPOSITORY          TAG       IMAGE ID       CREATED         SIZE
app                 opt       f3f02879367d   4 minutes ago   244MB
```

## 5- Comparaison des resultats avant/après optimisation
### Vitesse de build 
- Avant : 1 minutes et 5 secondes
- Après : 
    - Builder + Runner (Build à vide): 18 secondes
    - Runner (build après save de cash +update du server.js) : 5 secondes
On remarque un gain considerable en temps de build essentiellement du aux pratiques correctes utilisées , le gain de rebuild est lui aussi considerable grace à la mise des packages en cache
### Taille de l'image 
- Avant : 1.73 GB
- Après : 244 MB

On remarque un gain considerable en stockage essenntiellement dû au type de l'image (base alpine) plus leger, la non-copie de node_modules et à l'usage de `npm ci`
###  Compte rendu final 
```md
| Critère        | Avant (baseline) | Après (optimisé) |
|----------------|------------------|------------------|
| Temps build    | ~65 s            | ~5 s             |
| Taille image   | 1.73 GB          | 244 MB           |
| Sécurité       | root             | user non-root    |
| Base           | node:latest      | node:22-alpine   |

```