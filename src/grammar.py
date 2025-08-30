NAME = ["jarvis"]

ACTIONS = [## ACTIONS
            "allume", 
            #"éteins",
            "ouvre",
            "ferme", 
            "baisse",
            "augmente",
            "verrouille",]
NOMS = [ "musique", 
            "fenetre",
            "active",
            "volume", 
            "lumiere",
            "terminal",
            "terminaux",
            "navigateur",
            "pc",
            "toi",
            "fichier",
            "document",
            "ordinateur",
            "ecran",]

MISC = [ ## MISC
            "oui",
            "pourcent",
            "les",
            "le",
            "l",
            "a",
            "de",
            "jusqu'a",
            "non",
            "[unk]"]

NOMBRES = [ "zero",
            "dix",
            "vingt",
            "trente",
            "quarante",
            "cinquante",
            "soixante",
            "soixante-dix",
            "quatre-vingt",
            "quatre-vingt-dix",
            "cent"]

NUMBER_DICT = {
    "zero" : 0,
    "dix" : 10,
    "vingt" : 20,
    "trente" : 30,
    "quarante" : 40,
    "cinquante" :50,
    "soixante":60,
    "soixante-dix" :70,
    "quatre-vingt":80,
    "quatre-vingt-dix" :90,
    "cent" :100

}
GRAMMAR = NAME + ACTIONS + NOMS + MISC + NOMBRES