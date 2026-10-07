La CI exécutait le lint et les tests, sans mesure de couverture ni seuil bloquant.
Les assertions existantes ne vérifiaient aucun montant avec virgule ; le test numérique n'avait aucune assertion sur le résultat.
Le correctif n'ajoutait aucun test de régression : une CI verte attestait seulement la réussite de ces contrôles, pas la fiabilité des montants exportés.

# Couverture et fiabilité

## État avant la pratique

La théorie est documentée dans [theorie.md](theorie.md). Sur `app/normalize.py`, la mesure de référence du 7 octobre 2026 donne 73,33 % de lignes, 62,5 % de branches et 69,57 % combinés (70 % affichés). Le test creux a ensuite été supprimé : l'état actuel donne 70 % de lignes, 56,25 % de branches et 65,22 % combinés (65 % affichés). Les deux tests restants passent. La couverture indique les chemins exécutés, pas la qualité des assertions.

## Décisions pour la pratique

- Ajouter une assertion de régression sur `1 250,00 €`, puis vérifier les huit échantillons avec des valeurs attendues indépendantes du code testé.
- Examiner les branches manquantes et les entrées invalides : l'objectif de 90 % de branches sur le normaliseur se mesure séparément du score combiné.
- Conserver le code de production dans le périmètre. Justifier toute exclusion ; un appel réseau simulable ne justifie pas à lui seul une exclusion.
- Choisir le seuil global après les tests utiles, à partir du score exact. `fail_under` bloque sous ce seuil ; en mode branches, il porte sur le total combiné de `app`, pas sur les seules branches de `normalize.py`.
- Vérifier que retirer les tests de normalisation déclenche réellement le garde-fou, puis valider la CI sous Python 3.11.

**Seuil retenu : 89 % du total combiné de `app`**, configuré dans `[tool.coverage.report]` avec `fail_under = 89`. La suite renforcée atteint 83/92 opportunités, soit 90,22 %. Le normaliseur atteint 100 % de lignes et 100 % de branches : les huit factures, les entrées numériques, l'espace fine insécable, le signe positif, les montants illisibles et l'absence de montant ont des assertions. Aucun code de production n'est exclu. La marge de 1,22 point évite de régler le seuil sur un arrondi ; la suppression des tests de normalisation reste nettement bloquée. Le brief demande un seuil supérieur à la mesure et une PR verte : ces exigences sont contradictoires pour la même suite. Nous retenons un seuil atteignable et un contrôle négatif explicite.

Les tests unitaires restent déterministes et sans appel LLM réel : ils vérifient les transformations rapidement et sans exposer de données ni dépendre du réseau. La couverture ne certifie ni sécurité ni performance ; les validations métier avant export et les tests du client HTTP devront être évalués selon leur propre périmètre.

## Relancer la mesure en local

Après installation des dépendances, depuis la racine :

```bash
.venv/bin/pytest --cov=app --cov-branch --cov-report=term-missing
```

Pour obtenir les pourcentages séparés de lignes et de branches :

```bash
.venv/bin/pytest --cov=app --cov-branch --cov-report=term-missing --cov-report=json:/tmp/factum-coverage.json
```

Lire `files["app/normalize.py"].summary.percent_statements_covered` et `percent_branches_covered` dans le JSON ; `percent_covered` est le score combiné.

## Validation locale de la pratique

Le 7 octobre 2026, sous Python 3.12.13 puis Python 3.11.15 (version mineure de la CI) : 16 tests passent avec le même score de 90,22 %. Le lint réussit. Pour reproduire le contrôle négatif sans supprimer le fichier :

```bash
.venv/bin/pytest --cov=app --cov-branch --ignore=tests/test_normalize.py
```

Le contrôle négatif a échoué comme prévu : le test du pipeline passe, mais le total combiné tombe à 72,83 %, sous le seuil de 89 %. Les statuts GitHub des deux PR restent à confirmer séparément ; une réussite locale ne vaut pas validation distante.
