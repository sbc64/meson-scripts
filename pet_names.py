import toml
import secrets

def format_name(n):
    return n.replace(" ", "-").lower()

def random_house():
    return secrets.choice(list(names_parsed['Houses'].keys()))

def random_person():
    h = random_house()
    p = secrets.choice(names_parsed['Houses'][h])
    return format_name("{}-{}".format(h, p))

names_parsed = toml.loads("""
[Houses]
Targaryen = [
  "Viserys",
  "Daenerys",
  "Aegon",
  "Aemon",
  "Rhaegar",
  "Rhaella",
  "Aerys",
  "Drogon",
  "Rhaegal",
  "Viserion",
  "Balerion",
  "Meraxes",
  "Vhagar"
]
Baratheon = [
  "Robert",
  "Stannis",
  "Renly",
  "Joffrey",
  "Myrcella",
  "Tommen",
  "Shireen"
]

Lannister = [
  "Tywin",
  "Cersei",
  "Jaime",
  "Tyrion",
  "Kevan",
  "Lancel",
  "Gregor",
  "Sandor"
]
Stark = [
  "Eddard",
  "Catelyn",
  "Robb",
  "Jon Snow",
  "Sansa",
  "Arya",
  "Bran",
  "Rickon",
  "Lyanna",
  "Roose",
  "Ramsay"
]

Martell = [
  "Doran",
  "Arianne",
  "Quentyn",
  "Trystane",
  "Oberyn"
]

SandSnakes = [
  "Obara",
  "Nymeria",
  "Tyene",
  "Sarella",
  "Elia",
  "Obella",
  "Dorea",
  "Loreza"
]

Tully = [
  "Hoster",
  "Brynden",
  "Edmure",
  "Catelyn",
  "Lysa"
]

Greyjoy = [
  "Balon",
  "Aeron",
  "Euron",
  "Asha",
  "Theon",
  "Yara"
]

Arryn = [
  "Jon",
  "Robert"
]

Tyrell = [
  "Mace",
  "Willas",
  "Margaery",
  "Loras",
  "Olenna Redwyne"
]

TheNightWatch = [
  "Lord Mormont",
  "Jon Snow",
  "Samwell Tarly",
  "Benjen Stark",
  "Bowen Marsh",
  "Donal Noye",
  "Eddison Tollett",
  "Maester Aemon",
  "Qhorin Halfhand",
  "Yoren"
]

[RenownedBeasts]
Direwolves = [
  "Grey Wind",
  "Ghost",
  "Lady",
  "Nymeria",
  "Summer",
  "Shaggydog"
]
Dragons = [
  "Archonei",
  "Arrax",
  "Caraxes",
  "Dreamfyre",
  "Essovius",
  "Ghiscar",
  "Grey Ghost",
  "Meleys",
  "Moondancer",
  "Morghul",
  "Seasmoke",
  "Sheepstealer",
  "Shrykos",
  "Silverwing",
  "Stormcloud",
  "Sunfyre",
  "Syrax",
  "Tessarion",
  "Tyaxes",
  "Valryon",
  "Vermac",
  "Vermithor",
  "Vermithrax",
  "Urrax"
]
""")

if __name__ == "__main__":
    print(random_person())
