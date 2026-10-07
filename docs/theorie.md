# Théorie — réponses

## 1. Lignes vs branches sur `normalize.py`

Mesure de référence (`pytest --cov=app --cov-branch --cov-report=term-missing`), avant suppression du test creux de `tests/test_normalize.py` :

| Mesure | % |
|---|---|
| Lignes (`--cov=app`, sans `--cov-branch`) | 73 % |
| Combiné lignes+branches (`--cov-branch`) | 70 % |
| Branches seules (`percent_branches_covered` du JSON) | 62,5 % (affiché 62 %) |

Ligne 29 : `if "," in text and "." in text:`. Les deux tests appellent `normalize_amount("1250.00")` et `normalize_amount(1250)` — aucun des deux ne contient de virgule. L'appel numérique retourne dès la ligne 18. L'appel texte exécute la ligne 29 (donc comptée couverte en ligne), mais ne prend jamais la branche "vrai" : la condition vaut `False` et tombe dans le `elif` ligne 36, lui-même `False`. Le test du pipeline utilise également un montant sans virgule (`"980.50"`). Tout le bloc de gestion de la virgule décimale (lignes 30-35, 38) reste inexécuté.

**En une phrase :** la couverture de lignes compte qu'une instruction a tourné au moins une fois, peu importe avec quelles valeurs ; la couverture de branches exige que chaque chemin (`if` vrai *et* faux) ait été pris — et c'est exactement la branche "virgule" que personne n'a testée, celle qui a fait partir 37 factures à 125 000 €.

## 2. Le test creux

`test_normalize_numeric_input` (`tests/test_normalize.py:10-11`) :

```python
def test_normalize_numeric_input():
    normalize_amount(1250)
```

Il appelle la fonction mais ne fait aucun `assert`. Le test passe quel que soit le résultat retourné, y compris s'il est faux.

Mesure sans ce test (revérifiée le 7 octobre 2026 par désélection, puis après suppression effective du test ; même résultat) :

| | Avec le test creux | Sans le test creux |
|---|---|---|
| `normalize.py` (combiné) | 70 % | 65 % |
| `normalize.py` — lignes manquantes | 16, 30-35, 38, 42-43, 46 | 16, **18**, 30-35, 38, 42-43, 46 |

Le pourcentage **bouge** (70 % → 65 %) en supprimant un test qui ne vérifie rien : la ligne 18 (`return Decimal(str(raw)).quantize(CENT)`, chemin numérique) redevient "manquante". Ça confirme que le pourcentage mesure seulement si le code a été *exécuté*, pas si le résultat a été *vérifié*. Un test sans assertion gonfle le score exactement comme un test avec assertion — coverage.py ne peut pas distinguer les deux.

## 3. `fail_under`, `omit`, `exclude_lines`

- **`fail_under`** (section `[tool.coverage.report]`) : fait échouer la commande `coverage report`/`pytest --cov` si le pourcentage global tombe sous ce seuil. C'est un garde-fou de CI.
- **`omit`** (section `[tool.coverage.run]`) : exclut des fichiers entiers (par motif de chemin, ex. `tests/*`, migrations, scripts) du calcul de couverture.
- **`exclude_lines`** (section `[tool.coverage.report]`) : exclut des lignes précises (par regex, ex. `pragma: no cover`, `if TYPE_CHECKING:`) du dénominateur, ligne par ligne.

**Options permettant de tricher :** `omit` et `exclude_lines`. Omettre `app/normalize.py` ou exclure ses chemins difficiles fait disparaître du code du dénominateur sans améliorer les tests. Les exclusions doivent être restreintes et justifiées en revue. `exclude_lines` remplace les motifs d'exclusion par défaut ; pour ajouter un motif en conservant les défauts, préférer `exclude_also`.

**Exemple d'exclusion légitime dans ce repo :** le corps déclaratif `...` de `LLMClient.complete`, un `Protocol` décrivant une interface sans comportement métier. Selon la version de coverage.py, ce motif est déjà exclu par défaut ; vérifier le rapport avant d'ajouter une exclusion. À l'inverse, `HttpLLMClient.complete` contient du comportement réel : construction de requête, authentification et lecture de réponse. On peut tester ce code sans réseau en remplaçant `urllib.request.urlopen` par une simulation contrôlée. `MockLLMClient` ne teste pas cette implémentation HTTP, et aucun test d'intégration de celle-ci n'est présent dans le dépôt.

## 4. Fowler sur la couverture

Dans [« Test Coverage »](https://martinfowler.com/bliki/TestCoverage.html), Fowler attend, avec des tests réfléchis, une couverture dans le haut des **80 % ou dans les 90 %**. Il cite une couverture inférieure à la moitié comme signal de problème, sans établir un seuil universel de confiance à 80 %.

Sur 100 % : il se méfie d'un chiffre atteint pour satisfaire une cible plutôt que pour tester les comportements utiles. Un score élevé ne prouve pas la qualité des assertions. La couverture sert à repérer les zones inexécutées ; elle ne prouve pas la correction du code. Dans notre projet, viser tous les chemins pertinents du normaliseur peut rester utile : la décision dépend du risque financier et des comportements, pas du prestige du chiffre.

## 5. Pourquoi la CI était verte

Les trois lignes demandées sont en tête de [couverture.md](couverture.md). Le workflow actuel exécute le lint et `pytest`, sans collecte de couverture ni seuil. Les tests ne vérifient aucun format avec virgule, et le correctif décrit par le post-mortem n'a pas apporté de test de régression.

Un seuil global avec mesure de branches peut révéler un manque, mais ne garantit ni un cas précis ni une assertion correcte. La protection principale contre la récidive est un test explicite : `normalize_amount("1 250,00 €") == Decimal("1250.00")`, complété par une revue des autres formats et des erreurs attendues.

## Reproduire les mesures

Mesures revérifiées le 7 octobre 2026 avec Python 3.12.13, pytest 8.4.2, pytest-cov 7.1.0 et coverage.py 7.16.2. La CI utilise Python 3.11 : sa validation restera à effectuer pendant la pratique.

Depuis la racine, dans l'environnement installé :

```bash
.venv/bin/pytest --cov=app --cov-branch --cov-report=term-missing --cov-report=json:/tmp/factum-coverage.json
```

Avant suppression, le JSON donne `covered_lines / num_statements` (22/30) et `covered_branches / num_branches` (10/16) pour `app/normalize.py`. La colonne `Cover` combine lignes et branches : (22+10)/(30+16), soit 69,57 %, affiché 70 %. Ne pas la confondre avec les branches seules. Après suppression, la commande ci-dessus donne 21/30 lignes (70 %), 9/16 branches (56,25 %) et 30/46 combinés (65,22 %). Les deux tests restants passent. Le test creux a été supprimé conformément à la théorie ; le test paramétré sera ajouté pendant la pratique.

Sources : [mesure des branches](https://coverage.readthedocs.io/en/latest/branch.html), [configuration coverage.py](https://coverage.readthedocs.io/en/latest/config.html), [Fowler](https://martinfowler.com/bliki/TestCoverage.html).
