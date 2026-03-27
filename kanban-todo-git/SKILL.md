---
name: kanban-todo-git
description: "Un scanner de TODO hybride et un tableau Kanban basé sur Python qui utilise l'historique Git pour suivre le flux des tâches et calculer des métriques. Analyse les marqueurs BUG/TODO/IMPROVEMENT, les organise, et maintient un tableau Kanban en Markdown (To Do, In Progress, Review, Done) avec des limites WIP, des métriques de temps de cycle/délai, et une analyse des goulots d'étranglement pour les agents IA."
category: productivity
---

# kanban-todo-git (Version Python / Agent IA)

Un scanner de TODO et tableau Kanban qui utilise Python et l'historique Git pour suivre le flux de travail et calculer les métriques. Conçu pour être exécuté par un Agent IA coordinateur, il scanne les marqueurs dans le code, maintient un tableau Markdown (To Do, In Progress, Review, Done) et génère des données JSON pour faciliter le dispatching des tâches.

## Quand utiliser ce Skill
- Vous souhaitez suivre la dette technique, les demandes de fonctionnalités et les améliorations découvertes dans votre code.
- Vous préférez un système léger, piloté par Python et Git, plutôt que des outils externes lourds.
- Vous travaillez avec des agents IA qui ont besoin de lire l'état du projet via une sortie JSON structurée.
- Vous voulez des métriques réelles (lead time, cycle time, débit) pour améliorer la prévisibilité.

## Concepts de base
Ce skill combine deux approches :
1. **Scanner Python** : Analyse le code via des expressions régulières pour trouver les marqueurs (BUG:/TODO:/IMPROVEMENT:).
2. **Tableau Kanban** : Visualise le flux avec des limites WIP (Work In Progress).

Contrairement à un simple script Bash, l'utilisation de Python garantit l'idempotence et permet une interaction fluide avec les agents IA via le flag `--json`.

## Prérequis
- Dépôt Git (initialisé ou existant).
- Python 3.6 ou supérieur.
- Aucune dépendance externe (utilise uniquement la bibliothèque standard Python : `os`, `re`, `json`, `subprocess`, `pathlib`).

## Flux de travail étape par étape

### Étape 0 — Initialisation et lecture de l'état
Le script `kanban_scanner.py` charge le fichier `TODO.md` s'il existe en mémoire (parsing) pour préserver l'état actuel des colonnes et des cases cochées.

### Étape 1 — Scan du code source
Le script parcourt tous les fichiers non binaires et non exclus à la recherche des marqueurs :
- `BUG:` → défauts à corriger.
- `TODO:` → fonctionnalités à implémenter.
- `IMPROVEMENT:` → refactorisation ou optimisation.

Dossiers exclus par défaut : `.git/`, `node_modules/`, `dist/`, `build/`, `coverage/`, `.next/`, `out/`, `.cache/`, `__pycache__/`.

### Étape 2 & 3 — Synchronisation du Kanban
Pour chaque élément découvert :
- S'il est **nouveau** : Ajouté à la colonne **To Do**.
- S'il est **existant** : Reste dans sa colonne actuelle (l'état est conservé manuellement ou par l'agent coordinateur).
- S'il est **résolu** (n'est plus dans le code) : Déplacé automatiquement vers **Done** avec une coche `[x]`.

**Règle d'or** : Additif uniquement. Aucun élément non coché n'est supprimé s'il est encore dans le code.

### Étape 4 — Alertes de limites WIP (Work In Progress)
Le script vérifie les limites (To Do: 3, In Progress: 2, Review: 1). Si une colonne dépasse sa limite, une alerte est générée (et incluse dans le JSON pour l'agent IA).

### Étape 5 — Génération du Rapport Markdown et/ou JSON
Le script met à jour le fichier `TODO.md` avec l'analyse des goulots d'étranglement. Si exécuté avec `--json`, il renvoie un payload structuré contenant les métriques et les tâches disponibles pour qu'un agent IA puisse les dispatcher.

---

## Exemple d'utilisation (Humain & IA)

1. **Lancement standard (Génération Markdown) :**
```bash
python kanban_scanner.py
```
*Met à jour le fichier TODO.md et affiche les alertes WIP dans la console.*

2. **Lancement par un Agent Coordinateur :**
```bash
python kanban_scanner.py --json
```
*L'agent reçoit un JSON contenant les tâches `To Do` et décide de déléguer la correction d'un `BUG:` à un sous-agent.*

3. **Mise à jour de l'état (par l'Humain ou l'Agent) :**
Déplacez manuellement une ligne de `## To Do` vers `## In Progress` dans le fichier `TODO.md` et changez `[ ]` en `[~]`. Le script Python respectera ce changement au prochain scan.

4. **Sauvegarde :**
```bash
git add TODO.md
git commit -m "chore(todo): update Kanban board via AI agent"
```

## Étapes de vérification
1. Vérifiez que `TODO.md` contient les quatre colonnes avec les bonnes limites WIP.
2. Lancez `python kanban_scanner.py --json` et vérifiez que le JSON généré contient bien les tâches disponibles.
3. Supprimez un marqueur `BUG:` de votre code, relancez le script, et vérifiez qu'il passe bien dans la colonne `Done` avec `[x]`.
4. Vérifiez que les chemins de fichiers (normalisés avec `/` par `pathlib`) pointent vers les bons endroits.

## Dépannage
- **Marqueurs non détectés** : Assurez-vous d'utiliser exactement `BUG:`, `TODO:`, ou `IMPROVEMENT:` (sensible à la casse).
- **Faux éléments résolus** : Ne commentez pas temporairement les marqueurs, sinon le script Python pensera qu'ils sont résolus et les placera dans "Done".
- **Chemins Windows** : Contrairement à l'ancienne version Bash, l'utilisation de `pathlib` en Python normalise automatiquement les chemins avec des barres obliques (`/`), vous n'aurez donc plus de problèmes de compatibilité.

## Personnalisation
Pour adapter ce script à votre flux de travail :
1. Éditez le dictionnaire `WIP_LIMITS` en haut du fichier `kanban_scanner.py`.
2. Ajoutez de nouveaux dossiers à ignorer dans le set `EXCLUDED_DIRS`.
3. Modifiez la liste `MARKERS` si vous souhaitez suivre `FIXME:` ou `HACK:`.

## Intégration Multi-Agents (Hermes & Discord)

Ce skill est conçu pour s'intégrer dans un écosystème multi-agents (ex: un Coordinateur et un Développeur) communiquant via Discord.

### Configuration du Coordinateur (Cron)
Le coordinateur doit lire la sortie `--json` du script et distribuer les rôles sur différents canaux :
- **Reporting & Alertes WIP :** Envoyés dans le canal de management.
- **Délégation de code :** Envoyée dans le canal technique.

### Le Prompt de Délégation (Standard)
Lorsque le Coordinateur assigne une tâche issue du Kanban à l'Agent Codeur, il DOIT utiliser cette structure de prompt pour garantir que le Kanban se mette à jour automatiquement au prochain cycle :

> "Agent Codeur, j'ai une tâche prioritaire pour toi issue du Kanban.
> **Mission :** {tache_desc}
> **Emplacement :** Fichier `{fichier}`, autour de la ligne `{ligne}`.
> 
> **Instructions strictes :**
> 1. Analyse le contexte autour du marqueur.
> 2. Apporte la correction nécessaire au code.
> 3. **CRUCIAL :** Une fois la correction faite, tu dois IMPÉRATIVEMENT supprimer la ligne contenant le commentaire d'origine (`// BUG: ...` ou `# TODO: ...`). C'est cette suppression qui permet au système Kanban de détecter que la tâche est 'Done'.
> 4. Ne modifie pas le reste du fichier si ce n'est pas strictement nécessaire."
