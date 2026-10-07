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

**Seuil retenu : à déterminer pendant la pratique**, après mesure de la suite renforcée. Aucun seuil n'est encore configuré. Le brief demande un seuil au-dessus de la mesure obtenue tout en exigeant une PR verte : un seuil réellement supérieur au score exact ferait échouer cette même suite. La décision fiable sera un seuil atteignable, justifié par les risques couverts et la capacité à détecter la suppression des tests, sans modifier le périmètre pour embellir le score.

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

Lire `files["app/normalize.py"].summary.percent_statements_covered` et `percent_branches_covered` dans le JSON ; `percent_covered` est le score combiné. La configuration et le seuil définitifs seront renseignés à la fin de la pratique.
