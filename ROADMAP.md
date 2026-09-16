# MultiRoleWorkIsland — roadmap

## 1. Cíl projektu

MultiRoleWorkIsland je třístranný pracovní, prezentační, výukový a společenský ostrov. Tři pracoviště A/B/C jsou rozmístěna po 120°. Každé má samostatně polohovatelné plochy Primary, Secondary a Tertiary (P/S/T), vlastní trojici monitorů a lokální řízení. Sdílená ramena a centrální část se mohou překrýt druhou souvislou vrstvou party desek.

Projekt zahrnuje nábytek, nosnou konstrukci, pohony, bezpečnost, kabeláž, elektroniku, řízení os, HMI, směrování obrazu a vstupů i software pro scénáře. Současný CAD je prostorová studie, nikoliv výrobní dokumentace.

Pracovní název projektu a repozitáře: **MultiRoleWorkIsland**.

## 2. Dosud přijatá rozhodnutí

### Geometrie a ergonomie

- Tři pracoviště A/B/C po 120° a tři společná ramena.
- Devět nezávislých pracovních ploch: PA/SA/TA, PB/SB/TB a PC/SC/TC.
- Původní prostorová obálka ramene 1500 × 1600 mm zůstává zatím limitem, nikoliv definitivním tvarem pracovní desky.
- Technický kanál mezi sousedními plochami na rameni má pracovní hodnotu 400 mm; musí se ověřit podle monitorových liftů, konstrukce a kabelových řetězů.
- Čelní hrana pracoviště směrem k uživateli má mít přibližně 800 mm.
- Užitná hloubka před monitorem má být 500–600 mm; výchozí parametr další studie je 550 mm.
- P/S/T desky se nesmějí půdorysně překrývat. Jejich tvar se má odvodit od polohy uživatele, monitoru, ergonomické hloubky a hran sousedních pracovišť, nikoliv z pevných obdélníků.
- Centrální party útvar má trojnásobnou symetrii, ale nemá být pravidelným šestiúhelníkem. Tři hlavní hrany orientované k uživatelům mají přibližně 800 mm; zbývající hrany vzniknou z návaznosti desek.
- Primární monitory tvoří trojúhelník uprostřed. Sekundární a terciární monitor každého pracoviště se orientují k jeho uživateli; nemají být pouze kolmé k ose ramene.
- Devět monitorů se parkuje pod pracovní vrstvu. Dvojice bočních monitorů sousedních pracovišť leží zády k sobě kolem technického kanálu.
- Zadní zvýšené hrany pracovních desek mají bránit pádu předmětů při změně výšky.

### Výšky a režimy

- Party výška: 700 mm.
- Aktuální CAD používá pracovní výšku 750 mm a provizorní servisní výšku 1200 mm.
- Dříve uvažované ergonomické rozsahy přibližně 650–1250 nebo 680–1280 mm je nutné sjednotit s reálně vybranými zdvihy.
- Hodnoty fyzického zdvihu 300–2000 mm a softwarového posunu na 700–2400 mm v prvních skriptech jsou simulační obálkou, nikoliv schválenou výrobní specifikací.
- Cílové zatížení jedné řízené jednotky bylo uvažováno až přibližně 200 kg; musí být rozděleno na dynamické, statické a bezpečnostní zatížení a potvrzeno výpočtem.

### Party vrstva

- Party režim není pouze sada úzkých spojovacích pásů.
- Druhá sada desek musí vytvořit souvislou horní vrstvu a kompletně překrýt pracovní desky, zaparkované monitory i technické mezery.
- Ramenní party desky mohou být v pracovním/hybridním režimu postavené jako vertikální přepážky.
- Centrální kryt překrývá trojúhelník primárních monitorů.
- Party transformace vyžaduje zarovnání dotčených pracovních ploch na 700 mm, zaparkování monitorů, přestavení desek a mechanické zajištění.

### Režimy použití

1. **Full Work** — všechna tři pracoviště samostatná, monitory vysunuté, party desky uložené nebo jako přepážky.
2. **Hybrid Work** — vybrané primární monitory aktivní, party desky mohou oddělovat pracovní skupiny.
3. **Shared Work / Three Users** — řízené sdílení zobrazovačů a vstupů mezi stanicemi.
4. **Training / Simulation / Seminar** — třetí stanice může být instruktorská; obsah a vstupy se řídí podle týmů, přepážky mohou zajišťovat izolaci.
5. **Presentation** — definovaná topologie obrazovek, vstupů, zvuku, světel a poloh.
6. **Full Party** — monitory zaparkované, pracovní vrstva zakrytá souvislou party vrstvou ve výšce 700 mm.
7. **Service** — přístup k mechanismům; jednotlivé stanice mohou do servisu vstupovat samostatně za splnění blokovacích podmínek.

## 3. Řídicí architektura

### Hierarchie

- Čtyři koordinační uzly: Workstation A, Workstation B, Workstation C a Central Coordinator.
- Devět lokálních řízení os: PA/SA/TA, PB/SB/TB, PC/SC/TC.
- Pokud jednu desku pohání dva aktuátory, jejich synchronizace patří do jejího lokálního axis controlleru.
- Preferované samostatné řízení party mechanismů: PARTY_AB, PARTY_BC, PARTY_CA a CENTRAL_TOP.
- Každá osa smí mít v jednom okamžiku právě jednoho vlastníka. Lokální a centrální koordinátor ji nesmějí ovládat současně.
- Při party transformaci Central Coordinator dočasně převezme potřebné osy sousedních pracovišť.
- Service je primárně lokální stav pracoviště; Party je sdílený stav řízený centrálně.

### Priorita řízení

1. bezpečnost,
2. Primary,
3. Secondary,
4. Tertiary,
5. estetické zarovnání.

Režim „follow primary“ pro S/T je volitelný. Porucha následovníka nesmí sama o sobě zablokovat bezpečný pohyb P. Servisní synchronizace je přísnější; pokud nelze garantovat synchronní pohyb mezi regulátory, přechází se do Service pouze z definovaného stavu Work.

### Stavový model

Minimální referenční stavy:

- `HOME`
- `WORK`
- `PARTY`
- `SERVICE`
- `MONITOR_PARK`
- `FAULT`
- `ESTOP`

Přechody musí být explicitní procedury s předpodmínkami, kontrolou senzorů, časovými limity, možností bezpečného zastavení a diagnostickým důvodem odmítnutí.

## 4. Bezpečnostní invarianty

- E-STOP, koncové spínače, ochrana proti sevření a základní bezpečnost nesmějí záviset na Raspberry Pi, GUI ani síťové službě.
- Service je povolen pouze s party deskami v poloze Work/uloženo a se všemi dotčenými monitory potvrzenými v parkovací poloze.
- Pohyb desky je blokován, pokud její mechanický zámek není ve stavu požadovaném danou procedurou.
- Ruční manipulace s party deskou: odemknout výchozí polohu → přemístit/překlopit → zamknout cílovou polohu → potvrdit. Koordinátor samostatně ověřuje polohu i zámek koncovými spínači.
- HMI nesmí pokračovat k dalšímu kroku, dokud nejsou splněny interlocky.
- Před transformací se kontroluje přítomnost osob a předmětů, poloha monitorů, výšky dotčených desek a stav zámků.
- Musí existovat definovaný bezpečný mezistav a postup obnovy po výpadku napájení, komunikace nebo senzoru.
- Bezpečnostní analýza musí pokrýt sevření, střih, převrácení, kolizi os, pád desky, přetížení, uvolněný zámek, přerušený kabel a neočekávaný restart.

## 5. Softwarová architektura

Software se dělí na tři nezávislé roviny spojené scénickým enginem:

### Mechanical plane

- řízení os, monitorových liftů, party mechanismů a zámků,
- snímání poloh, proudů/zatížení, koncových spínačů a bezpečnostních stavů,
- vlastnictví os, stavové automaty, interlocky, diagnostika a audit událostí,
- lokální realtime řízení v MCU/PLC; vyšší koordinace nad ním.

### Display plane

- směrování DP/HDMI nebo AV-over-IP,
- správa EDID a stabilní identity monitorů,
- scény pro Work, Code+Test, Three Users, Presentation, Training a Service,
- možnost zobrazit odlišný obsah jednotlivým týmům nebo instruktorský náhled.

### Input plane

- směrování klávesnice, myši, dotyku a dalších HID mezi hostiteli,
- virtuální HID na jednotlivých počítačích,
- globální kurzor nebo řízený přechod mezi hostiteli,
- klávesnice následuje aktivní fokus; myš může následovat hostitele pod globálním kurzorem,
- časově kritické HID funkce mají běžet na MCU nebo specializované vrstvě, ne pouze v GUI.

### Scene engine a API

- Orchestrátor skládá mechanickou polohu, topologii obrazu, vstupy, USB, zvuk, osvětlení a napájení do verzovaných scén.
- HMI posílá záměry typu `request_mode(PARTY_AB)`, nikoliv přímé PWM nebo povely jednotlivým motorům.
- Každý požadavek vrací přijat/odmítnut, důvod, průběh procedury a výsledný stav.
- Konfigurace hardwaru, limity, kalibrace a scény musí být oddělené od programu a verzované.
- Události a chyby se logují monotónním časem i reálným časem; log nesmí obsahovat citlivý obsah obrazovek ani stisknuté klávesy.

### HMI

- Čtyři fyzická místa ovládání: lokální A/B/C a centrální.
- Jednoduchý tlačítkový panel může obsluhovat bezpečné základní funkce.
- Raspberry Pi s dotykovým displejem může zobrazovat profily, diagnostiku, stavový diagram a krokové instrukce pro ruční úkony.
- Lokální HMI může obsahovat lokální i centrální funkce, ale oprávnění a vlastnictví os musí zůstat jednoznačné.
- Nouzové zastavení musí být fyzické a nezávislé na dotykovém rozhraní.

## 6. Kabeláž, data a technické zázemí

- Každá nezávisle pohyblivá část má vlastní kabelový svazek vedený energetickým řetězem.
- Nevézt kabel přímo mezi dvěma nezávisle pohyblivými deskami.
- Ethernet je preferovaná komunikační páteř.
- Video řešit krátkým lokálním DP/HDMI, kabelem určeným pro trvalý ohyb nebo AV-over-IP; běžný HDMI kabel není vhodný pro opakované ostré ohýbání.
- Oddělit silové vedení, bezpečnostní signály a vysokorychlostní data.
- Navrhnout servisní smyčky, konektory, odlehčení tahu, zemnění, ochranu proti rušení a výměnu modulu bez rozebrání celého ostrova.
- Prověřit centrální IT/rack prostor, ventilaci, napájení, UPS, síťové prvky a přístup v režimu Service.

## 7. Doporučená struktura repozitáře

```text
MultiRoleWorkIsland/
├── README.md
├── ROADMAP.md
├── LICENSES/
├── cad/
│   ├── generators/
│   ├── models/
│   ├── exports/
│   └── drawings/
├── mechanics/
│   ├── calculations/
│   ├── actuators/
│   ├── safety/
│   └── bom/
├── electronics/
│   ├── schematics/
│   ├── pcb/
│   └── wiring/
├── firmware/
│   ├── axis-controller/
│   ├── safety-io/
│   └── party-controller/
├── software/
│   ├── coordinator/
│   ├── scene-engine/
│   ├── display-router/
│   ├── input-router/
│   ├── hmi/
│   └── simulator/
├── config/
│   ├── hardware/
│   ├── limits/
│   └── scenes/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── hil/
│   └── safety/
├── tools/
│   └── run_freecad.sh
└── docs/
    ├── architecture/
    ├── procedures/
    ├── risk-analysis/
    └── media/
```

Generované FCStd/STEP soubory mohou být vydávané jako artefakty buildu nebo releasu. Do Gitu je vhodné ukládat především zdrojový generátor, ručně udržované modely a výkresy; politika pro velké binární CAD soubory se musí rozhodnout dříve, než historie repozitáře naroste.

## 8. Vývojové milníky

### M0 — Repozitář a reprodukovatelný CAD build

- [x] Založit Git repozitář.
- [x] Uchovat V1/V2 jako historické prostorové studie.
- [x] Přidat shellový runner pro FreeCADCmd a kontrolu výstupů.
- [ ] Uspořádat adresáře a přesunout generátor bez přerušení buildu. *(Přesun proveden; čeká ověření reálným FreeCADCmd.)*
- [ ] Přidat `.gitignore` pro logy, cache a lokální buildy.
- [ ] Zapsat podporované verze FreeCADu, Pythonu a OpenCascade.
- [ ] Přidat CI smoke test: spuštění generátoru, neprázdný FCStd/STEP, počet očekávaných objektů.

**Hotovo, když:** čistý checkout vytvoří stejným příkazem model a oba STEP snapshoty.

### M1 — Ergonomický půdorys V2.1

- [ ] Nahradit pravidelný centrální šestiúhelník trojnásobně symetrickým nepravidelným obrysem.
- [ ] Parametrizovat čelo 800 mm a pracovní hloubku 500–600 mm, výchozí 550 mm.
- [ ] Odvodit P/S/T desky z ergonomických hran a odstranit všechny půdorysné překryvy.
- [ ] Natočit S/T monitory k uživateli; ověřit zorné úhly, vzdálenost a vzájemné zakrytí.
- [ ] Dopočítat tvar a rozměry S/T místo použití pevné šířky 600 mm.
- [ ] Doplnit 2D kótovaný půdorys a parametrické kontrolní rozměry.
- [ ] Ověřit polohy židlí, prostor pro nohy, vstup a opuštění pracoviště.

**Hotovo, když:** žádné dvě pracovní desky se neprotínají, každý uživatel má 500–600 mm použitelné hloubky a všechny tři monitory jsou ergonomicky orientované.

### M2 — Souvislá party vrstva a kinematika

- [ ] Navrhnout kompletní druhou sadu horních desek překrývající pracovní vrstvu, monitory a mezery.
- [ ] Rozdělit horní vrstvu na tři ramenní moduly a centrální modul s realizovatelnými spárami.
- [ ] Navrhnout uložení party desek v režimech Work/Hybrid.
- [ ] Prověřit lift → rotate → lower sekvence a přesné pohybové obálky, nikoliv pouze bounding boxy.
- [ ] Navrhnout panty, vedení a ruční nebo motorické přestavení.
- [ ] Umístit mechanické zámky a dvojici potvrzení POSITION/LOCK.
- [ ] Prověřit, zda se celý party povrch bezpečně zarovná na 700 mm.

**Hotovo, když:** CAD přehraje bezkolizní posloupnost Work ↔ Party a horní vrstva vytvoří souvislý použitelný povrch.

### M3 — Konstrukce, zdvihy a servis

- [ ] Vybrat konstrukční princip rámu a materiál desek.
- [ ] Rozdělit cílové zatížení a provést statický, dynamický a stabilitní výpočet.
- [ ] Vybrat zdvihové sloupy/aktuátory s programovatelnými limity a kalibrací.
- [ ] Rozhodnout skutečný pracovní a servisní rozsah; odstranit simulační rozsah 700–2400 mm.
- [ ] Ověřit zdvih se dvěma aktuátory, synchronizaci a reakci na zkřížení.
- [ ] Prověřit kolize základen, nohou, židlí, sloupů a centrální konstrukce.
- [ ] Navrhnout servisní přístup, modulární výměnu pohonů a ruční nouzové spuštění.

**Hotovo, když:** existuje dimenzovaný konstrukční koncept, seznam kandidátních pohonů a ověřená servisní poloha.

### M4 — Jedna osa a bezpečnostní lavice

- [ ] Postavit test jedné desky s reálným pohonem, snímáním polohy a koncovými spínači.
- [ ] Implementovat lokální axis controller a kalibraci.
- [ ] Ověřit proudovou/přetěžovací ochranu a detekci překážky.
- [ ] Ověřit E-STOP, ztrátu komunikace, restart, výpadek senzoru a výpadek napájení.
- [ ] Změřit rychlost, hlučnost, přesnost, opakovatelnost, drift a zahřívání.
- [ ] Stanovit bezpečnou brzdnou vzdálenost a časové limity.

**Hotovo, když:** jedna osa projde opakovaným zatěžovacím a poruchovým testem bez závislosti bezpečnosti na vyšším softwaru.

### M5 — Jedno kompletní pracoviště

- [ ] Integrovat P/S/T, tři monitorové lifty a lokální Workstation Coordinator.
- [ ] Implementovat exkluzivní vlastnictví os a volitelný `follow primary`.
- [ ] Ověřit, že porucha S/T neblokuje bezpečný pohyb P.
- [ ] Implementovat lokální Work a Service procedury.
- [ ] Vyrobit kabelové svazky a energetické řetězy pro každou pohyblivou část.
- [ ] Ověřit ergonomii na uživatelích různých výšek.

**Hotovo, když:** stanice pracuje samostatně, bezpečně přejde Work ↔ Service a poskytuje úplnou diagnostiku.

### M6 — Sdílené rameno a party mechanismus

- [ ] Spojit dvě sousední stanice jedním fyzickým ramenem.
- [ ] Implementovat PARTY_AB jako první sdílený modul.
- [ ] Ověřit dočasné převzetí os Central Coordinator-em.
- [ ] Ověřit mechanické zámky, koncové spínače a krokovou ruční proceduru.
- [ ] Otestovat rozdílné výšky sousedních pracovišť a odmítnuté transformace.
- [ ] Ověřit technický kanál 400 mm s reálnými lifty a kabeláží.

**Hotovo, když:** jedno rameno bezpečně přechází mezi Work/Hybrid/Party a chybné podmínky vedou k vysvětlenému odmítnutí.

### M7 — Kompletní mechanický ostrov

- [ ] Integrovat A/B/C, tři ramena a centrální party modul.
- [ ] Implementovat Full Work, Hybrid, Full Party a Service.
- [ ] Ověřit stabilitu a kolize ve všech kombinacích povolených stavů.
- [ ] Provést kabeláž, napájení, zemnění, ventilaci a centrální technický prostor.
- [ ] Doplnit fyzické E-STOP prvky dostupné ze všech stran.

**Hotovo, když:** celý ostrov mechanicky provede všechny podporované transformace a bezpečně se zastaví při každé simulované poruše.

### M8 — Display/Input platforma a scene engine

- [ ] Zvolit DP/HDMI matrix versus AV-over-IP a otestovat EDID/hotplug chování.
- [ ] Implementovat stabilní mapování devíti displejů a hostitelských počítačů.
- [ ] Prototypovat Input plane: RPi + evdev/uinput + tři MCU/Pico nebo ekvivalentní architektura.
- [ ] Implementovat virtuální HID a řízené předávání fokusu.
- [ ] Implementovat scene engine a verzovaný formát scén.
- [ ] Propojit mechanické stavy s obrazem, vstupy, zvukem, světly, USB a napájením.
- [ ] Otestovat Work, Code+Test, Three Users, Presentation, Training a Service scény.

**Hotovo, když:** jedna atomická scéna bezpečně nastaví podporovanou mechanickou polohu i digitální topologii a umí se vrátit do známého stavu.

### M9 — HMI a provozní postupy

- [ ] Navrhnout tlačítkové lokální panely A/B/C a centrální panel.
- [ ] Implementovat dotykové HMI pro profily, diagnostiku a krokové instrukce.
- [ ] Zobrazit aktuálního vlastníka osy, blokující podmínku a bezpečný další krok.
- [ ] Vytvořit průvodce ručním odemknutím/překlopením/zamknutím party desky.
- [ ] Oddělit běžné, servisní a administrátorské operace.
- [ ] Doplnit audit změn konfigurace a export diagnostického balíčku bez záznamu citlivých vstupů.

**Hotovo, když:** uživatel provede běžné režimy bez znalosti vnitřní architektury a technik dostane jednoznačnou diagnostiku.

### M10 — Validace, dokumentace a výroba

- [ ] Zpracovat formální analýzu rizik a bezpečnostní požadavky podle cílového způsobu uvedení do provozu.
- [ ] Provést dlouhodobé cyklické testy všech pohybových mechanismů.
- [ ] Ověřit EMC, elektrickou ochranu, teploty, hlučnost a požární rizika.
- [ ] Dokončit výrobní CAD, výkresy, tolerance, kusovník a montážní přípravky.
- [ ] Vytvořit instalační, kalibrační, provozní a servisní dokumentaci.
- [ ] Zavést verzování hardwarových revizí, firmwaru, konfigurace a kalibrace.
- [ ] Rozhodnout licenční strategii zvlášť pro software, elektroniku, CAD a dokumentaci.

**Hotovo, když:** dokumentace umožní sestavit, oživit, otestovat, provozovat a servisovat konkrétní hardwarovou revizi.

## 9. Testovací strategie

- **Unit tests:** stavové automaty, geometrické výpočty, limity, parser konfigurace, scene resolver.
- **Property tests:** zakázané přechody, exkluzivita vlastníka osy, invarianty zámků a monitorů.
- **CAD tests:** nulové průniky P/S/T, minimální mezery, obálky pohybu, rozměry party povrchu.
- **Simulation:** virtuální axis controllers, senzory, latence, poruchy a restart uprostřed procedury.
- **Hardware-in-the-loop:** reálný MCU/PLC, bezpečnostní I/O a simulované pohony před připojením nábytku.
- **Fault injection:** odpojený senzor, zaseknutý zámek, ztráta Ethernetu, nesouhlas poloh, přetížení, výpadek napájení.
- **Cycle tests:** opakování Work/Party/Service s průběžným měřením vůlí, driftu a teplot.
- **Ergonomie:** dosah, zorné úhly, prostor nohou, přístupnost, odlesky a dlouhodobé používání.

## 10. Nejbližší backlog

1. Zařadit `sector_generator_v2.py`, `run_freecad.sh` a tuto roadmapu do repozitáře.
2. Přesunout generátor do `cad/generators/` a upravit výchozí cestu runneru, nebo ponechat kompatibilní symlink/wrapper.
3. Vytvořit V2.1 od ergonomických parametrů 800/550 mm.
4. Odstranit překryvy P/S/T a přidat automatický collision report.
5. Opravit orientaci S/T monitorů směrem k uživateli.
6. Nahradit pravidelný centrální šestiúhelník nepravidelnou trojnásobně symetrickou geometrií.
7. Vymodelovat kompletní souvislou party vrstvu nad pracovní vrstvou.
8. Změřit potřebnou šířku technického kanálu podle reálných monitorových liftů a kabelových řetězů.
9. Založit softwarový simulátor stavových automatů dříve, než se vyberou finální pohony.
10. Sepsat první tabulku I/O, stavů, interlocků a vlastnictví os.

## 11. Otevřené otázky

- Přesný tvar a rozměry P/S/T po ergonomickém odvození.
- Skutečná šířka technického kanálu a uspořádání dvojice monitorových liftů.
- Způsob uložení a pohonu ramenních party desek a centrálního krytu.
- Ruční, asistované nebo plně motorické party transformace.
- Výběr zdvihových sloupů, jejich počet na desku, rychlost, hlučnost a certifikace.
- Potřebné užitečné a bezpečnostní zatížení jednotlivých ploch.
- Rozsah mechanicky povolených kombinací výšek sousedních P/S/T.
- Způsob detekce osoby/předmětu v nebezpečné zóně.
- DP/HDMI matrix versus AV-over-IP a umístění hostitelských počítačů.
- Rozsah Training/Simulation a izolace jednotlivých týmů.
- Umístění racku, úložišť, napájení, UPS a ventilace.
- Rozhraní na případný širší FederatedProjectWorkspace; zatím není přijato konkrétní integrační rozhodnutí.
- Licenční model pro software, firmware, elektroniku, CAD a dokumentaci.
