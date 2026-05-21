"""
Agent 0 — Brand Interview
Eenmalig per product uitvoeren.
Genereert brand manual, moodboard, Soul ID, product reference en editing stijl.

Gebruik:
  Interactief:  python agent0.py
  Met product ID (vult aan):  python agent0.py --product-id 9
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import time
import os
import base64
import sys
from datetime import datetime

# ============================================================
# CONFIGURATIE
# ============================================================

SUPABASE_URL      = os.environ.get("SUPABASE_URL",      "https://txuzmuhbmvzqotjuffhv.supabase.co")
SUPABASE_KEY      = os.environ.get("SUPABASE_KEY",      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR4dXptdWhibXZ6cW90anVmZmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNDMzMTMsImV4cCI6MjA5MjYxOTMxM30.irLNWt6YIN39bOqCiEosBiXJU5jsycG91d0OX3tRVgg")
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY",      "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")
HIGGSFIELD_KEY    = os.environ.get("HIGGSFIELD_KEY",    "ed9412d969feb6cbe6fedfe22d975b76e6ace49b0db99286e4b8cf9bbbc21bf9")
HIGGSFIELD_API_ID = os.environ.get("HIGGSFIELD_API_ID", "de6f0431-ba49-490d-b2de-40d5bef228f4")

_combined       = f"{HIGGSFIELD_API_ID}:{HIGGSFIELD_KEY}"
HIGGSFIELD_AUTH = f"Basic {base64.b64encode(_combined.encode()).decode()}"

# ============================================================
# INTERVIEW SECTIES & VRAGEN
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
            "Waar staat het merk op een positioneringsmatrix? Kies twee relevante assen en beschrijf de positie.",
            "Is er een merk in een andere categorie dat als strategische inspiratie dient? Waarom is dat relevant?",
            "Schrijf de interne positioneringszin van het merk — 2-3 zinnen."
        ]
    },
    {
        "naam": "Kanaalgidsen & Contentstrategie",
        "intro": "De contentstrategie — per kanaal, per contentpijler en de grote moves voor dit jaar.",
        "vragen": [
            "Op welke platforms is het merk actief of wil het actief zijn? Wat is het primaire doel per platform?",
            "Wat zijn de 4-5 vaste content pijlers? Geef per pijler: naam, frequentie en toon.",
            "Wat is de gewenste format-mix per platform? (bijv. 60% Reels, 25% carousels, 15% Stories)",
            "Zijn er specifieke content formats of rubrieken die bij dit merk passen?",
            "Zijn er andere relevante kanalen naast social media?",
            "Wat zijn de 3 strategische prioriteiten voor het komende jaar?"
        ]
    },
    {
        "naam": "Product Visueel",
        "intro": "Nu leggen we het product visueel vast voor de AI video generator.",
        "vragen": [
            "Wat is de URL van een productafbeelding met hoge resolutie? (directe link naar .jpg of .png)",
            "Beschrijf het product visueel in detail: kleur, vorm, materiaal, verpakking, afmetingen, opvallende kenmerken.",
            "Hoe moet het product in beeld komen? Beschrijf de ideale productshot: hoek, belichting, achtergrond, afstand.",
            "Zijn er specifieke productdetails die altijd zichtbaar moeten zijn in de video?",
            "Wat moet er NOOIT zichtbaar zijn bij het product in een video?"
        ]
    },
    {
        "naam": "Video Editing Stijl",
        "intro": "Nu leggen we de editing stijl vast — hoe de video's worden gemonteerd en gevoeld.",
        "vragen": [
            "Wat is de gewenste snelheid van de video's? (bijv. traag en cinematisch, medium tempo, snel en energiek)",
            "Welke camera bewegingen passen bij het merk? (bijv. langzame zoom, handheld shake, static, push-in)",
            "Wat voor soort cuts passen bij het merk? (bijv. zachte dissolves, harde cuts, jump cuts)",
            "Beschrijf de gewenste belichting en kleurgrading.",
            "Zijn er referentie video's of creators waarvan de editing stijl past? Noem ze.",
            "Wat is het gewenste muziek karakter voor de video's?"
        ]
    },
    {
        "naam": "Verboden Content & Claims",
        "intro": "Nu leggen we vast wat het merk NOOIT mag zeggen of tonen.",
        "vragen": [
            "Welke woorden of uitdrukkingen zijn absoluut verboden voor dit merk?",
            "Welke claims mag het merk juridisch NOOIT maken?",
            "Wat mag er visueel NOOIT getoond worden in video's?",
            "Zijn er specifieke doelgroepen die NIET aangesproken mogen worden?",
            "Zijn er juridische of compliance vereisten waar het merk aan moet voldoen?"
        ]
    },
    {
        "naam": "Merkarchitectuur voor AI",
        "intro": "De AI Brand Constitution — exacte instructies die de AI altijd volgt bij het maken van video's.",
        "vragen": [
            "Wat moet er ALTIJD zichtbaar zijn in elke video van dit merk?",
            "Wat mag er NOOIT zichtbaar zijn in een video van dit merk?",
            "Hoe moet het product ALTIJD gepresenteerd worden?",
            "Welke emotie moet de kijker ALTIJD voelen na het zien van een video?",
            "Als je één zin kon geven aan de AI als instructie voor elke video — wat zou die zin zijn?",
            "Zijn er specifieke locaties of settings die ALTIJD of NOOIT gebruikt mogen worden?"
        ]
    }
]

# ============================================================
# API FUNCTIES — aangeroepen door api.py
# ============================================================

def get_interview_vragen():
    """
    Geeft alle interview secties en vragen terug als gestructureerde
    JSON voor het dashboard. Aangeroepen via GET /agent0/vragen.
    """
    result = []
    for sectie in SECTIES:
        vragen_list = []
        for i, vraag_tekst in enumerate(sectie["vragen"]):
            vragen_list.append({
                "id":          f"v{i + 1}",
                "vraag":       vraag_tekst,
                "type":        "textarea",
                "vereist":     True,
                "placeholder": "Geef een gedetailleerd antwoord…"
            })
        result.append({
            "naam":   sectie["naam"],
            "intro":  sectie["intro"],
            "vragen": vragen_list
        })
    return result


def run_via_api(antwoorden: dict) -> dict:
    """
    Voert Agent 0 volledig uit met antwoorden aangeleverd vanuit het
    dashboard (niet-interactief). Aangeroepen via POST /agent0/uitvoeren.

    Verwacht formaat van antwoorden:
    {
        "doelland":    "Nederland",
        "doeltaal":    "Nederlands",
        "product_url": "https://...",
        "secties": {
            "Merkfundament":           {"v1": "antwoord", ...},
            "Product & Prijsstrategie": {"v1": "antwoord", ...},
            ...
        }
    }
    """
    doelland    = antwoorden.get("doelland",    "Nederland")
    doeltaal    = antwoorden.get("doeltaal",    "Nederlands")
    product_url = antwoorden.get("product_url", "")

    alle_antwoorden = {
        "doelland":    doelland,
        "doeltaal":    doeltaal,
        "product_url": product_url,
        "secties":     antwoorden.get("secties", {})
    }

    # Stap 1 — Brand manual genereren via Groq
    brand_manual = genereer_brand_manual(alle_antwoorden)
    if not brand_manual:
        return {"success": False, "bericht": "Brand manual genereren mislukt (Groq fout)"}

    # Stap 2 — Gestructureerde brand data extraheren
    brand_data   = extraheer_brand_data(brand_manual)
    product_naam = brand_data.get("product_naam", "product")

    # Stap 3 — Exporteer als markdown bestand
    exporteer_markdown(product_naam, brand_manual)

    # Stap 4 — Product reference + Soul ID + editing stijl
    ref_data = genereer_product_reference(brand_manual, brand_data, alle_antwoorden)

    # Stap 5 — Moodboard
    moodboard_data = genereer_moodboard(brand_manual, brand_data)

    # Stap 6 — Alles opslaan in Supabase
    product_id = sla_op_in_supabase(
        brand_data, brand_manual, alle_antwoorden,
        doelland, doeltaal, product_url,
        ref_data, moodboard_data
    )

    if product_id:
        return {
            "success":      True,
            "product_id":   product_id,
            "product_naam": product_naam,
            "bericht":      f"Brand manual succesvol gegenereerd voor '{product_naam}'"
        }

    return {
        "success": False,
        "bericht": "Brand manual gegenereerd maar opslaan in Supabase mislukt"
    }

# ============================================================
# BRAND MANUAL PROMPT
# ============================================================

BRAND_MANUAL_PROMPT = """
Je bent een senior brand strategist met 15+ jaar ervaring bij top-bureaus.
Genereer een volledige, professionele brand manual op basis van de interview antwoorden.
Minimaal 2000 woorden. Bureau-kwaliteit. Gebruik concrete namen en voorbeelden uit de antwoorden.

Structuur:
# [Merknaam] — Brand Manual [Jaar]
## 1. Merkfundament (Oorsprong, Golden Circle, Waarden, Belofte, Persoonlijkheid)
## 2. Product & Prijsstrategie (Beschrijving, Prijspunt, USPs, Productlijn)
## 3. Doelgroepen (Primair, Secundair, Pijnpunten, Kooptriggers)
## 4. Voice & Tone (Stem, Tone per context, Do's & Don'ts, Slogansysteem)
## 5. Visuele Identiteit (Kleuren met hex, Typografie, Fotostijl, Logo-systeem)
## 6. Concurrentiepositionering (Landschap, Positionering, Differentiatie)
## 7. Kanaalgidsen (Per platform, Content pijlers, Format-mix)
## Strategische Aanbevelingen [Jaar]
"""

BRAND_DATA_EXTRACT_PROMPT = """
Extraheer gestructureerde data uit deze brand manual. Return ALLEEN pure JSON.
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

PRODUCT_REFERENCE_PROMPT = """
Je bent een AI video director. Genereer op basis van de interview antwoorden:
1. Product reference prompt voor Higgsfield
2. Soul ID persona beschrijving (primaire doelgroep als AI persona)
3. Editing stijl profiel

Return ALLEEN pure JSON:
{
  "product_reference": {
    "higgsfield_prompt": "",
    "image_reference_url": "",
    "shot_instructie": "",
    "vermijd": []
  },
  "soul_id_persona": {
    "naam": "",
    "leeftijd": "",
    "uiterlijk": "",
    "stijl": "",
    "higgsfield_portret_prompt": ""
  },
  "editing_stijl": {
    "tempo": "",
    "camera_bewegingen": [],
    "cut_stijl": "",
    "belichting": "",
    "kleurgrading": "",
    "muziek_karakter": ""
  }
}
"""

MOODBOARD_PROMPT = """
Je bent een AI art director. Genereer op basis van de brand manual een volledig moodboard pakket.

Return ALLEEN pure JSON:
{
  "product_naam": "",
  "laag_1_prompts": [
    {"nummer": 1, "type": "product close-up", "beschrijving": "", "prompt": ""}
  ],
  "laag_2_soul_hex": {
    "primaire_kleur": "",
    "secondaire_kleur": "",
    "accent_kleur": "",
    "achtergrond_kleur": "",
    "soul_hex_string": ""
  },
  "laag_3_vibe": {
    "algemene_stijl": "",
    "belichting": "",
    "texturen": "",
    "compositie_stijl": "",
    "sfeer_omschrijving": "",
    "master_style_prompt": ""
  }
}
Genereer 10 prompts in laag_1_prompts verdeeld over:
3x product close-up, 2x lifestyle still life, 2x textuur/materiaal, 2x kleur/compositie, 1x ambient mood.
Alle prompts in het Engels.
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
        data=payload, method="POST"
    )
    req.add_header("Authorization", f"Bearer {GROQ_API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        print(f"[Groq] Fout: {e.code} - {e.read().decode()[:300]}")
        return None


def parse_json(output):
    if not output:
        return {}
    try:
        schone = output.replace("```json", "").replace("```", "")
        start  = schone.find("{")
        einde  = schone.rfind("}") + 1
        if start != -1 and einde > start:
            return json.loads(schone[start:einde])
    except json.JSONDecodeError as e:
        print(f"[JSON] Parse fout: {e}")
    return {}


def genereer_brand_manual(alle_antwoorden):
    print("\n[Agent 0] Brand manual genereren via Groq...")
    print("[Agent 0] Even geduld — dit duurt 30-60 seconden...")

    user_message = (
        "Genereer een volledige professionele brand manual op basis van deze interview antwoorden.\n\n"
        "INTERVIEW ANTWOORDEN:\n" + json.dumps(alle_antwoorden, ensure_ascii=False, indent=2) + "\n\n"
        "Gebruik de exacte namen, feiten en voorbeelden. Minimaal 2000 woorden."
    )

    manual = groq_call(BRAND_MANUAL_PROMPT, user_message, max_tokens=4000)
    if manual:
        print(f"[Agent 0] Brand manual gegenereerd ({len(manual)} tekens).")
    return manual


def extraheer_brand_data(brand_manual):
    print("[Agent 0] Gestructureerde data extraheren...")
    time.sleep(5)
    output = groq_call(
        BRAND_DATA_EXTRACT_PROMPT,
        f"Extraheer data uit deze brand manual:\n\n{brand_manual[:4000]}",
        max_tokens=800,
        temperature=0.1
    )
    data = parse_json(output)
    if data:
        print("[Agent 0] ✓ Brand data geëxtraheerd.")
    return data


def genereer_product_reference(brand_manual, brand_data, alle_antwoorden):
    print("[Agent 0] Product reference + Soul ID + editing stijl genereren...")
    time.sleep(5)

    product_visueel = alle_antwoorden.get("secties", {}).get("Product Visueel", {})
    editing         = alle_antwoorden.get("secties", {}).get("Video Editing Stijl", {})
    doelgroep       = alle_antwoorden.get("secties", {}).get("Doelgroepen", {})

    user_message = (
        "Genereer product reference, Soul ID persona en editing stijl.\n\n"
        "PRODUCT VISUEEL:\n" + json.dumps(product_visueel, ensure_ascii=False) + "\n\n"
        "EDITING STIJL:\n" + json.dumps(editing, ensure_ascii=False) + "\n\n"
        "DOELGROEP:\n" + json.dumps(doelgroep, ensure_ascii=False) + "\n\n"
        "BRAND DATA:\n" + json.dumps(brand_data, ensure_ascii=False)
    )

    output = groq_call(PRODUCT_REFERENCE_PROMPT, user_message, max_tokens=2000, temperature=0.5)
    data = parse_json(output)
    if data:
        print("[Agent 0] ✓ Product reference gegenereerd.")
    return data


def genereer_moodboard(brand_manual, brand_data):
    print("[Agent 0] Moodboard genereren...")
    time.sleep(5)

    user_message = (
        "Genereer moodboard pakket voor dit merk.\n\n"
        "BRAND DATA:\n" + json.dumps(brand_data, ensure_ascii=False) + "\n\n"
        "BRAND MANUAL:\n" + brand_manual[:2000]
    )

    output = groq_call(MOODBOARD_PROMPT, user_message, max_tokens=2000, temperature=0.7)
    data = parse_json(output)
    if data:
        print(f"[Agent 0] ✓ Moodboard gegenereerd ({len(data.get('laag_1_prompts', []))} prompts).")
    return data


def exporteer_markdown(product_naam, brand_manual):
    veilige_naam = product_naam.lower()
    for t in [' ', '/', '\\', '|', ':', '*', '?', '"', '<', '>']:
        veilige_naam = veilige_naam.replace(t, '_')
    bestandsnaam = f"brand_manual_{veilige_naam}.md"
    with open(bestandsnaam, "w", encoding="utf-8") as f:
        f.write(brand_manual)
    print(f"[Agent 0] Geëxporteerd: {bestandsnaam}")
    return bestandsnaam


def sla_op_in_supabase(brand_data, brand_manual, alle_antwoorden,
                        doelland, doeltaal, product_url,
                        ref_data=None, moodboard_data=None):
    print("\n[Agent 0] Opslaan in Supabase...")

    prijspunt = brand_data.get("prijspunt", 0)
    try:
        prijspunt = float(str(prijspunt).replace(",", ".").replace("€", "").strip())
    except:
        prijspunt = 0

    soul_hex = ""
    vibe     = ""
    if moodboard_data:
        soul_hex = moodboard_data.get("laag_2_soul_hex", {}).get("soul_hex_string", "")
        vibe     = moodboard_data.get("laag_3_vibe", {}).get("master_style_prompt", "")

    record = {
        "product_naam":             brand_data.get("product_naam", ""),
        "product_beschrijving":     brand_data.get("product_beschrijving", ""),
        "product_type":             brand_data.get("product_type", "Fysiek product"),
        "prijspunt":                prijspunt,
        "usp":                      brand_data.get("usp", ""),
        "primaire_kleur":           brand_data.get("primaire_kleur", ""),
        "secondaire_kleur":         brand_data.get("secondaire_kleur", ""),
        "lettertype":               brand_data.get("lettertype", ""),
        "visuele_stijl":            brand_data.get("visuele_stijl", ""),
        "tone_of_voice":            brand_data.get("tone_of_voice", ""),
        "categorie":                brand_data.get("categorie", ""),
        "platform":                 brand_data.get("platform", "Instagram, TikTok"),
        "doelland":                 doelland,
        "doeltaal":                 doeltaal,
        "product_url":              product_url,
        "brand_manual":             brand_manual,
        "brandguide":               alle_antwoorden,
        "status":                   "Actief",
        "research_gedaan":          False,
        "moodboard_prompts":        moodboard_data.get("laag_1_prompts") if moodboard_data else None,
        "moodboard_volledig":       moodboard_data if moodboard_data else None,
        "moodboard_status":         "Prompts klaar" if moodboard_data else "Nog niet gegenereerd",
        "soul_hex_kleuren":         soul_hex,
        "vibe_beschrijving":        vibe,
        "product_reference_prompt": ref_data.get("product_reference", {}).get("higgsfield_prompt", "") if ref_data else "",
        "product_image_url":        ref_data.get("product_reference", {}).get("image_reference_url", "") if ref_data else "",
        "soul_id_persona":          ref_data.get("soul_id_persona") if ref_data else None,
        "editing_stijl":            ref_data.get("editing_stijl") if ref_data else None,
        "editing_tempo":            ref_data.get("editing_stijl", {}).get("tempo", "") if ref_data else "",
        "editing_kleurgrading":     ref_data.get("editing_stijl", {}).get("kleurgrading", "") if ref_data else "",
        "muziek_karakter":          ref_data.get("editing_stijl", {}).get("muziek_karakter", "") if ref_data else "",
    }

    payload = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/producten",
        data=payload, method="POST"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read().decode())
            product_id = result[0].get("id")
            print(f"[Agent 0] ✓ Product opgeslagen — ID: {product_id}")
            return product_id
    except urllib.error.HTTPError as e:
        print(f"[Agent 0] Supabase fout: {e.code} - {e.read().decode()[:300]}")
        return None


# ============================================================
# HOOFDPROGRAMMA — BRAND INTERVIEW
# ============================================================

def run():
    print("\n" + "=" * 60)
    print("  AGENT 0 — BRAND INTERVIEW")
    print("  Bouw een professionele brand manual via interview")
    print("=" * 60)

    product_url = input("\n  Productlink (optioneel — druk Enter om over te slaan): ").strip()
    doelland    = input("  Doelland (bijv. Nederland): ").strip() or "Nederland"
    doeltaal    = input("  Doeltaal (bijv. Nederlands): ").strip() or "Nederlands"

    alle_antwoorden = {
        "doelland":    doelland,
        "doeltaal":    doeltaal,
        "product_url": product_url,
        "secties":     {}
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
        print("  Gestopt.")
        return

    # Stap 1 — Brand manual
    brand_manual = genereer_brand_manual(alle_antwoorden)
    if not brand_manual:
        print("[Agent 0] Fout bij genereren brand manual.")
        return

    # Stap 2 — Brand data extraheren
    brand_data   = extraheer_brand_data(brand_manual)
    product_naam = brand_data.get("product_naam", "product")

    # Stap 3 — Exporteer markdown
    exporteer_markdown(product_naam, brand_manual)

    # Stap 4 — Product reference + editing stijl + Soul ID
    ref_data = genereer_product_reference(brand_manual, brand_data, alle_antwoorden)

    # Stap 5 — Moodboard
    moodboard_data = genereer_moodboard(brand_manual, brand_data)

    # Stap 6 — Sla alles op in Supabase
    product_id = sla_op_in_supabase(
        brand_data, brand_manual, alle_antwoorden,
        doelland, doeltaal, product_url,
        ref_data, moodboard_data
    )

    print("\n" + "=" * 60)
    print("  AGENT 0 KLAAR!")
    print(f"  Product: {product_naam}")
    print(f"  Supabase ID: {product_id}")
    print("  Brand manual: lokaal .md bestand + Supabase")
    print("  Moodboard: prompts opgeslagen in Supabase")
    print("  Volgende stap: agent2.py uitvoeren voor marktonderzoek")
    print("=" * 60)

    return product_id


if __name__ == "__main__":
    run()
