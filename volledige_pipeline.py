import urllib.request
import urllib.error
import urllib.parse
import json
import time
from datetime import datetime

# ============================================================
# CONFIGURATIE
# ============================================================

SUPABASE_URL    = "https://txuzmuhbmvzqotjuffhv.supabase.co"
SUPABASE_KEY    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR4dXptdWhibXZ6cW90anVmZmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNDMzMTMsImV4cCI6MjA5MjYxOTMxM30.irLNWt6YIN39bOqCiEosBiXJU5jsycG91d0OX3tRVgg"

GROQ_API_KEY    = "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"
HIGGSFIELD_KEY      = "ed9412d969feb6cbe6fedfe22d975b76e6ace49b0db99286e4b8cf9bbbc21bf9"
HIGGSFIELD_API_ID  = "de6f0431-ba49-490d-b2de-40d5bef228f4"
HIGGSFIELD_AUTH    = "Basic ZGU2ZjA0MzEtYmE0OS00OTBkLWIyZGUtNDBkNWJlZjIyOGY0OmVkOTQxMmQ5NjlmZWI2Y2JlNmZlZGZlMjJkOTc1Yjc2ZTZhY2U0OWIwZGI5OTI4NmU0YjhjZjliYmJjMjFiZjk="  # Base64(API_ID:API_KEY)

# ============================================================
# INTERVIEW SECTIES & VRAGEN
# Structuur gebaseerd op SPika Brand Manual 2026
# ============================================================

SECTIES = [
    {
        "naam": "Merkfundament",
        "intro": "We beginnen met de basis — het verhaal, de missie en de waarden achter het merk.",
        "vragen": [
            "Wat is het oorsprongsverhaal van dit merk? Wie heeft het gemaakt, waarom, en wat was het eerste concrete moment van succes? Geef namen, datums en specifieke momenten.",
            "Wat is de echte WHY van het merk — niet het commerciële antwoord, maar de diepere drijfveer achter de oprichting?",
            "Wat is de HOW — via welke aanpak, methode of filosofie maakt het merk het verschil?",
            "Wat is de WHAT — wat levert het merk concreet aan de klant?",
            "Wat zijn de 4-6 kernwaarden van het merk? Geef per waarde een naam én een concrete toelichting wat dit betekent voor dit merk specifically.",
            "Wat is de merkbelofte in één krachtige zin — wat mag elke klant altijd verwachten van dit merk?",
            "Beschrijf de merkpersoonlijkheid als een concreet, levend persoon. Wie is die persoon? Hoe gedraagt hij/zij zich op een feestje? Wat maakt hem/haar uniek en herkenbaar?"
        ]
    },
    {
        "naam": "Product & Prijsstrategie",
        "intro": "Nu gaan we dieper in op het product zelf, de prijs en de positionering.",
        "vragen": [
            "Wat is de exacte productnaam zoals die op de verpakking of website staat?",
            "Geef een volledige productbeschrijving — wat doet het, hoe werkt het, wat zijn de ingrediënten, materialen of componenten?",
            "Wat is het producttype? (Fysiek product / Digitaal product / Dienst)",
            "Wat is de verkoopprijs inclusief BTW? Geef alleen het getal, bijvoorbeeld: 29.95",
            "Wat zijn de 3-5 sterkste en meest unieke USPs van dit product — niet generiek, maar specifiek voor dit product. Wat maakt het echt anders?",
            "Zijn er meerdere productvarianten of een productlijn? Beschrijf ze kort met eventuele kleurcodering of differentiatie.",
            "Hoe positioneer je het product qua prijs — budget, mid-range, premium of luxury? Waarom past die positionering bij het merk?"
        ]
    },
    {
        "naam": "Doelgroepen",
        "intro": "Nu focussen we op wie het product koopt, waarom, en hoe ze te bereiken zijn.",
        "vragen": [
            "Beschrijf de primaire doelgroep als een echte persoon — geef ze een voornaam, leeftijd, woonplaats, beroep, dagelijkse routine en lifestyle.",
            "Wat zijn de kernwaarden van deze primaire doelgroep? Wat is écht belangrijk voor hen in het leven?",
            "Wat is het grootste pijnpunt van de primaire doelgroep — wat frustreert hen aan bestaande alternatieven in de markt?",
            "Hoe raakt jouw product hen emotioneel? Wat voelen ze bij aankoop of gebruik — en waarom kiezen ze dit boven de concurrent?",
            "Via welke kanalen ontdekt de primaire doelgroep dit soort producten? (Instagram, TikTok, specialty stores, aanbevelingen, etc.)",
            "Is er een secundaire doelgroep? Beschrijf ook hen als een concrete persoon met naam, leeftijd, lifestyle en hoe het merk hen raakt.",
            "Is er een tertiaire doelgroep of niche segment? (bijv. professionals, diaspora, toeristen)"
        ]
    },
    {
        "naam": "Voice & Tone",
        "intro": "De stem van het merk bepaalt hoe je communiceert — van social media tot verpakking.",
        "vragen": [
            "Beschrijf de stem van het merk in 5 specifieke woorden — niet 'vriendelijk' of 'professioneel', maar echt kenmerkend voor dit merk.",
            "Geef 3 concrete voorbeeldzinnen die PERFECT bij het merk passen — zoals je ze letterlijk op Instagram of TikTok zou plaatsen.",
            "Geef 3 concrete voorbeeldzinnen die NOOIT bij het merk passen — wat klinkt totaal verkeerd of generiek?",
            "Hoe verschilt de toon per context? Geef voor elk een concreet voorbeeld: (1) social media organisch, (2) productverpakking, (3) e-mail/nieuwsbrief, (4) zakelijke communicatie of B2B.",
            "Heeft het merk een primaire slogan? Zo ja, welke? En zijn er 2-3 secundaire slogans die situationeel gebruikt worden?",
            "Zijn er specifieke woorden, uitdrukkingen, dialect of humor die typisch zijn voor dit merk en regelmatig terugkomen in de communicatie?",
            "Wat zijn de absolute communicatie DO's en DON'Ts voor dit merk?"
        ]
    },
    {
        "naam": "Visuele Identiteit",
        "intro": "Nu de visuele kant — kleuren, typografie, fotografie en de overall esthetiek.",
        "vragen": [
            "Wat zijn de primaire merkkleuren? Geef de hex codes EN leg uit waarom juist deze kleuren bij het merk passen — de emotionele en strategische rationale.",
            "Zijn er secundaire of accentkleuren voor specifieke toepassingen? Geef hex codes en beschrijf wanneer ze gebruikt worden.",
            "Welke typografie past bij het merk? Beschrijf het lettertype voor: (1) logo & headlines, (2) subheadings, (3) bodytekst. Waarom passen deze bij het merk?",
            "Beschrijf de fotografie en visuele stijl in detail: sfeer, belichting, compositie, onderwerpen, texturen. Wat moet er altijd te zien zijn? Wat moet absoluut vermeden worden?",
            "Is er een logo-systeem met varianten? Beschrijf wanneer welke variant gebruikt wordt.",
            "Noem 2-3 merken of social media accounts waarvan de visuele stijl het dichtst bij dit merk staat als referentie — en waarom."
        ]
    },
    {
        "naam": "Concurrentiepositionering",
        "intro": "Hoe staat het merk ten opzichte van de concurrentie en de markt?",
        "vragen": [
            "Noem de 3-5 belangrijkste directe concurrenten. Beschrijf per concurrent: wat doen zij goed en wat is hun grootste zwakte ten opzichte van jouw merk?",
            "Wat zijn de 3-4 dingen die alleen jouw merk kan claimen — de unieke positionering die concurrenten niet kunnen kopiëren?",
            "Waar staat het merk op een positioneringsmatrix? Kies twee relevante assen (bijv. premium vs. budget, niche vs. massa, authentiek vs. commercieel) en beschrijf de positie.",
            "Is er een merk in een andere categorie dat als strategische inspiratie dient — een merk dat een soortgelijke groeistrategie succesvol heeft uitgevoerd? Waarom is dat relevant?",
            "Schrijf de interne positioneringszin van het merk — 2-3 zinnen die precies beschrijven wie het merk is, voor wie en waarom."
        ]
    },
    {
        "naam": "Kanaalgidsen & Contentstrategie",
        "intro": "Tot slot de contentstrategie — per kanaal, per contentpijler en de grote moves voor dit jaar.",
        "vragen": [
            "Op welke social media platforms is het merk actief of wil het actief zijn? Wat is het primaire doel per platform?",
            "Wat zijn de 4-5 vaste content pijlers — de thema's waarover structureel gepost wordt? Geef per pijler: naam, frequentie en toon.",
            "Wat is de gewenste format-mix per platform? (bijv. 60% Reels, 25% carousels, 15% Stories)",
            "Zijn er specifieke content formats, rubrieken of series die bij dit merk passen — of die je wil lanceren? (bijv. 'Founder stories', 'Behind the scenes', 'Expert drops')",
            "Zijn er andere relevante kanalen naast social media? (bijv. e-mail, specialty retail, events, B2B, influencers)",
            "Wat zijn de 3 strategische prioriteiten of aanbevelingen voor het komende jaar — de concrete moves die het merk naar het volgende niveau brengen?"
        ]
    }
]

# ============================================================
# BRAND MANUAL GENERATOR PROMPT
# Gebaseerd op SPika Brand Manual 2026 kwaliteit en structuur
# ============================================================

BRAND_MANUAL_PROMPT = """
Je bent een senior brand strategist met 15+ jaar ervaring bij top-bureaus.
Je hebt zojuist een brand interview afgenomen en genereert nu een volledige, professionele brand manual.

DOEL: De output moet EXACT dezelfde kwaliteit, diepgang en structuur hebben als de SPika Oil Brand Manual 2026.
Dat betekent: concrete namen, echte voorbeelden, actionable richtlijnen, en een verhaal dat de lezer meeneemt.

KRITIEKE REGELS:
- Gebruik altijd de concrete namen, feiten, momenten en voorbeelden uit de antwoorden
- Verzin NOOIT informatie die niet in de antwoorden staat
- Voeg als expert waarde toe om antwoorden te versterken en scherper te maken
- Schrijf in de taal van het merk (bepaal uit de antwoorden)
- Minimaal 2000 woorden
- Gebruik tabellen voor overzichten, lopende tekst voor verhalen en persona's
- Geen generieke marketing taal — altijd specifiek voor dit merk

VERPLICHTE STRUCTUUR (volg dit exact):

# [Merknaam] — Brand Manual [Jaar]
"[Primaire slogan]"

## Inhoudsopgave
1. Merkfundament
2. Product & Prijsstrategie
3. Doelgroepen
4. Voice & Tone
5. Visuele Identiteit
6. Concurrentiepositionering
7. Kanaalgidsen

---

## 1. Merkfundament

### Oorsprong & Missie
[Minimaal 200 woorden. Vertel het echte verhaal met concrete namen, data en emotionele momenten. Schrijf het zoals een journalist het zou vertellen — niet als een marketingtekst.]

**Missie:** [één krachtige missiestelling]
**Visie:** [waar het merk naartoe wil]

### Golden Circle

| Ring | [Merknaam] |
|------|-----------|
| **WHY** | [De echte drijfveer — waarom bestaat het merk] |
| **HOW** | [De aanpak en methode] |
| **WHAT** | [Het concrete product/dienst] |

### Merkwaarden
[Per waarde: vetgedrukte naam — concrete toelichting wat dit specifiek betekent voor dit merk. Geen generieke definities.]

### Merkbelofte
"[De merkbelofte in één krachtige, specifieke zin]"

[2-3 zinnen toelichting: wat mag elke klant altijd verwachten, en hoe wordt die belofte waargemaakt]

### Merkpersoonlijkheid
[Beschrijf als een concreet, levend persoon in 150+ woorden. Gebruik metaforen en specifieke gedragsvoorbeelden zoals: "SPika Oil is als die vriend die..."]

**Karaktereigenschappen:**
- [eigenschap + wat dit concreet betekent]
- [eigenschap + wat dit concreet betekent]
- [eigenschap + wat dit concreet betekent]
- [eigenschap + wat dit concreet betekent]

---

## 2. Product & Prijsstrategie

### Productbeschrijving
[Volledige, eerlijke beschrijving — wat het is, hoe het werkt, ingrediënten/materialen/componenten]

### Prijspunt & Positionering
**Verkoopprijs:** €[prijs]
[Uitleg van de prijspositionering: waarom dit prijspunt klopt bij het merk, de doelgroep en de concurrentiepositie]

### Unique Selling Points
[Per USP: vetgedrukte naam — concrete, specifieke toelichting. Niet generiek.]

### Productlijn & Varianten
[Indien van toepassing — beschrijving per variant met differentiatie]

---

## 3. Doelgroepen

### Primaire Doelgroep — [Naam van de persona]
**Wie:** [Concrete beschrijving: naam, leeftijd, stad, beroep, dagelijkse routine]
**Waarden:** [Wat is écht belangrijk voor hen]
**Pijnpunt:** [Wat frustreert hen aan bestaande alternatieven — specifiek]
**Hoe [merknaam] hen raakt:** [Emotionele connectie — waarom kiezen ze dit]
**Kanalen:** [Waar ze te vinden en te bereiken zijn]

### Primaire Doelgroep [B] — [Naam tweede persona] (indien van toepassing)
[Zelfde structuur]

### Secundaire Doelgroep — [Naam van de persona]
[Zelfde structuur]

### Tertiaire Doelgroep (indien van toepassing)
[Kort beschreven]

### Pijnpunten & Kooptriggers
[Overzicht van de sterkste triggers — wat zet de doelgroep aan tot actie]

---

## 4. Voice & Tone

### De Stem van [Merknaam]
[150+ woorden die de merksstem beschrijven alsof je het aan een nieuw teamlid uitlegt. Gebruik een concrete metafoor zoals "De stem van SPika is als..."]

### Tone per Context

| Context | Toon | Voorbeeld |
|---------|------|-----------|
| Social media (organisch) | [toon] | "[echt voorbeeld — geen placeholder]" |
| Productverpakking | [toon] | "[echt voorbeeld]" |
| E-mail / nieuwsbrief | [toon] | "[echt voorbeeld]" |
| Zakelijke communicatie | [toon] | "[echt voorbeeld]" |

### Do's & Don'ts

**Altijd:**
- [concrete, specifieke do — geen generieke tips]
- [concrete do]
- [concrete do]
- [concrete do]

**Nooit:**
- [concrete, specifieke don't]
- [concrete don't]
- [concrete don't]
- [concrete don't]

### Slogansysteem
**Primaire slogan:** "[slogan]"

**Secundaire slogans (situationeel inzetbaar):**
- "[slogan 2]"
- "[slogan 3]"
- "[slogan 4]"

---

## 5. Visuele Identiteit

### Primaire Kleurenpalet

| Kleur | Hex | Gebruik |
|-------|-----|---------|
| [naam] | #XXXXXX | [specifiek gebruik — niet "primary color"] |
| [naam] | #XXXXXX | [specifiek gebruik] |
| [naam] | #XXXXXX | [specifiek gebruik] |

### Uitgebreid Kleurenpalet (limited use — campagnes, varianten)

| Kleur | Hex | Toepassing |
|-------|-----|------------|
| [naam] | #XXXXXX | [wanneer en hoe in te zetten] |
| [naam] | #XXXXXX | [wanneer en hoe in te zetten] |

### Kleurpsychologie
[Waarom deze kleuren — de emotionele en strategische rationale achter de keuzes]

### Typografie

| Gebruik | Font | Karakter |
|---------|------|----------|
| Logo & headlines | [font] | [karakter beschrijving] |
| Subheads | [font] | [karakter beschrijving] |
| Bodytekst | [font] | [karakter beschrijving] |

[Eventuele aanbevelingen voor 2026/komend jaar]

### Logo-systeem (indien van toepassing)

| Variant | Wanneer gebruiken |
|---------|------------------|
| [variant] | [context] |
| [variant] | [context] |

### Fotografie & Visuele Stijl
**Sfeer:** [Concrete beschrijving — belichting, texturen, sfeer, Caribische energie of wellness aesthetic etc.]
**Productshots:** [Hoe het product gefotografeerd moet worden — specifiek]
**Personages:** [Wie in beeld — wanneer en waarom]
**Wat absoluut te vermijden:** [Concrete no-go's]

### Referentiemerken (visuele inspiratie)
- **[merk 1]** — [waarom dit als referentie]
- **[merk 2]** — [waarom dit als referentie]

---

## 6. Concurrentiepositionering

### Competitieflandschap

| Concurrent | Sterk punt | Zwak punt vs. [merknaam] |
|------------|-----------|--------------------------|
| [naam] | [concreet sterk punt] | [concrete zwakte] |
| [naam] | [concreet sterk punt] | [concrete zwakte] |
| [naam] | [concreet sterk punt] | [concrete zwakte] |

### [Merknaam]'s Positionering
[Merknaam] is het enige merk dat:
1. [Uniek punt 1 — iets dat alleen dit merk kan claimen]
2. [Uniek punt 2]
3. [Uniek punt 3]
4. [Uniek punt 4]

**Positioneringsmatrix:** [Beschrijving van waar het merk staat op de relevante assen]

### Strategische Inspiratie
[Het referentiemerk uit een andere categorie + de les die hieruit getrokken wordt voor dit merk]

### Positioneringszin (intern gebruik)
[2-3 zinnen die precies beschrijven wie het merk is, voor wie en waarom — zoals in de SPika manual]

---

## 7. Kanaalgidsen

### [Platform 1 — bijv. Instagram]
**Doel:** [Concreet doel]

**Contentstrategie:**

| Pijler | Frequentie | Toon |
|--------|-----------|------|
| [pijler 1] | [freq] | [toon] |
| [pijler 2] | [freq] | [toon] |
| [pijler 3] | [freq] | [toon] |
| [pijler 4] | [freq] | [toon] |

**Format-mix:** [percentage verdeling — bijv. 60% Reels, 25% carousels, 15% Stories]
**Toon:** [beschrijving van de toon specifiek voor dit platform]

**[Jaar] aanbevelingen:**
- [concrete aanbeveling 1]
- [concrete aanbeveling 2]
- [concrete aanbeveling 3]

### [Platform 2 — bijv. TikTok]
**Doel:** [Concreet doel]
[Zelfde structuur — maar aanpassingen voor TikTok specifiek]

### Overige Kanalen (indien van toepassing)
[E-mail, specialty retail, events, B2B — kort beschreven]

---

## Strategische Aanbevelingen [Jaar]

### 1. [Titel van aanbeveling 1]
[Minimaal 80 woorden uitleg — waarom dit prioriteit heeft, hoe het uitgevoerd wordt en wat het oplevert]

### 2. [Titel van aanbeveling 2]
[Minimaal 80 woorden uitleg]

### 3. [Titel van aanbeveling 3]
[Minimaal 80 woorden uitleg]

---

[Merknaam] Brand Manual [Jaar] — Versie 1.0
Opgesteld op basis van brand interview [maand jaar].
"""

BRAND_DATA_EXTRACT_PROMPT = """
Extraheer gestructureerde data uit deze brand manual voor de database.
Return ALLEEN pure JSON — geen markdown, geen backticks, geen extra tekst.
Start direct met { en eindig met }.

Regels:
- lettertype: geef de exacte fontnaam voor headings (bijv. "Cormorant Garamond")
- platform: geef de platforms als komma-gescheiden tekst (bijv. "Instagram, TikTok")
- primaire_kleur: alleen de hex code (bijv. "#1A1A1A")
- secondaire_kleur: alleen de hex code (bijv. "#D4AF37")
- prijspunt: alleen het getal zonder valutasymbool (bijv. 71.0)

{
  "product_naam": "",
  "product_beschrijving": "",
  "product_type": "",
  "prijspunt": 0,
  "usp": "",
  "primaire_kleur": "",
  "secondaire_kleur": "",
  "lettertype": "",
  "visuele_stijl": "",
  "tone_of_voice": "",
  "categorie": "",
  "platform": "",
  "merkbelofte": "",
  "primaire_slogan": ""
}
"""

# ============================================================
# HELPER FUNCTIES
# ============================================================

def stel_vraag(vraag, nummer, totaal):
    print(f"\n  [{nummer}/{totaal}] {vraag}")
    print("  " + "─" * 55)
    antwoord = input("  > ").strip()
    while not antwoord:
        print("  Antwoord mag niet leeg zijn.")
        antwoord = input("  > ").strip()
    return antwoord


def groq_call(system_prompt, user_message, max_tokens=4000, temperature=0.6):
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        print(f"[Groq] Fout: {e.code} - {e.read().decode()}")
        return None


def genereer_brand_manual(alle_antwoorden):
    print("\n[Agent 0] Brand manual genereren via Groq...")
    print("[Agent 0] Even geduld — dit duurt 30-60 seconden...")

    antwoorden_tekst = json.dumps(alle_antwoorden, ensure_ascii=False, indent=2)

    user_message = (
        "Genereer een volledige professionele brand manual op basis van deze interview antwoorden.\n\n"
        "INTERVIEW ANTWOORDEN:\n" + antwoorden_tekst + "\n\n"
        "KRITIEK: Gebruik de exacte namen, feiten en voorbeelden uit de antwoorden.\n"
        "Volg de verplichte structuur exact.\n"
        "Schrijf minimaal 2000 woorden.\n"
        "De kwaliteit moet gelijk zijn aan een professionele bureau-deliverable."
    )

    manual = groq_call(BRAND_MANUAL_PROMPT, user_message, max_tokens=4000)
    if manual:
        print(f"[Agent 0] Brand manual gegenereerd ({len(manual)} tekens).")
    return manual


def extraheer_brand_data(brand_manual):
    print("[Agent 0] Gestructureerde data extraheren...")
    time.sleep(8)

    output = groq_call(
        BRAND_DATA_EXTRACT_PROMPT,
        f"Extraheer data uit deze brand manual:\n\n{brand_manual[:5000]}",
        max_tokens=800,
        temperature=0.1
    )

    if output:
        try:
            schone = output.replace("```json", "").replace("```", "")
            start = schone.find("{")
            einde = schone.rfind("}") + 1
            if start != -1 and einde > start:
                data = json.loads(schone[start:einde])
                print("[Agent 0] Data succesvol geëxtraheerd.")
                return data
        except json.JSONDecodeError as e:
            print(f"[Agent 0] JSON parse fout: {e}")
    return {}


def sla_op_in_supabase(brand_data, brand_manual, alle_antwoorden, doelland, doeltaal, product_url):
    print("\n[Agent 0] Opslaan in Supabase...")

    prijspunt = brand_data.get("prijspunt", 0)
    try:
        prijspunt = float(str(prijspunt).replace(",", ".").replace("€", "").strip())
    except:
        prijspunt = 0

    record = {
        "product_naam":         brand_data.get("product_naam", ""),
        "product_beschrijving": brand_data.get("product_beschrijving", ""),
        "product_type":         brand_data.get("product_type", "Fysiek product"),
        "prijspunt":            prijspunt,
        "usp":                  brand_data.get("usp", ""),
        "primaire_kleur":       brand_data.get("primaire_kleur", ""),
        "secondaire_kleur":     brand_data.get("secondaire_kleur", ""),
        "lettertype":           brand_data.get("lettertype", ""),
        "visuele_stijl":        brand_data.get("visuele_stijl", ""),
        "tone_of_voice":        brand_data.get("tone_of_voice", ""),
        "categorie":            brand_data.get("categorie", ""),
        "platform":             brand_data.get("platform", "Instagram, TikTok"),
        "doelland":             doelland,
        "doeltaal":             doeltaal,
        "product_url":          product_url,
        "brand_manual":         brand_manual,
        "brandguide":           alle_antwoorden,
        "status":               "Actief",
        "research_gedaan":      False,
        "moodboard_prompts":    None,
        "moodboard_afbeeldingen": None,
        "moodboard_status":     "Nog niet gegenereerd"
    }

    payload = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten",
        data=payload,
        method="POST"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
            product_id = result[0].get("id")
            print(f"[Agent 0] Product opgeslagen — ID: {product_id}")
            return product_id
    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"[Agent 0] Supabase fout: {e.code} - {fout}")
        return None


def exporteer_markdown(product_naam, brand_manual):
    veilige_naam = product_naam.lower()
    for t in [' ', '/', '\\', '|', ':', '*', '?', '"', '<', '>']:
        veilige_naam = veilige_naam.replace(t, '_')
    bestandsnaam = f"brand_manual_{veilige_naam}.md"
    with open(bestandsnaam, "w", encoding="utf-8") as f:
        f.write(brand_manual)
    print(f"[Agent 0] Geëxporteerd: {bestandsnaam}")
    return bestandsnaam




# ============================================================
# PRODUCT REFERENCE PROMPT GENERATOR
# ============================================================

PRODUCT_REFERENCE_PROMPT = """
Je bent een AI video director gespecialiseerd in product visualisatie voor Higgsfield AI.
Je ontvangt product visuele beschrijving en editing stijl informatie uit een brand interview.

Genereer drie dingen:

1. PRODUCT REFERENCE PROMPT
Een gedetailleerde Higgsfield prompt die beschrijft hoe het product er exact uitziet.
Dit wordt bij elke video generatie meegegeven als image_reference context.

2. SOUL ID PERSONA BESCHRIJVING
Beschrijf de ideale AI persona voor UGC video's van dit product.
Gebaseerd op de primaire doelgroep uit de brand manual.
Geen echte persoon — een AI-gegenereerde persona die de doelgroep vertegenwoordigt.

3. EDITING STIJL PROFIEL
Een concreet Higgsfield Cinema Studio profiel met:
- Camera bewegingen
- Cut stijl
- Belichting preset
- Kleurgrading beschrijving
- Muziek richting

Return ALLEEN pure JSON:
{
  "product_naam": "",

  "product_reference": {
    "beschrijving": "",
    "higgsfield_prompt": "",
    "image_reference_url": "",
    "product_details": {
      "kleur": "",
      "vorm": "",
      "materiaal": "",
      "opvallende_kenmerken": ""
    },
    "shot_instructie": "",
    "vermijd": []
  },

  "soul_id_persona": {
    "naam": "",
    "leeftijd": "",
    "uiterlijk": "",
    "stijl": "",
    "expressie": "",
    "higgsfield_portret_prompt": "",
    "gebruik": "Genereer dit portret in Higgsfield Soul en sla op als Soul ID"
  },

  "editing_stijl": {
    "tempo": "",
    "camera_bewegingen": [],
    "cut_stijl": "",
    "belichting": "",
    "kleurgrading": "",
    "muziek_karakter": "",
    "cinema_studio_preset": "",
    "higgsfield_stijl_parameter": ""
  }
}
"""


def genereer_product_reference_en_editing(brand_manual, brand_data, alle_antwoorden):
    """Genereert product reference prompt, Soul ID persona en editing stijl profiel."""
    print("\n[Agent 0] Product reference + editing stijl genereren...")

    product_visueel = alle_antwoorden.get("secties", {}).get("Product Visueel", {})
    editing_stijl   = alle_antwoorden.get("secties", {}).get("Video Editing Stijl", {})
    doelgroep       = alle_antwoorden.get("secties", {}).get("Doelgroepen", {})

    user_message = (
        "Genereer product reference prompt, Soul ID persona en editing stijl profiel.\n\n"
        "PRODUCT VISUEEL:\n" + json.dumps(product_visueel, ensure_ascii=False) + "\n\n"
        "EDITING STIJL:\n" + json.dumps(editing_stijl, ensure_ascii=False) + "\n\n"
        "DOELGROEP (voor Soul ID persona):\n" + json.dumps(doelgroep, ensure_ascii=False) + "\n\n"
        "BRAND DATA:\n" + json.dumps(brand_data, ensure_ascii=False) + "\n\n"
        "Return ALLEEN pure JSON."
    )

    output = groq_call(PRODUCT_REFERENCE_PROMPT, user_message, max_tokens=2000, temperature=0.5)

    if output:
        try:
            schone = output.replace("```json", "").replace("```", "")
            start  = schone.find("{")
            einde  = schone.rfind("}") + 1
            if start != -1 and einde > start:
                data = json.loads(schone[start:einde])
                print("[Agent 0] Product reference + editing stijl gegenereerd.")
                return data
        except json.JSONDecodeError as e:
            print(f"[Agent 0] JSON parse fout: {e}")
    return {}


def sla_product_reference_op_supabase(product_id, ref_data):
    """Slaat product reference, Soul ID en editing stijl op in Supabase."""
    print("\n[Agent 0] Product reference opslaan in Supabase...")

    product_ref  = ref_data.get("product_reference", {})
    soul_persona = ref_data.get("soul_id_persona", {})
    editing      = ref_data.get("editing_stijl", {})

    record = {
        "product_reference_prompt": product_ref.get("higgsfield_prompt", ""),
        "product_image_url":        product_ref.get("image_reference_url", ""),
        "product_reference_volledig": ref_data,
        "soul_id_persona":          soul_persona,
        "editing_stijl":            editing,
        "editing_tempo":            editing.get("tempo", ""),
        "editing_kleurgrading":     editing.get("kleurgrading", ""),
        "muziek_karakter":          editing.get("muziek_karakter", "")
    }

    payload = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?id=eq.{product_id}",
        data=payload, method="PATCH"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req):
            print(f"[Agent 0] Product reference opgeslagen voor ID: {product_id}")
    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"[Agent 0] Supabase fout: {e.code} - {fout}")
        if "column" in fout:
            print("[Agent 0] Voer dit uit in Supabase SQL Editor:")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS product_reference_prompt TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS product_image_url TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS product_reference_volledig JSONB;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS soul_id_persona JSONB;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS soul_id TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS editing_stijl JSONB;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS editing_tempo TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS editing_kleurgrading TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS muziek_karakter TEXT;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS soul_id_portret_url TEXT;")


# ============================================================
# SOUL ID AANMAKEN — via Higgsfield API
# ============================================================

# 20 hoeken voor Soul ID training
SOUL_ID_HOEKEN = [
    ("frontaal neutraal",           "looking directly at camera, neutral expression"),
    ("frontaal lichte glimlach",    "looking directly at camera, slight warm smile"),
    ("frontaal serieus",            "looking directly at camera, serious focused expression"),
    ("frontaal meditief",           "looking directly at camera, calm meditative expression"),
    ("frontaal ogen neer",          "looking slightly downward, peaceful expression"),
    ("3/4 links",                   "three quarter view left, looking slightly left, calm expression"),
    ("3/4 rechts",                  "three quarter view right, looking slightly right, slight smile"),
    ("profiel links",               "side profile left, looking left, elegant posture"),
    ("profiel rechts",              "side profile right, looking right, calm expression"),
    ("lichte hoek omhoog",          "slightly high angle, looking up at camera, open expression"),
    ("lichte hoek omlaag",          "slightly low angle, looking slightly down, confident expression"),
    ("close-up ogen",               "extreme close-up face, eyes looking at camera, calm expression"),
    ("close-up glimlach",           "close-up face, warm genuine smile, eyes slightly crinkled"),
    ("hoofd schuin rechts",         "head tilted slightly right, warm natural expression"),
    ("hoofd schuin links",          "head tilted slightly left, thoughtful expression"),
    ("ogen gesloten",               "eyes gently closed, peaceful meditative expression, slight smile"),
    ("omhoog kijkend",              "looking slightly up and to the right, contemplative expression"),
    ("neer kijkend",                "looking gently downward, serene expression"),
    ("over schouder links",         "over shoulder left, looking back at camera, subtle smile"),
    ("over schouder rechts",        "over shoulder right, looking back at camera, confident expression"),
]


def genereer_soul_id_foto(higgsfield_client, basis_prompt, hoek_beschrijving, hoek_prompt, referentie_job_id=None):
    """Genereert één Soul ID foto via Higgsfield SDK."""
    volledige_prompt = (
        f"{basis_prompt}, {hoek_prompt}, "
        "soft natural window light from the left, clean white background, "
        "shallow depth of field, premium wellness lifestyle aesthetic, "
        "no text, no watermark"
    )

    try:
        args = {
            "prompt": volledige_prompt,
            "quality": "720p",
            "aspect_ratio": "2:3"
        }

        result = higgsfield_client.subscribe(
            "higgsfield-ai/soul/standard",
            arguments=args
        )

        jobs = result.get("jobs", [])
        if jobs:
            results = jobs[0].get("results", {})
            url = (results.get("raw", {}).get("url") or
                   results.get("min", {}).get("url"))
            if url:
                return url

        images = result.get("images", [])
        if images:
            return images[0].get("url", "")

    except Exception as e:
        print(f"  [Soul] Fout bij {hoek_beschrijving}: {str(e)[:100]}")

    return None


def maak_soul_id_aan(soul_persona, product_naam):
    """
    Volledig automatische Soul ID aanmaak:
    1. Genereert basisportret
    2. Genereert 20 variaties vanuit verschillende hoeken
    3. Registreert alle foto's als Soul ID bij Higgsfield
    """
    if not HIGGSFIELD_AUTH:
        print("\n[Agent 0] Higgsfield API key niet ingesteld — Soul ID overgeslagen.")
        return None

    # Importeer higgsfield SDK
    try:
        import higgsfield_client as hf
        import os
        os.environ["HF_API_KEY"]    = HIGGSFIELD_API_ID
        os.environ["HF_API_SECRET"] = HIGGSFIELD_KEY
    except ImportError:
        print("[Agent 0] higgsfield-client niet geïnstalleerd.")
        print("Voer uit: pip install higgsfield-client")
        return None

    portret_prompt = soul_persona.get("higgsfield_portret_prompt", "")
    naam           = soul_persona.get("naam", "Persona")
    leeftijd       = soul_persona.get("leeftijd", "30-35 jaar")
    uiterlijk      = soul_persona.get("uiterlijk", "natural makeup, dark hair pulled back elegantly")
    stijl          = soul_persona.get("stijl", "minimal gold jewelry, wellness lifestyle")

    # Basis beschrijving die bij alle 20 foto's gelijk blijft
    basis_prompt = (
        f"Portrait photo of a {leeftijd} woman, {uiterlijk}, "
        f"{stijl}, same person in every photo"
    )

    print(f"\n[Agent 0] Soul ID aanmaken voor {naam} — 20 foto's genereren...")
    print(f"[Agent 0] Basis prompt: {basis_prompt[:100]}...")

    gegenereerde_urls = []

    for i, (beschrijving, hoek_prompt) in enumerate(SOUL_ID_HOEKEN, 1):
        print(f"[Agent 0] Foto {i}/20 — {beschrijving}...")

        url = genereer_soul_id_foto(hf, basis_prompt, beschrijving, hoek_prompt)

        if url:
            gegenereerde_urls.append({
                "nummer": i,
                "hoek": beschrijving,
                "url": url
            })
            print(f"  ✓ {url[:60]}...")
        else:
            print(f"  ✗ Mislukt — overgeslagen")

        time.sleep(2)  # Rate limit

    print(f"\n[Agent 0] {len(gegenereerde_urls)}/20 foto's gegenereerd.")

    if len(gegenereerde_urls) < 5:
        print("[Agent 0] Te weinig foto's voor Soul ID — minimaal 5 nodig.")
        return {
            "soul_id":    None,
            "foto_urls":  gegenereerde_urls,
            "naam":       naam,
            "instructie": "Upload de gegenereerde foto's handmatig naar higgsfield.ai/soul"
        }

    # Registreer als Soul ID
    print(f"\n[Agent 0] Soul ID registreren met {len(gegenereerde_urls)} foto's...")

    input_images = [
        {"type": "IMAGE_URL", "image_url": foto["url"]}
        for foto in gegenereerde_urls
    ]

    soul_payload = json.dumps({
        "name": f"{naam}_{product_naam.replace(' ', '_')}",
        "input_images": input_images
    }).encode("utf-8")

    soul_req = urllib.request.Request(
        "https://cloud.higgsfield.ai/api/v1/soul-ids",
        data=soul_payload, method="POST"
    )
    soul_req.add_header("Authorization", HIGGSFIELD_AUTH)
    soul_req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(soul_req) as r:
            soul_result = json.loads(r.read().decode())
            soul_id = soul_result.get("id") or soul_result.get("soul_id")
            if soul_id:
                print(f"[Agent 0] ✓ Soul ID aangemaakt: {soul_id}")
                return {
                    "soul_id":   soul_id,
                    "foto_urls": gegenereerde_urls,
                    "naam":      naam
                }
    except urllib.error.HTTPError as e:
        print(f"[Agent 0] Soul ID registratie fout: {e.code} - {e.read().decode()[:200]}")

    # Fallback — sla URLs op voor handmatige upload
    print("[Agent 0] Soul ID registratie mislukt — foto URLs opgeslagen voor handmatige upload.")
    return {
        "soul_id":    None,
        "foto_urls":  gegenereerde_urls,
        "naam":       naam,
        "instructie": f"Upload de {len(gegenereerde_urls)} foto's handmatig naar higgsfield.ai/soul"
    }


def sla_soul_id_op_supabase(product_id, soul_data):
    """Slaat Soul ID op in Supabase producten tabel."""
    if not soul_data:
        return

    print("\n[Agent 0] Soul ID opslaan in Supabase...")

    record = {
        "soul_id": soul_data.get("soul_id", ""),
        "soul_id_portret_url": soul_data.get("portret_url", "")
    }

    payload = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?id=eq.{product_id}",
        data=payload, method="PATCH"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req):
            print(f"[Agent 0] Soul ID opgeslagen: {soul_data.get('soul_id', 'portret URL opgeslagen')}")
    except urllib.error.HTTPError as e:
        print(f"[Agent 0] Soul ID Supabase fout: {e.code}")

# ============================================================
# MOODBOARD GENERATOR — via Higgsfield text-to-image
# ============================================================

MOODBOARD_PROMPT_GENERATOR = """
Je bent een senior AI art director gespecialiseerd in visuele merkidentiteit voor social media.
Je ontvangt een brand manual en genereert daaruit een volledig Higgsfield visueel moodboard pakket.

Het moodboard pakket bestaat uit DRIE LAGEN die samen de volledige visuele identiteit vastleggen:

LAAG 1 — SOUL MOODBOARD REFERENTIEAFBEELDINGEN (10 prompts)
Verdeling van de 10 afbeeldingen:
- 3x product close-up (macro detail, materiaal, textuur van het product zelf)
- 2x lifestyle still life (product in context met props die de merkwaarden uitdrukken)
- 2x textuur en materiaal shots (abstracte texturen die de merksfeer weerspiegelen — marmer, linnen, hout, metaal etc.)
- 2x kleur en compositie shots (kleurvlakken, schaduwen, vormen die de merkkleur dominant tonen)
- 1x ambient mood shot (sfeer, belichting, atmosfeer — geen product, alleen gevoel)

LAAG 2 — SOUL HEX KLEURENPALET
Extraheer de exacte hex codes voor het kleurenpalet uit de brand manual.
Dit wordt direct als Soul HEX parameter meegegeven bij elke Higgsfield generatie.

LAAG 3 — VIBE & TEXTUUR BESCHRIJVING
Een gedetailleerde stijlbeschrijving die de vibe, texturen, belichting en sfeer vastlegt.
Dit wordt gebruikt als master style prompt bij alle video generaties.

VERPLICHTE REGELS VOOR ALLE PROMPTS:
- Schrijf ALLE prompts in het Engels
- Elke prompt: 2-3 zinnen, maximaal 400 tekens
- Verwerk de EXACTE hex kleuren met beschrijvende namen (bijv. "warm gold #D4AF37")
- GEEN gezichten, GEEN mensen, GEEN tekst in beeld
- GEEN stockfoto-vibes — alles moet premium, intentioneel en art-directed aanvoelen
- Elke prompt structuur: [ONDERWERP] + [COMPOSITIE] + [BELICHTING] + [KLEUR/SFEER]
- Gebruik concrete fotografie termen: shallow DOF, rim light, overhead, macro, etc.

Return ALLEEN pure JSON — geen markdown, geen backticks, geen extra tekst:
{
  "product_naam": "",
  "moodboard_naam": "",

  "laag_1_prompts": [
    {
      "nummer": 1,
      "type": "product close-up",
      "beschrijving": "",
      "prompt": ""
    }
  ],

  "laag_2_soul_hex": {
    "primaire_kleur": "#XXXXXX",
    "secondaire_kleur": "#XXXXXX",
    "accent_kleur": "#XXXXXX",
    "achtergrond_kleur": "#XXXXXX",
    "soul_hex_string": "#XXXXXX, #XXXXXX, #XXXXXX, #XXXXXX"
  },

  "laag_3_vibe": {
    "algemene_stijl": "",
    "belichting": "",
    "texturen": "",
    "compositie_stijl": "",
    "sfeer_omschrijving": "",
    "master_style_prompt": "Gebruik dit als master style prompt bij elke Higgsfield video generatie"
  },

  "higgsfield_upload_instructie": "Upload de 10 gegenereerde afbeeldingen naar higgsfield.ai/moodboard voor jouw Soul Moodboard",
  "soul_hex_instructie": "Voeg de soul_hex_string toe als Soul HEX parameter bij elke generatie voor kleurconsistentie"
}
"""

def genereer_moodboard_prompts(brand_manual, brand_data):
    """Genereert 10 moodboard prompts op basis van de brand manual."""
    print("\n[Agent 0] Moodboard prompts genereren...")

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": MOODBOARD_PROMPT_GENERATOR},
            {"role": "user", "content": (
                "Genereer 10 moodboard image prompts voor dit merk.\n\n"
                "BRAND DATA:\n" + json.dumps(brand_data, ensure_ascii=False) + "\n\n"
                "BRAND MANUAL (visuele identiteit sectie):\n" + brand_manual[:3000] + "\n\n"
                "Return ALLEEN pure JSON."
            )}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload, method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
        output = result["choices"][0]["message"]["content"]
        schone = output.replace("```json", "").replace("```", "")
        start = schone.find("{")
        einde = schone.rfind("}") + 1
        if start != -1 and einde > start:
            moodboard_data = json.loads(schone[start:einde])
            print(f"[Agent 0] {len(moodboard_data.get('prompts', []))} moodboard prompts gegenereerd.")
            return moodboard_data
    except Exception as e:
        print(f"[Agent 0] Moodboard prompt fout: {e}")
    return None


def genereer_moodboard_afbeeldingen(moodboard_data):
    """
    Genereert afbeeldingen via Higgsfield text-to-image API.
    Slaat de URLs op voor gebruik als visuele referentie in Agent 4.
    """
    if not HIGGSFIELD_AUTH:
        print("\n[Agent 0] Higgsfield API key niet ingesteld.")
        return []

    print("\n[Agent 0] Moodboard afbeeldingen genereren via Higgsfield...")
    prompts = moodboard_data.get("prompts", [])
    gegenereerde_urls = []

    for i, prompt_item in enumerate(prompts[:10], 1):
        prompt = prompt_item.get("prompt", "")
        print(f"[Agent 0] Afbeelding {i}/10: {prompt_item.get('beschrijving', '')}...")

        payload = json.dumps({
            "model": "bytedance/seedream/v4/text-to-image",
            "arguments": {
                "prompt": prompt,
                "resolution": "1K",
                "aspect_ratio": "1:1",
                "camera_fixed": True
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://cloud.higgsfield.ai/api/v1/subscribe",
            data=payload, method="POST"
        )
        req.add_header("Authorization", HIGGSFIELD_AUTH)
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req) as r:
                result = json.loads(r.read().decode())
                images = result.get("images", [])
                if images:
                    url = images[0].get("url", "")
                    gegenereerde_urls.append({
                        "nummer": i,
                        "beschrijving": prompt_item.get("beschrijving", ""),
                        "prompt": prompt,
                        "url": url
                    })
                    print(f"[Agent 0] ✓ Afbeelding {i} klaar: {url[:60]}...")

        except urllib.error.HTTPError as e:
            print(f"[Agent 0] Higgsfield fout afbeelding {i}: {e.code} - {e.read().decode()[:200]}")

        # Wacht even tussen requests
        if i < len(prompts):
            time.sleep(3)

    print(f"\n[Agent 0] {len(gegenereerde_urls)}/10 moodboard afbeeldingen gegenereerd.")
    return gegenereerde_urls


def sla_moodboard_op_supabase(product_id, moodboard_data, afbeelding_urls):
    """Slaat het volledige moodboard pakket op in Supabase voor gebruik door Agent 4."""
    print("\n[Agent 0] Moodboard opslaan in Supabase...")

    # Extraheer Soul HEX en vibe uit de drie lagen
    soul_hex = moodboard_data.get("laag_2_soul_hex", {})
    vibe     = moodboard_data.get("laag_3_vibe", {})

    moodboard_record = {
        "moodboard_prompts":      moodboard_data.get("laag_1_prompts", []),
        "moodboard_afbeeldingen": afbeelding_urls,
        "moodboard_status":       "Gegenereerd" if afbeelding_urls else "Prompts klaar",
        "soul_hex_kleuren":       soul_hex.get("soul_hex_string", ""),
        "vibe_beschrijving":      vibe.get("master_style_prompt", ""),
        "moodboard_volledig":     moodboard_data
    }

    payload = json.dumps(moodboard_record).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?id=eq.{product_id}",
        data=payload, method="PATCH"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req):
            print(f"[Agent 0] Moodboard opgeslagen voor product ID: {product_id}")
    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"[Agent 0] Moodboard Supabase fout: {e.code} - {fout}")
        # Voeg kolommen toe als ze ontbreken
        if "moodboard" in fout:
            print("[Agent 0] Voer dit uit in Supabase SQL Editor:")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS moodboard_prompts JSONB;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS moodboard_afbeeldingen JSONB;")
            print("ALTER TABLE producten ADD COLUMN IF NOT EXISTS moodboard_status TEXT;")


def exporteer_moodboard_json(product_naam, moodboard_data, afbeelding_urls):
    """Exporteert moodboard als lokaal JSON bestand."""
    veilige_naam = product_naam.lower()
    for t in [' ', '/', '\\', '|', ':', '*', '?', '"', '<', '>']:
        veilige_naam = veilige_naam.replace(t, '_')
    bestandsnaam = f"moodboard_{veilige_naam}.json"

    output = {
        "moodboard_data": moodboard_data,
        "afbeeldingen": afbeelding_urls
    }

    with open(bestandsnaam, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Agent 0] Moodboard geëxporteerd: {bestandsnaam}")
    return bestandsnaam

# ============================================================
# HOOFDPROGRAMMA — BRAND INTERVIEW
# ============================================================


# ============================================================
# STAP 2 — Market Research via Groq (Agent 2)
# ============================================================

AGENT_2_SYSTEM_PROMPT = """
SYSTEM ROLE
You are an AI Product Market Segment & Viral Social Creative Research Agent.
You are a research-and-analysis operator for product marketing and social content strategy.
Your output is used directly by a video script writer (Agent 3) to create short-form video content for Instagram Reels and TikTok.

PRIMARY OBJECTIVE
When given a product, you must:
1. Understand the product deeply.
2. Classify the product into the most likely market segment and subsegment.
3. Infer target audience, core pain points, desires, objections, and buying triggers.
4. Identify short-form video patterns and hooks that work best for this product.
5. Generate 5 concrete video concepts the script writer can use directly.

IMPORTANT PRINCIPLES
- Do not hallucinate specific performance claims.
- If data is missing, say so explicitly.
- Separate facts, interpretation, and hypotheses.
- All output in Dutch unless English performs better for the platform.

STEP 1 — PRODUCT UNDERSTANDING
Determine:
- what the product is and what problem it solves
- what desired outcome it promises
- who is most likely to buy it
- category type: functional / emotional / aspirational / problem-solution / lifestyle / niche

STEP 2 — MARKET SEGMENT CLASSIFICATION
Determine:
- main category, market segment, subsegment
- confidence score 0-100 with short reasoning

STEP 3 — AUDIENCE & BUYER PSYCHOLOGY
Infer:
- primary and secondary audience
- age band, gender relevance
- pain points and frustrations
- emotional and functional buying triggers
- why this audience would stop scrolling
- what would make them watch longer, click, and buy

STEP 4 — CONTENT PATTERNS FOR INSTAGRAM REELS & TIKTOK
Identify:
- top 3 hooks that work for this product type
- dominant visual styles that convert
- best performing emotional angles
- best CTA styles for this product
- underused formats worth testing

STEP 5 — VIDEO CONTENT IDEAS
Create exactly 5 video concepts for this product.
Each concept must be directly usable by a script writer.
Each concept includes:
- titel: short descriptive title
- hook: exact first sentence spoken or shown on screen (max 10 words)
- script_richting: what happens in the video, shot by shot in 2-3 sentences
- format: e.g. productshot / voor-na / testimonial / spokesperson / voice-over
- emotionele_hoek: the core emotion triggered
- cta: exact call to action text
- platform: Instagram Reels / TikTok / both
- confidence: high / medium / low

STEP 6 — UNCERTAINTIES
List any missing data or assumptions made.

OUTPUT RULES
- Return ONLY pure JSON
- No markdown, no code blocks, no extra text outside the JSON
- Start directly with { and end with }

OUTPUT FORMAT
{
  "product_naam": "",
  "product_samenvatting": {
    "kern_belofte": "",
    "aankoop_motivatie": "",
    "categorie_type": ""
  },
  "markt_segment": {
    "hoofd_categorie": "",
    "segment": "",
    "subsegment": "",
    "confidence_score": 0,
    "redenering": ""
  },
  "doelgroep": {
    "primair": "",
    "secundair": "",
    "leeftijd": "",
    "geslacht": "",
    "pijnpunten": [],
    "kooptriggers": [],
    "scroll_stop_factor": "",
    "klik_motivatie": "",
    "koop_motivatie": ""
  },
  "concurrenten": [
    {
      "naam": "",
      "aanpak": "",
      "zwakte": ""
    }
  ],
  "content_patronen": {
    "top_hooks": [],
    "visuele_stijlen": [],
    "emotionele_hoeken": [],
    "cta_stijlen": [],
    "onderbenutte_formats": []
  },
  "video_ideeen": [
    {
      "titel": "",
      "hook": "",
      "script_richting": "",
      "format": "",
      "emotionele_hoek": "",
      "cta": "",
      "platform": "",
      "confidence": ""
    }
  ],
  "aanbevolen_cta": "",
  "toon_advies": "",

  "hook_bibliotheek": [
    {
      "hook_tekst": "",
      "video_type": "",
      "emotie": "",
      "platform": "",
      "waarom_effectief": "",
      "confidence": ""
    }
  ],

  "cta_bibliotheek": [
    {
      "cta_tekst": "",
      "platform": "",
      "video_type": "",
      "conversie_type": "",
      "waarom_effectief": ""
    }
  ],

  "video_format_regels": {
    "ugc": {
      "dos": [],
      "donts": [],
      "toon": "",
      "camera_stijl": "",
      "best_practices": []
    },
    "productshot": {
      "dos": [],
      "donts": [],
      "toon": "",
      "camera_stijl": "",
      "best_practices": []
    },
    "testimonial": {
      "dos": [],
      "donts": [],
      "toon": "",
      "camera_stijl": "",
      "best_practices": []
    },
    "how_to": {
      "dos": [],
      "donts": [],
      "toon": "",
      "camera_stijl": "",
      "best_practices": []
    }
  },

  "onzekerheden": []
}
"""

def voer_market_research_uit(product_data):
    print("\n[Agent 2] Market research starten via Groq...")
    print("[Agent 2] Even geduld...")

    product_tekst = json.dumps(product_data, ensure_ascii=False, indent=2)

    user_message = (
        "Analyseer dit product en lever het volledige research rapport in het gevraagde JSON formaat.\n\n"
        "Productdata:\n" + product_tekst + "\n\n"
        "Platforms: Instagram Reels en TikTok\n"
        "Doel: producten verkopen\n"
        "Output: ALLEEN pure JSON — geen markdown, geen extra tekst"
    )

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": AGENT_2_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Python/3.x groq-client)")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        output_tekst = result["choices"][0]["message"]["content"]

        try:
            start = output_tekst.find("{")
            einde = output_tekst.rfind("}") + 1
            if start != -1 and einde > start:
                rapport = json.loads(output_tekst[start:einde])
                print("\n[Agent 2] JSON succesvol geparsed.")
                return rapport
        except json.JSONDecodeError:
            print("\n[Agent 2] Kon JSON niet parsen — ruwe output:")
            print(output_tekst)
            return output_tekst

    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"Groq API fout: {e.code} - {fout}")
        return None

# ============================================================
# STAP 3 — Script Maker via Groq (Agent 3)
# ============================================================

AGENT_3_SYSTEM_PROMPT = """
SYSTEM ROLE
You are an expert video script writer specialized in 8-second short-form social media videos for TikTok and Instagram Reels.

You receive two or three data blocks:
- Block 1: Brand data from Agent 1 (visual identity, colors, tone)
- Block 2: Market research from Agent 2 (audience, hooks, video concepts)
- Block 3 (optional): Agent 6 performance recommendation

Your job is to write TWO separate 8-second video scripts based on the TOP 2 performing formats from Agent 2.

CRITICAL RULES
- Script 1 format = highest confidence video concept from Agent 2 video_ideeen (or Agent 6 recommendation if available)
- Script 2 format = second highest confidence video concept from Agent 2 video_ideeen
- Video duration: EXACTLY 8 seconds each
- Maximum 3 shots per script
- On-screen text: maximum 5 words per shot
- Visual style always from Agent 1 brand data
- Hook always from Agent 2 top_hooks

OUTPUT RULES
- Return ONLY ONE pure JSON object containing both scripts
- NO markdown backticks, NO code blocks, NO extra text
- Start DIRECTLY with { and end with }
- Both scripts inside ONE JSON object

OUTPUT FORMAT
{
  "product_naam": "",
  "script_1": {
    "format": "",
    "format_bron": "",
    "video_type_motivatie": "",
    "hook": {
      "tekst": "",
      "visueel": "",
      "kleur": ""
    },
    "shots": [
      {
        "tijdstip": "",
        "beeld": "",
        "camerahoek": "",
        "beweging": "",
        "sfeer": "",
        "kleurgebruik": "",
        "onscreen_tekst": ""
      }
    ],
    "cta": {
      "tekst": "",
      "visueel": "",
      "kleur": ""
    },
    "caption": {
      "instagram": "",
      "tiktok": ""
    },
    "muziek_richting": "",
    "video_prompt": ""
  },
  "script_2": {
    "format": "",
    "format_bron": "",
    "video_type_motivatie": "",
    "hook": {
      "tekst": "",
      "visueel": "",
      "kleur": ""
    },
    "shots": [
      {
        "tijdstip": "",
        "beeld": "",
        "camerahoek": "",
        "beweging": "",
        "sfeer": "",
        "kleurgebruik": "",
        "onscreen_tekst": ""
      }
    ],
    "cta": {
      "tekst": "",
      "visueel": "",
      "kleur": ""
    },
    "caption": {
      "instagram": "",
      "tiktok": ""
    },
    "muziek_richting": "",
    "video_prompt": ""
  }
}
"""




# ============================================================
# AGENT 3 — OPHAAL FUNCTIES UIT SUPABASE
# ============================================================

def haal_agent3_context_op(product_id, product_naam):
    """
    Agent 3 haalt zelf alle benodigde context op uit Supabase:
    - Hook bibliotheek (Agent 2)
    - CTA bibliotheek (Agent 2)
    - Video format regels (Agent 2)
    - Verboden content (Agent 0)
    - Merkarchitectuur (Agent 0)
    """
    print("\n[Agent 3] Context ophalen uit Supabase...")

    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?select=hook_bibliotheek,cta_bibliotheek,video_format_regels,brandguide,brand_manual&id=eq.{product_id}",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())

        if not data:
            print("[Agent 3] Geen context gevonden in Supabase.")
            return {}

        velden = data[0]

        # Extraheer verboden content en merkarchitectuur uit brandguide
        brandguide = velden.get("brandguide", {}) or {}
        if isinstance(brandguide, str):
            try:
                brandguide = json.loads(brandguide)
            except:
                brandguide = {}

        secties  = brandguide.get("secties", {}) if isinstance(brandguide, dict) else {}
        verboden = secties.get("Verboden Content & Claims", {})
        merkarch = secties.get("Merkarchitectuur voor AI", {})

        context = {
            "hook_bibliotheek":    velden.get("hook_bibliotheek", []) or [],
            "cta_bibliotheek":     velden.get("cta_bibliotheek", []) or [],
            "video_format_regels": velden.get("video_format_regels", {}) or {},
            "verboden_content":    verboden,
            "merkarchitectuur":    merkarch,
            "brand_manual":        velden.get("brand_manual", "")
        }

        print(f"[Agent 3] Context opgehaald:")
        print(f"  Hooks: {len(context['hook_bibliotheek'])} beschikbaar")
        print(f"  CTAs: {len(context['cta_bibliotheek'])} beschikbaar")
        print(f"  Format regels: {list(context['video_format_regels'].keys()) if context['video_format_regels'] else 'geen'}")
        print(f"  Verboden content: {'ja' if verboden else 'niet ingevuld'}")
        print(f"  Merkarchitectuur: {'ja' if merkarch else 'niet ingevuld'}")

        return context

    except urllib.error.HTTPError as e:
        print(f"[Agent 3] Supabase fout: {e.code}")
        return {}

def voer_script_maker_uit(product_data, research_rapport, agent6_aanbeveling=None):
    print("\n[Agent 3] Script Maker starten via Groq...")
    print("[Agent 3] 2x 8 seconden scripts worden geschreven...")

    brand_tekst = json.dumps(product_data, ensure_ascii=False, indent=2)
    research_tekst = json.dumps(research_rapport, ensure_ascii=False, indent=2)

    # Bouw user message op basis van beschikbaarheid Agent 6 aanbeveling
    if agent6_aanbeveling:
        agent6_tekst = json.dumps(agent6_aanbeveling, ensure_ascii=False, indent=2)
        user_message = (
            "Schrijf TWEE productieklare 8-seconden video scripts.\n\n"
            "SCRIPT 1 — Gebaseerd op Agent 6 performance aanbeveling (wat bewezen werkt voor dit account):\n"
            "Gebruik de agent3_instructie uit Agent 6 als basis voor Script 1.\n\n"
            "SCRIPT 2 — Gebaseerd op Agent 2 marktdata (nieuwe trends in de markt):\n"
            "Gebruik het best scorende video concept uit Agent 2 video_ideeen.\n\n"
            "BLOK 1 — Brand data (Agent 1):\n" + brand_tekst + "\n\n"
            "BLOK 2 — Market research (Agent 2):\n" + research_tekst + "\n\n"
            "BLOK 3 — Agent 6 performance aanbeveling (gebruik voor Script 1):\n" + agent6_tekst + "\n\n"
            "Lever ALLEEN pure JSON output — geen markdown, geen extra tekst."
        )
    else:
        user_message = (
            "Schrijf TWEE productieklare 8-seconden video scripts.\n\n"
            "Geen Agent 6 aanbeveling beschikbaar — gebruik top 2 video concepts uit Agent 2.\n"
            "Script 1 = hoogste confidence video concept uit Agent 2.\n"
            "Script 2 = tweede hoogste confidence video concept uit Agent 2.\n\n"
            "BLOK 1 — Brand data (Agent 1):\n" + brand_tekst + "\n\n"
            "BLOK 2 — Market research (Agent 2):\n" + research_tekst + "\n\n"
            "Lever ALLEEN pure JSON output — geen markdown, geen extra tekst."
        )

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": AGENT_3_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Python/3.x groq-client)")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        output_tekst = result["choices"][0]["message"]["content"]

        try:
            # Strip markdown backticks en code blocks
            schone_tekst = output_tekst
            schone_tekst = schone_tekst.replace("```json", "").replace("```", "")
            start = schone_tekst.find("{")
            einde = schone_tekst.rfind("}") + 1
            if start != -1 and einde > start:
                script = json.loads(schone_tekst[start:einde])
                # Valideer dat beide scripts aanwezig zijn
                if "script_1" in script and "script_2" in script:
                    print("\n[Agent 3] 2 scripts succesvol geparsed.")
                else:
                    print("\n[Agent 3] Waarschuwing: script_1 of script_2 ontbreekt.")
                return script
        except json.JSONDecodeError as e:
            print(f"\n[Agent 3] JSON parse fout: {e}")
            print("Ruwe output:")
            print(output_tekst)
            return None

    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"Groq API fout: {e.code} - {fout}")
        return None

# ============================================================
# STAP 4 — Video Generator via Groq + Kling (Agent 4)
# ============================================================

AGENT_4_SYSTEM_PROMPT = """
SYSTEM ROLE
You are an expert AI video production agent specialized in generating Kling AI prompts.
You receive a complete video script from Agent 3 AND brand data from Agent 1.
Your job is to write ONE single 8-second video prompt that captures the entire video concept.

YOUR JOB
1. Combine all shots from Agent 3 into ONE single cohesive 8-second video prompt
2. Use the brand colors, visual style and product details from Agent 1
3. Write one master prompt that describes the full 8-second video flow
4. Add one voice_over line for the entire video
5. Keep it punchy, visual and brand-accurate

8-SECOND VIDEO PROMPT STRUCTURE
[OPENING SHOT + HOOK ACTION] then [PRODUCT FOCUS + KEY USP] then [CLOSING CTA VISUAL]
Write this as one flowing cinematic description in English.

RULES
- Write in English
- ONE single prompt — NOT multiple clips
- Total duration: exactly 8 seconds
- Reference brand primary color hex explicitly
- Reference brand secondary color hex for accents
- Use the visuele_stijl literally
- Reference the product name and key USP
- Maximum 500 characters
- Be extremely visual and concrete — no abstract words
- End with the CTA visual from Agent 3

VOICE OVER RULES
- One single voice_over line for the entire 8-second video
- Based on the hook tekst from Agent 3
- Maximum 10 words
- Same language as Agent 3 output

KLING PARAMETERS
- model: kling-v1-5
- aspect_ratio: 9:16
- duration: 8
- cfg_scale: 0.7

NEGATIVE PROMPT
"blurry, low quality, watermark, text overlay, cartoon, animation, distorted, unrealistic, bad lighting, overexposed, multiple products, cluttered background, shaky camera, poor composition, wrong colors, inconsistent style"

OUTPUT RULES
- Return ONLY pure JSON
- No markdown, no code blocks, no extra text outside the JSON
- Start directly with { and end with }

OUTPUT FORMAT
{
  "product_naam": "",
  "kling_model": "kling-v1-5",
  "aspect_ratio": "9:16",
  "duratie": 8,
  "cfg_scale": 0.7,
  "kling_prompt": "",
  "voice_over": "",
  "negatieve_prompt": "blurry, low quality, watermark, text overlay, cartoon, animation, distorted, unrealistic, bad lighting, overexposed, multiple products, cluttered background, shaky camera, poor composition, wrong colors, inconsistent style",
  "muziek_richting": "",
  "klaar_voor_kling": true
}
"""

def voer_video_generator_uit(product_data, script):
    print("\n[Agent 4] Video Generator starten via Groq...")
    print("[Agent 4] 8-seconden Kling prompt wordt gegenereerd...")

    brand_tekst = (
        "product_naam: " + product_data.get("product_naam", "") + "\n"
        "primaire_kleur: " + product_data.get("primaire_kleur", "") + "\n"
        "secondaire_kleur: " + product_data.get("secondaire_kleur", "") + "\n"
        "visuele_stijl: " + product_data.get("visuele_stijl", "") + "\n"
        "tone_of_voice: " + product_data.get("tone_of_voice", "") + "\n"
        "usp: " + product_data.get("usp", "")
    )

    script_tekst = json.dumps(script, ensure_ascii=False, indent=2)

    user_message = (
        "Schrijf ONE enkele 8-seconden Kling video prompt op basis van onderstaande data.\n"
        "Combineer alle shots tot een vloeiende 8-seconden video — geen losse clips.\n\n"
        "BRAND DATA (Agent 1):\n" + brand_tekst + "\n\n"
        "VIDEO SCRIPT (Agent 3):\n" + script_tekst + "\n\n"
        "INSTRUCTIES:\n"
        "- Schrijf ONE enkele kling_prompt van 8 seconden totaal\n"
        "- Verwerk de hook, key shots en CTA in een vloeiende beschrijving\n"
        "- Verwerk primaire_kleur en secondaire_kleur expliciet\n"
        "- Verwerk de visuele_stijl letterlijk\n"
        "- Lever ALLEEN pure JSON — geen markdown, geen extra tekst"
    )

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": AGENT_4_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.5,
        "max_tokens": 2000
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Python/3.x groq-client)")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        output_tekst = result["choices"][0]["message"]["content"]

        try:
            start = output_tekst.find("{")
            einde = output_tekst.rfind("}") + 1
            if start != -1 and einde > start:
                kling_params = json.loads(output_tekst[start:einde])
                print("\n[Agent 4] Kling prompt succesvol geparsed.")
                return kling_params
        except json.JSONDecodeError:
            print("\n[Agent 4] Kon JSON niet parsen — ruwe output:")
            print(output_tekst)
            return output_tekst

    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"Groq API fout: {e.code} - {fout}")
        return None


def stuur_naar_kling(kling_params):
    if KLING_API_KEY == "jouw_kling_api_key_hier":
        print("\n[Agent 4] Kling API key nog niet ingesteld.")
        print("[Agent 4] Voeg je Kling API key toe om de video te genereren.")
        return None

    print("\n[Agent 4] Video naar Kling sturen...")

    payload = json.dumps({
        "model": kling_params.get("kling_model", "kling-v1-5"),
        "prompt": kling_params.get("kling_prompt", ""),
        "negative_prompt": kling_params.get("negatieve_prompt", ""),
        "cfg_scale": kling_params.get("cfg_scale", 0.7),
        "aspect_ratio": kling_params.get("aspect_ratio", "9:16"),
        "duration": kling_params.get("duratie", 8)
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.klingai.com/v1/videos/text2video",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {KLING_API_KEY}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"\n[Agent 4] Kling response: {json.dumps(result, indent=2)}")
            return result
    except urllib.error.HTTPError as e:
        fout = e.read().decode()
        print(f"Kling API fout: {e.code} - {fout}")
        return None



# ============================================================
# AGENT 6 AANBEVELING OPHALEN UIT SUPABASE
# ============================================================

def haal_agent6_aanbeveling_op(product_naam):
    """
    Checkt of er een Agent 6 aanbeveling beschikbaar is
    uit de vorige pipeline run. Zo ja — gebruik die voor Script 1.
    """
    print("\n[Agent 3] Checken of Agent 6 aanbeveling beschikbaar is...")

    product_naam_encoded = urllib.parse.quote(product_naam)
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/pipeline_runs?select=*&video_status=eq.Agent6+Aanbeveling&product_naam=eq.{product_naam_encoded}&order=aangemaakt_op.desc&limit=1",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if data:
            aanbeveling = data[0].get("video_script", {})
            print("[Agent 3] Agent 6 aanbeveling gevonden — Script 1 gebaseerd op performance data.")
            return aanbeveling
        else:
            print("[Agent 3] Geen Agent 6 aanbeveling gevonden — beide scripts gebaseerd op Agent 2.")
            return None

    except urllib.error.HTTPError as e:
        print(f"[Agent 3] Supabase fout: {e.code} - {e.read().decode()}")
        return None

# ============================================================
# QUEUE — Haal wachtende productlinks op uit Supabase
# ============================================================

def haal_queue_op():
    """
    Haalt alle productlinks op met status Wachtend
    uit de product_queue tabel in Supabase.
    """
    print("\n[Queue] Wachtende productlinks ophalen uit Supabase...")

    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/product_queue?select=*&status=eq.Wachtend&order=aangemaakt_op.asc",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"[Queue] {len(data)} product(en) gevonden om te verwerken.")
            return data
    except urllib.error.HTTPError as e:
        print(f"[Queue] Supabase fout: {e.code} - {e.read().decode()}")
        return []


def update_queue_status(queue_id, status):
    """
    Update de status van een queue item in Supabase.
    """
    from datetime import datetime
    velden = {
        "status": status,
        "verwerkt_op": datetime.now().isoformat()
    }

    payload = json.dumps(velden).encode("utf-8")

    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/product_queue?id=eq.{queue_id}",
        data=payload,
        method="PATCH"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            print(f"[Queue] Status bijgewerkt naar: {status}")
    except urllib.error.HTTPError as e:
        print(f"[Queue] Status update fout: {e.code} - {e.read().decode()}")


# ============================================================
# HOOFDPROGRAMMA — Verwerk alle wachtende productlinks
# ============================================================




# ============================================================
# HELPER — Haal ALLE actieve producten op
# ============================================================

def haal_alle_actieve_producten():
    """Haalt alle actieve producten op uit Supabase."""
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?select=*&status=eq.Actief&order=id.asc",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"[Pipeline] {len(data)} actief product(en) gevonden.")
            return data
    except urllib.error.HTTPError as e:
        print(f"[Pipeline] Supabase fout: {e.code} - {e.read().decode()}")
        return []


def haal_opgeslagen_research_op(product_id):
    """
    Checkt of er al market research beschikbaar is voor dit product
    in de pipeline_runs tabel. Zo ja — gebruik die, geen nieuwe Agent 2 call nodig.
    """
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/pipeline_runs?select=research_rapport&product_id=eq.{product_id}&order=aangemaakt_op.desc&limit=1",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and data[0].get("research_rapport"):
                rapport = data[0]["research_rapport"]
                if isinstance(rapport, str):
                    rapport = json.loads(rapport)
                print(f"[Agent 2] Bestaande research gevonden — geen nieuwe analyse nodig.")
                return rapport
            return None
    except urllib.error.HTTPError as e:
        return None


def markeer_research_gedaan(product_id):
    """Markeert het product als geanalyseerd door Agent 2."""
    payload = json.dumps({"research_gedaan": True}).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten?id=eq.{product_id}",
        data=payload,
        method="PATCH"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req):
            pass
    except:
        pass

# ============================================================
# DAGELIJKSE CONTENT PIPELINE
# ============================================================

def voer_content_pipeline_uit():
    """
    Dagelijkse content pipeline — draait voor ALLE actieve producten.
    Agent 2 alleen als er nog geen research is voor dat product.
    Agent 3 t/m 5 draaien elke dag voor elk product.
    """

    producten = haal_alle_actieve_producten()

    if not producten:
        print("[Pipeline] Geen actieve producten gevonden.")
        return

    print(f"\n[Pipeline] {len(producten)} product(en) verwerken...")

    for velden in producten:
        brandguide = velden.get("brandguide") or {}
        if isinstance(brandguide, str):
            try:
                brandguide = json.loads(brandguide)
            except:
                brandguide = {}
        if not isinstance(brandguide, dict):
            brandguide = {}

        visueel = brandguide.get("visuele_identiteit") or {}

        # Haal moodboard data op
        moodboard_volledig = velden.get("moodboard_volledig") or {}
        if isinstance(moodboard_volledig, str):
            try:
                moodboard_volledig = json.loads(moodboard_volledig)
            except:
                moodboard_volledig = {}

        soul_hex = (
            velden.get("soul_hex_kleuren") or
            moodboard_volledig.get("laag_2_soul_hex", {}).get("soul_hex_string", "")
        )
        vibe = (
            velden.get("vibe_beschrijving") or
            moodboard_volledig.get("laag_3_vibe", {}).get("master_style_prompt", "")
        )

        product = {
            "product_id":           velden.get("id"),
            "product_naam":         velden.get("product_naam", ""),
            "product_beschrijving": velden.get("product_beschrijving", ""),
            "product_type":         velden.get("product_type", ""),
            "prijspunt":            velden.get("prijspunt", ""),
            "usp":                  velden.get("usp", ""),
            "primaire_kleur":       velden.get("primaire_kleur", "") or (visueel.get("primaire_kleur", {}).get("hex", "") if isinstance(visueel.get("primaire_kleur"), dict) else ""),
            "secondaire_kleur":     velden.get("secondaire_kleur", "") or (visueel.get("secondaire_kleur", {}).get("hex", "") if isinstance(visueel.get("secondaire_kleur"), dict) else ""),
            "lettertype":           velden.get("lettertype", "") or (visueel.get("typografie", {}).get("heading_font", "") if isinstance(visueel.get("typografie"), dict) else ""),
            "visuele_stijl":        velden.get("visuele_stijl", "") or visueel.get("visuele_stijl", ""),
            "tone_of_voice":        velden.get("tone_of_voice", ""),
            "status":               velden.get("status", ""),
            "brandguide":           brandguide,
            "brand_manual":         velden.get("brand_manual", ""),
            "soul_hex_kleuren":           soul_hex,
            "vibe_beschrijving":          vibe,
            "moodboard_id":               velden.get("moodboard_id", ""),
            "product_reference_prompt":   velden.get("product_reference_prompt", ""),
            "product_image_url":          velden.get("product_image_url", ""),
            "soul_id":                    velden.get("soul_id", ""),
            "editing_stijl":              velden.get("editing_stijl", {}),
            "editing_tempo":              velden.get("editing_tempo", ""),
            "editing_kleurgrading":       velden.get("editing_kleurgrading", ""),
            "muziek_karakter":            velden.get("muziek_karakter", "")
        }

        print(f"\n[Pipeline] ── Product: {product['product_naam']} ──")

        # Agent 2 — alleen als nog niet gedaan voor dit product
        product_id = product.get("product_id")
        research_gedaan = velden.get("research_gedaan", False)

        if research_gedaan:
            print(f"[Agent 2] Research al gedaan — ophalen uit Supabase...")
            rapport = haal_opgeslagen_research_op(product_id)
            if not rapport:
                print(f"[Agent 2] Geen opgeslagen research gevonden — toch nieuw onderzoek...")
                rapport = voer_market_research_uit(product)
        else:
            print(f"[Agent 2] Nieuw product — market research starten...")
            rapport = voer_market_research_uit(product)
            if rapport:
                markeer_research_gedaan(product_id)

        if not rapport:
            print(f"[Pipeline] Kon geen research ophalen voor {product['product_naam']} — overslaan.")
            continue

        print("\n[Pipeline] Wachten 30 seconden voor Groq rate limit...")
        time.sleep(30)

        # Check Agent 6 aanbeveling
        agent6_aanbeveling = haal_agent6_aanbeveling_op(product.get("product_naam", ""))

        # Agent 3 — 2x 8 sec scripts
        script = voer_script_maker_uit(product, rapport, agent6_aanbeveling)

        if not script:
            print(f"[Pipeline] Script maken mislukt voor {product['product_naam']} — overslaan.")
            continue

        print("\n" + "=" * 50)
        print(f"OUTPUT AGENT 3 — {product['product_naam']} — 2x VIDEO SCRIPT (8 SEC):")
        print("=" * 50)
        print(json.dumps(script, indent=2, ensure_ascii=False))

        print("\n[Pipeline] Wachten 30 seconden voor Groq rate limit...")
        time.sleep(30)

        # Agent 4
        kling_params = voer_video_generator_uit(product, script)

        if not kling_params:
            print(f"[Pipeline] Video generator mislukt voor {product['product_naam']} — overslaan.")
            continue

        print("\n" + "=" * 50)
        print(f"OUTPUT AGENT 4 — {product['product_naam']} — HIGGSFIELD PROMPTS:")
        print("=" * 50)
        print(json.dumps(kling_params, indent=2, ensure_ascii=False))

        stuur_naar_kling(kling_params)

        # Log pipeline run naar Supabase
        print("\n[Pipeline] Resultaat opslaan in Supabase...")
        log_data = {
            "product_id":       product.get("product_id"),
            "product_naam":     product.get("product_naam", ""),
            "research_rapport": rapport,
            "video_script":     script,
            "kling_prompt":     kling_params.get("kling_prompt", ""),
            "voice_over":       kling_params.get("voice_over", ""),
            "video_url":        kling_params.get("video_url", ""),
            "video_status":     "Gegenereerd"
        }

        log_payload = json.dumps(log_data).encode("utf-8")
        log_req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/pipeline_runs",
            data=log_payload,
            method="POST"
        )
        log_req.add_header("apikey", SUPABASE_KEY)
        log_req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
        log_req.add_header("Content-Type", "application/json")
        log_req.add_header("Prefer", "return=representation")

        try:
            with urllib.request.urlopen(log_req) as log_response:
                log_result = json.loads(log_response.read().decode())
                run_id = log_result[0].get("id")
                print(f"[Pipeline] Run opgeslagen — ID: {run_id}")
        except urllib.error.HTTPError as e:
            print(f"[Pipeline] Supabase log fout: {e.code} - {e.read().decode()}")

        print(f"\n[Pipeline] {product['product_naam']} succesvol verwerkt.")

        # Wacht tussen producten voor rate limit
        if len(producten) > 1:
            print("\n[Pipeline] Wachten 30 seconden voor volgend product...")
            time.sleep(30)

    print("\n" + "=" * 50)
    print("Alle producten verwerkt.")
    print("=" * 50)


# ============================================================
# HOOFDPROGRAMMA
# ============================================================

def voer_agent0_interview_uit():
    """
    Agent 0 — Brand Interview.
    Eenmalig per product uitvoeren via: python volledige_pipeline.py --interview
    """
    print("\n" + "=" * 60)
    print("  AGENT 0 — BRAND INTERVIEW")
    print("  Bouw een professionele brand manual via interview")
    print("=" * 60)

    product_url = input("\n  Productlink (optioneel — Enter om over te slaan): ").strip()
    doelland    = input("  Doelland (bijv. Nederland): ").strip() or "Nederland"
    doeltaal    = input("  Doeltaal (bijv. Nederlands): ").strip() or "Nederlands"

    alle_antwoorden = {
        "doelland": doelland, "doeltaal": doeltaal,
        "product_url": product_url, "secties": {}
    }

    totaal_vragen = sum(len(s["vragen"]) for s in SECTIES)
    vraag_teller  = 0

    for i, sectie in enumerate(SECTIES, 1):
        print(f"\n{'=' * 60}")
        print(f"  SECTIE {i}/{len(SECTIES)} — {sectie['naam'].upper()}")
        print(f"  {sectie['intro']}")
        print("=" * 60)

        sectie_antwoorden = {}
        for vraag in sectie["vragen"]:
            vraag_teller += 1
            sectie_antwoorden[vraag] = stel_vraag(vraag, vraag_teller, totaal_vragen)

        alle_antwoorden["secties"][sectie["naam"]] = sectie_antwoorden
        print(f"\n  ✓ Sectie '{sectie['naam']}' voltooid.")

    print("\n" + "=" * 60)
    bevestiging = input("  Brand manual genereren? (j/n): ").strip().lower()
    if bevestiging != "j":
        return None

    brand_manual = genereer_brand_manual(alle_antwoorden)
    if not brand_manual:
        return None

    print("\n" + "=" * 60)
    print("  BRAND MANUAL PREVIEW:")
    print("=" * 60)
    print(brand_manual[:600] + "\n...")

    time.sleep(8)
    brand_data   = extraheer_brand_data(brand_manual)
    product_naam = brand_data.get("product_naam", "product")

    exporteer_markdown(product_naam, brand_manual)
    product_id = sla_op_in_supabase(
        brand_data, brand_manual, alle_antwoorden,
        doelland, doeltaal, product_url
    )

    # Product reference + editing stijl genereren
    print("\n[Agent 0] Product reference + editing stijl genereren...")
    time.sleep(8)
    ref_data = genereer_product_reference_en_editing(brand_manual, brand_data, alle_antwoorden)
    if ref_data and product_id:
        sla_product_reference_op_supabase(product_id, ref_data)

        # Soul ID automatisch aanmaken
        soul_persona = ref_data.get("soul_id_persona", {})
        if soul_persona:
            print("\n[Agent 0] Soul ID automatisch aanmaken...")
            time.sleep(5)
            soul_data = maak_soul_id_aan(soul_persona, product_naam)
            if soul_data and product_id:
                sla_soul_id_op_supabase(product_id, soul_data)
                if soul_data.get("soul_id"):
                    print(f"\n[Agent 0] ✓ Soul ID actief: {soul_data.get('soul_id')}")
                else:
                    print(f"\n[Agent 0] Portret URL: {soul_data.get('portret_url', '')}")
                    print("[Agent 0] → Registreer handmatig als Soul ID op higgsfield.ai")

    # Moodboard genereren
    print("\n[Agent 0] Moodboard genereren...")
    time.sleep(8)
    moodboard_data = genereer_moodboard_prompts(brand_manual, brand_data)

    afbeelding_urls = []
    if moodboard_data:
        afbeelding_urls = genereer_moodboard_afbeeldingen(moodboard_data)
        exporteer_moodboard_json(product_naam, moodboard_data, afbeelding_urls)
        if product_id:
            sla_moodboard_op_supabase(product_id, moodboard_data, afbeelding_urls)

        print("\n" + "=" * 60)
        print("  MOODBOARD PROMPTS:")
        print("=" * 60)
        for p in moodboard_data.get("prompts", []):
            print(f"  [{p.get('nummer')}] {p.get('beschrijving', '')}")
            print(f"      {p.get('prompt', '')[:100]}...")

    print("\n" + "=" * 60)
    print("  AGENT 0 KLAAR!")
    print(f"  Product: {product_naam} — Supabase ID: {product_id}")
    print(f"  Moodboard: {len(afbeelding_urls)} afbeeldingen")
    print("  Start pipeline: python volledige_pipeline.py")
    print("=" * 60)
    return product_id


if __name__ == "__main__":
    import sys

    # Modus bepalen op basis van argument
    if len(sys.argv) > 1 and sys.argv[1] == "--interview":
        # Agent 0 — Brand interview voor nieuw product
        voer_agent0_interview_uit()
    else:
        # Dagelijkse content pipeline
        print("=" * 60)
        print("AI Content Pipeline — Volledig Automatisch")
        print("Agent 0 (interview) → 2 → 3 → 4 → 5 → 6")
        print("Frequentie: elke 24 uur")
        print("=" * 60)
        print()
        print("TIP: Nieuw product toevoegen?")
        print("     python volledige_pipeline.py --interview")
        print()

        run = 1
        while True:
            print(f"\n[Pipeline] ===== Run #{run} gestart — {datetime.now().strftime('%d-%m-%Y %H:%M')} =====")
            voer_content_pipeline_uit()
            run += 1
            print(f"\n[Pipeline] Run klaar. Volgende run over 24 uur...")
            print("[Pipeline] Druk Ctrl+C om te stoppen.")
            time.sleep(24 * 60 * 60)
