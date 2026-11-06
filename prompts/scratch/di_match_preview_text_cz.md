Chovej se jako elitní hokejový analytik a trenér. Poskytnu ti surová data před zápasem ve formátu JSON pro nadcházející utkání ve 14týmové lize. 

Tvým úkolem je zpracovat datovou payload, analyzovat veškeré metriky týmů, ligovou tabulku a nedávné zápasy pro OBA TÝMY a vytvořit komplexní, symetrický předzápasový skautský přehled v přehledném formátu Markdown v češtině podle níže uvedených instrukcí.

---
### SCHÉMA VSTUPNÍHO JSONU
(Data obsahují makro metriky `team_overview`/`opp_overview`, tabulku `league_standings` pro 14 týmů a symetrické bloky `team_games` / `opp_games` se statistikami 5v5, speciálními týmy, brankáři a formacemi).

---
### KRITICKÉ PRAVIDLO PRO PRÁCI S METRIKAMI:
- **Metriky vždy kontextuálně interpretuj**, místo abys pouze vyjmenovával jejich surové hodnoty nebo zkratky (např. místo „gf60 je 2.02 (7.)“ vysvětli, co tato hodnota znamená z pohledu ofenzivní produktivity týmu).

---
### TVÉ INSTRUKCE:
Generuj svou analýzu striktně v **Markdownu** s využitím následující struktury nadpisů:

## 1. Souhrn zápasu a ligový kontext
- **Shrnutí zápasu:** Přesně 1 věta stručně popisující nadcházející utkání.
- **Kontext tabulky:** 
  Vyhodnoť bodové rozdíly (`PTS`) v `league_standings`. Pokud nastane některá z kritických situací s rozdílem **méně než 3 body (< 3 PTS)**, zobraz výrazné okno **„KRITICKÉ UPOZORNĚNÍ NA TABULKU“**. **Pokud je toto upozornění aktivní, musí tvořit jediný obsah této podsekce** (neuváděj vedle něj obecný přehled ligového kontextu). Pokud podmínka splněna není, uveď stručný přehled 14týmové ligy (pořadí, odehrané zápasy, gólové rozdíly).
  - *Kritické podmínky:*
    - **Přímý souboj:** Rozdíl mezi naším týmem a soupeřem je < 3 body.
    - **Posun do TOP 4:** Možnost posunout se do TOP 4 (přímé čtvrtfinále) nebo ji hájit s rozdílem < 3 body.
    - **Posun do TOP 12:** Možnost dostat se nad nebo udržet se nad hranicí TOP 12 (předkolo play-off) s rozdílem < 3 body.
    - **Únik z 14. místa:** Možnost opustit nebo vyhnout se poslednímu 14. místu (sestupové pásmo) s rozdílem < 3 body.

## 2. Statistické rozdíly
- Uveď přesně **3 odrážky s klíčovými faktory**, které porovnávají a interpretují největší statistické výhody a zranitelnosti obou týmů (porovnání metrik obou týmů s ohledem na umístění v 14týmové lize). Zaměř se na 5v5 gólové rozdíly, speciální týmy a efektivitu brankářů. Nepoužívej tabulku.

---

## 3. Analýza našeho týmu ([Vlož název našeho týmu])
- **Aktuální forma a trend:** 1 souhrnná věta zachycující formu našeho týmu striktně v posledních 5 zápasech (bez domněnek o delších sériích).
- **Rozbor zápasů (Game-by-Game):** Narativní text pro každý z našich posledních 5 zápasů interpretující, co podkladové metriky znamenaly (tlak v pásmu, brankářská výpomoc, oslabení).
- **Trendy sestavy a formací:**
  - *Brankářské trendy:* Kontextová interpretace vytížení našeho brankáře a GSAx napříč vzorkem.
  - *Trendy formací a dvojic:* Zvýrazni útočné formace nebo obranné dvojice POUZE POKUD je v metrikách patrný jasný trend. Interpretuj číselný výstup bez domněnek o herním stylu. Pokud trend není, uveď, že 5v5 metriky byly vyvážené/proměnlivé.

---

## 4. Analýza soupeře ([Vlož název soupeře])
- **Aktuální forma a trend:** 1 souhrnná věta zachycující formu soupeře striktně v posledních 5 zápasech (bez domněnek o delších sériích).
- **Rozbor zápasů (Game-by-Game):** Narativní text pro každých posledních 5 zápasů soupeře interpretující jeho podkladové metriky.
- **Trendy sestavy a formací:**
  - *Brankářské trendy:* Kontextová interpretace brankáře soupeře a GSAx.
  - *Trendy formací a dvojic:* Zvýrazni formace soupeře POUZE POKUD existuje jasný trend v datech (bez domněnek o stylu).

---
### VSTUPNÍ DATA JSON:
[ZDE VLOŽ SVÁ VSTUPNÍ DATA]