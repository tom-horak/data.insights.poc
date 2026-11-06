Generuj svou analýzu striktně v **Markdownu** s využitím následující struktury nadpisů:

## 1. Souhrn zápasu a ligový kontext
- **Shrnutí zápasu:** Přesně 1 věta stručně popisující nadcházející utkání.
- **Kontext tabulky:**
  Pokud je v předpočítaných faktech `standings_alert.active = true`, zobraz výrazné okno **„KRITICKÉ UPOZORNĚNÍ NA TABULKU"** podle důvodů v `standings_alert.reasons`. **Toto upozornění pak musí tvořit jediný obsah této podsekce** (neuváděj vedle něj obecný přehled ligového kontextu). Pokud `active = false`, uveď stručný přehled {{league_teams}}týmové ligy (pořadí, odehrané zápasy, gólové rozdíly).

## 2. Statistické rozdíly
- Uveď přesně **3 odrážky s klíčovými faktory**, které porovnávají a interpretují největší statistické výhody a zranitelnosti obou týmů (porovnání metrik obou týmů s ohledem na umístění v {{league_teams}}týmové lize). Zaměř se na 5v5 gólové rozdíly, speciální týmy a efektivitu brankářů. Nepoužívej tabulku.

---

## 3. Analýza našeho týmu ({{team_name}})
- **Aktuální forma a trend:** 1 souhrnná věta zachycující formu našeho týmu striktně v posledních {{last_n_games}} zápasech (bez domněnek o delších sériích).
- **Rozbor zápasů (Game-by-Game):** Narativní text pro každý z našich posledních {{last_n_games}} zápasů interpretující, co podkladové metriky znamenaly (tlak v pásmu, brankářská výpomoc, oslabení).
- **Trendy sestavy a formací:**
  - *Brankářské trendy:* Kontextová interpretace vytížení našeho brankáře a GSAx napříč vzorkem.
  - *Trendy formací a dvojic:* Zvýrazni útočné formace nebo obranné dvojice POUZE POKUD je v metrikách patrný jasný trend. Interpretuj číselný výstup bez domněnek o herním stylu. Pokud trend není, uveď, že 5v5 metriky byly vyvážené/proměnlivé.

---

## 4. Analýza soupeře ({{opponent_name}})
- **Aktuální forma a trend:** 1 souhrnná věta zachycující formu soupeře striktně v posledních {{last_n_games}} zápasech (bez domněnek o delších sériích).
- **Rozbor zápasů (Game-by-Game):** Narativní text pro každých posledních {{last_n_games}} zápasů soupeře interpretující jeho podkladové metriky.
- **Trendy sestavy a formací:**
  - *Brankářské trendy:* Kontextová interpretace brankáře soupeře a GSAx.
  - *Trendy formací a dvojic:* Zvýrazni formace soupeře POUZE POKUD existuje jasný trend v datech (bez domněnek o stylu).
