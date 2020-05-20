# automation-parcoursup

## Installation

Commencez par [télécharger le fichier `.whl`](https://github.com/ewen-lbh/automation-parcoursup/releases/download/v0.1.0/automation_parcoursup-0.1.0-py3-none-any.whl)

```sh-session
$ pip install automation_parcoursup-X.X.X-py3-none-any.whl
# Configuration, il vous faut vos informations pour que le script se connecte automatiquement à votre compte
# Bientôt j'ajouterai un mode où on rentre ça manuellement au cas où vous ne me feriez pas confiance 
# (regardez le script si vous avez des doutes, *et vous devrez toujours*, ne jamais faire confiance aveuglement à un random sur internet)
$ echo -e 'PARCOURSUP_ID="Votre n° de dossier"\nPARCOURSUP_PASS="Votre mot de passe"' > ~/.parcoursup_creds
$ parcoursup
```

