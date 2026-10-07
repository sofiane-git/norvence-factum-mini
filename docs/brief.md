# Contexte du projet

Chez Norvence Gestion (syndic de copropriété), l'outil Factum extrait avec un LLM les champs des factures d'artisans et les pousse en comptabilité. Il y a trois semaines, 37 factures à « 1 250,00 € » sont parties à 125 000 € : le module de normalisation ne lisait pas la virgule décimale. Le correctif a été poussé sans test, et la CI est restée verte avant, pendant et après. Le post-mortem se termine sur une question : « pourquoi la CI était-elle verte ? »

## Modalités pédagogiques

### Théorie (25 min)

1. Installez `pytest-cov` et lancez `pytest --cov=app --cov-branch --cov-report=term-missing`. Relevez les deux pourcentages de `normalize.py` : lignes et branches. Ils ne sont pas les mêmes. Cherchez dans la documentation de `coverage.py` ce qu'est la branch coverage, puis expliquez en une phrase pourquoi la ligne du `if` compte comme couverte alors que la branche « virgule » ne l'est pas.
2. Ouvrez `tests/test_normalize.py`. Un des tests ne vérifie rien. Lequel ? Supprimez-le, relancez la mesure : le pourcentage a-t-il bougé ? Que conclure sur ce que la couverture mesure vraiment ?
3. Dans la documentation de `coverage.py`, trouvez à quoi servent `fail_under`, `omit` et `exclude_lines`. Laquelle de ces options permet de tricher avec le score ? Donnez un exemple d'exclusion légitime dans ce repo.
4. Lisez l'article de Fowler (5 min). Quel niveau de couverture trouve-t-il normal ? Que dit-il d'un 100 % ?
5. Écrivez en 3 lignes, en tête de `docs/couverture.md`, pourquoi la CI était verte pendant l'incident.

### Pratique (25 min)

1. Dans `pyproject.toml`, activez la couverture de branches sur le dossier `app` (section `[tool.coverage.run]`).
2. Remplacez le test creux par un test paramétré qui joue les 8 lignes de `tests/fixtures/echantillons.jsonl` : chaque cas compare la valeur produite à la valeur attendue. Cherchez `parametrize` dans la doc pytest.
3. Relancez la mesure. `normalize.py` doit atteindre 90 % de branches. Sinon, lisez la colonne `Missing` pour trouver la branche oubliée et ajoutez un cas.
4. Fixez le seuil dans `pyproject.toml` (section `[tool.coverage.report]`, option `fail_under`), au-dessus de la mesure que vous venez d'obtenir. Un commentaire à côté justifie le chiffre.
5. Dans `.github/workflows/ci.yml`, ajoutez `--cov=app --cov-branch` à la commande pytest. Rien d'autre : le seuil ne va pas dans le workflow.
6. Ouvrez une PR avec vos tests et votre configuration. Attendez qu'elle soit verte.
7. Sur une autre branche, supprimez `tests/test_normalize.py` et ouvrez une seconde PR. Elle doit être rouge. Lisez le message d'échec, puis fermez-la sans la fusionner.
8. Complétez `docs/couverture.md` sous vos 3 lignes : le seuil retenu et sa justification, la commande pour relancer la mesure en local.

## Modalités d'évaluation

Individuel.

### Livrables

- Fork public avec deux PR : une verte, une rouge fermée sans merge.
- `tests/test_normalize.py` paramétré, sans test creux ; `pyproject.toml` portant la configuration et le seuil.
- `docs/couverture.md` : les 3 lignes « pourquoi vert » et le seuil justifié.
- Quiz validé à 6/8.
