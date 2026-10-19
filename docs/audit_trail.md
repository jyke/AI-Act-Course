# Politique de journalisation et piste d’audit

## Objet et périmètre

L’API Iris écrit une ligne JSON par prédiction dans `logs/audit.jsonl`. Cette piste sert à retracer une prédiction, vérifier la version du modèle utilisée et faciliter le diagnostic d’incidents. Le fichier est conservé sur le volume `./logs` monté par Docker Compose.

Le middleware HTTP écrit également des événements structurés sur la sortie standard du processus. Ils contiennent le chemin d’URL, une latence, un identifiant de requête et un horodatage. Ces événements sont distincts des enregistrements de prédiction et ne sont pas écrits dans `logs/audit.jsonl`.

## Données enregistrées

Chaque ligne de `logs/audit.jsonl` peut contenir les champs suivants :

| Champ | Utilité | Donnée brute conservée ? |
| --- | --- | --- |
| `request_id` | Retrouver une prédiction et la distinguer des autres. | Non : identifiant aléatoire généré pour l’opération. |
| `model_version` | Identifier la version fonctionnelle du modèle. | Sans objet. |
| `git_sha` | Relier la prédiction au code source déployé. | Sans objet. |
| `mlflow_run_id` | Retrouver l’exécution d’entraînement associée. | Sans objet. |
| `prediction` | Reconstituer le résultat produit. | Résultat conservé. |
| `confidence` | Examiner le niveau de confiance retourné par le modèle. | Valeur conservée. |
| `latency_ms` | Mesurer le temps de calcul de la prédiction. | Valeur conservée. |
| `user_id_pseudo` | Relier les prédictions d’un même utilisateur sans écrire son identifiant directement. | L’identifiant brut n’est pas écrit. |

Le code ne journalise pas les quatre mesures Iris reçues (`sepal_length`, `sepal_width`, `petal_length`, `petal_width`), ni le corps complet de la requête. Il ne journalise pas non plus d’horodatage dans `audit.jsonl` à ce jour. L’horodatage du middleware est dans un autre flux ; son identifiant de requête est généré séparément de celui de la prédiction. Il ne faut donc pas supposer que ces deux événements peuvent être rapprochés par leur identifiant.

`src/audit_query.py` sait rechercher une entrée à partir de `request_id`. Il affiche aussi un éventuel `input_hash`, mais l’application actuelle ne produit pas ce champ.

## Finalités et base légale

Les finalités prévues sont la traçabilité des prédictions, le débogage, l’audit technique et l’investigation d’incidents. Les journaux ne doivent pas être réutilisés pour établir un profil des utilisateurs ou prendre une décision distincte de la prédiction sans nouvelle analyse de finalité et de base légale.

Le responsable du traitement doit déterminer et documenter la base légale en fonction du service réel et de son contexte :

- **Article 6, paragraphe 1, point f, du RGPD** : l’intérêt légitime peut convenir à la sécurité, au diagnostic et à l’audit d’un service, après avoir identifié l’intérêt poursuivi et réalisé une mise en balance avec les droits des personnes. L’utilisateur doit être informé et peut exercer son droit d’opposition dans les conditions de l’article 21.
- **Article 6, paragraphe 1, point c, du RGPD** : cette base ne s’applique que si une obligation légale précise impose au responsable de conserver ces journaux. Le projet seul ne démontre pas l’existence d’une telle obligation.

La démonstration Iris ne suffit pas, à elle seule, à établir que le système relève d’une catégorie à haut risque de l’AI Act. Les obligations de journalisation de l’article 12 et de conservation de l’article 19 visent les systèmes d’IA à haut risque concernés. Si cette qualification s’applique à un déploiement réel, les obligations applicables doivent être réévaluées. L’article 19 prévoit, pour les journaux sous le contrôle du fournisseur, une durée appropriée à la finalité d’au moins six mois, sauf règle applicable différente.

Références : [RGPD, règlement (UE) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra) ; [AI Act, règlement (UE) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/fra).

## Durée de conservation

Pour ce projet de démonstration, la durée cible proposée est de **six mois**, puis suppression des entrées arrivées à échéance. Cette durée est un choix de conception à valider par le responsable du traitement selon les besoins réels ; ce n’est pas une durée minimale générale imposée par le RGPD. Le minimum de six mois de l’article 19 de l’AI Act ne concerne que les journaux de systèmes à haut risque auxquels cet article s’applique, sous réserve des règles de protection des données et des autres règles applicables.

**Limite actuelle :** l’application ajoute les lignes au fichier sans mécanisme de purge ni date d’expiration. La durée cible n’est donc pas appliquée automatiquement. Avant un déploiement opérationnel, il faut mettre en place une purge contrôlée (planifiée ou par rotation), documenter les sauvegardes et vérifier que les copies sont également supprimées à échéance. Le volume Docker rend le fichier persistant ; supprimer ou recréer le conteneur ne constitue pas une politique de conservation.

## Protection et pseudonymisation

`user_id` est transformé par HMAC-SHA-256 avec `AUDIT_HMAC_KEY` avant son écriture sous le nom `user_id_pseudo`. Le même identifiant et la même clé produisent le même pseudonyme, ce qui permet de relier plusieurs événements. La valeur n’est pas réversible comme un chiffrement, mais elle reste une donnée pseudonymisée : une personne peut rester identifiable par recoupement ou par calcul avec la clé. Elle demeure donc une donnée personnelle au sens du RGPD.

La clé doit être aléatoire, suffisamment longue, fournie par un gestionnaire de secrets ou une variable d’environnement protégée, et accessible uniquement aux personnes et services autorisés. La valeur de développement codée par défaut dans l’application ne convient pas à la production : configurez `AUDIT_HMAC_KEY` avant tout déploiement réel. Une rotation de clé empêche de relier directement les pseudonymes produits avant et après la rotation, sauf migration contrôlée.

L’accès au fichier et aux sauvegardes doit être restreint. Les journaux ne doivent pas être publiés dans des dépôts, images ou rapports accessibles sans autorisation. Le transport et le stockage doivent être protégés conformément au contexte de déploiement.

## Droits des personnes

Les demandes d’accès, de rectification, d’effacement, de limitation et d’opposition doivent être adressées au responsable du traitement ou au contact indiqué dans la notice de confidentialité. L’identité du demandeur doit être vérifiée de façon proportionnée avant toute recherche ou modification.

L’application ne fournit actuellement aucun endpoint de gestion des droits. L’outil `src/audit_query.py` permet une recherche par `request_id`, mais ne permet pas de retrouver automatiquement les lignes à partir de l’identité de la personne. Le pseudonyme HMAC étant déterministe, un opérateur autorisé qui dispose de la clé peut le recalculer à partir de l’identifiant fourni par la personne, puis localiser les lignes correspondantes ; cette opération doit être encadrée et tracée séparément.

Après vérification, le responsable doit répondre dans les délais prévus par le RGPD, rectifier les données inexactes lorsque cela est possible, et effacer les données lorsqu’aucune exception légale ne justifie leur conservation. Les modifications ou suppressions doivent aussi être propagées aux copies et sauvegardes selon leur cycle de vie. Si une obligation de conservation ou un motif légitime prévaut sur une demande d’effacement, la décision doit être motivée et la conservation limitée à ce qui est nécessaire.

## Écarts connus avant un déploiement réel

- Ajouter un horodatage UTC dans chaque entrée `audit.jsonl`.
- Utiliser un identifiant de corrélation commun entre le middleware et la prédiction, et le retourner de manière cohérente au client.
- Appliquer automatiquement la durée de conservation retenue et la suppression des sauvegardes à échéance.
- Retirer le secret de développement par défaut en production et gérer la clé hors du code.
- Formaliser la base légale, l’intérêt légitime le cas échéant, les informations fournies aux utilisateurs, les rôles d’accès et le processus de traitement des demandes.
