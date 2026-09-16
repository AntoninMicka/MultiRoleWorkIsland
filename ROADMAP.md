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
- Technický kanál mezi sousedními plochami na rameni má ve V3.0 pracovní hodnotu 300 mm; musí se ověřit podle reálných monitorových liftů, konstrukce a kabelových řetězů.
- Čelní hrana pracoviště směrem k uživateli má mít přibližně 800 mm.
- V3.0 zmenšuje radiální hloubku primární pracovní desky na 400 mm. Původní studie V2.1–V2.3 ověřovala 500–600 mm s výchozí hodnotou 550 mm; při zachování 150mm zadního nosného pásu zbývá 250mm referenční prostor pro nohy, takže ergonomii kratší desky je nutné znovu ověřit fyzickou maketou.
- V3.0 používá společnou 400mm vzdálenost mezi hlavní přední a zadní hranou všech P/S/T desek. S/T zůstávají dlouhé 1000 mm a vznikají přímým vysunutím celé boční hrany P, takže napojení je plynulé bez přechodových segmentů a zářezů.
- P/S/T desky se nesmějí půdorysně překrývat. Jejich tvar se má odvodit od polohy uživatele, monitoru, ergonomické hloubky a hran sousedních pracovišť, nikoliv z pevných obdélníků.
- Centrální party útvar má trojnásobnou symetrii, ale nemá být pravidelným šestiúhelníkem. Tři hlavní hrany orientované k uživatelům mají přibližně 800 mm; zbývající hrany vzniknou z návaznosti desek.
- Primární monitory tvoří trojúhelník uprostřed. Sekundární a terciární monitor každého pracoviště se orientují k jeho uživateli; nemají být pouze kolmé k ose ramene.
- Devět monitorů se parkuje pod pracovní vrstvu. Dvojice bočních monitorů sousedních pracovišť leží zády k sobě kolem technického kanálu.
- Zadní zvýšené hrany pracovních desek mají bránit pádu předmětů při změně výšky.

### Nezávislé monitorové moduly a ergonomický oblouk

- Geometrie monitorů se neodvozuje přímo od středů desek P/S/T. Desky se navrhují podle dosahu, prostoru pro nohy a nezávislého výškového nastavení; monitory se v poloze Work skládají do kompaktního ergonomického oblouku kolem uživatele.
- Každý z devíti monitorů je samostatný mechanický modul. Sousední monitory se mechanicky nespojují, nezamykají a nepřenášejí mezi sebou zatížení; společná pracovní poloha vzniká pouze koordinovaným řízením.
- Každý monitorový modul zajišťuje vertikální výsun z parkovací kapsy, horizontální posun do pracovní polohy, natočení k uživateli, snímání rozhodujících poloh a bezpečný návrat do parkovací polohy.
- Primární monitor může mít kratší nebo nulový horizontální posun. S/T monitory se po vertikálním vysunutí posunou k primárnímu monitoru, aby vytvořily souvislejší oblouk.
- Koncept V2.2 umisťuje primární monitorový lift za zadní hranu P směrem ke středu a dvojice S/T liftů do technického kanálu mezi sousední desky; monitorové moduly tak neprocházejí půdorysem pracovních desek.
- V2.2 rozšiřuje zadní hranu P a používá její šikmé boky jako společné hrany navazujících S/T desek podle vyznačeného půdorysu.
- V2.3 uzavírá půdorys pracovních desek: přední a zadní hrana každé P/S/T desky jsou rovnoběžné; tato podmínka je automaticky kontrolovaný geometrický invariant.
- V3.0 zužuje technický kanál na 300 mm. Osy dvojice 90mm monitorových liftů leží 85 mm od osy kanálu, takže každému zbývá požadovaná 20mm rezerva k desce; S/T monitor se z osy liftu přesune do bezkolizní pracovní polohy.
- Parametry V3.0 se načítají z `config/design_parameters.toml`. Editor spuštěný přes `./run.sh --configure` zobrazuje živý Work/Party SVG náhled, nezávislé vstupy, odvozené vazby a geometrické kontroly; uložené hodnoty používá přímo FreeCAD generátor.
- Cílová mezera mezi sousedními rámečky v poloze Work je 20–40 mm. Finální hodnota závisí na konkrétních monitorech, rámech, poloměru oblouku a výrobních tolerancích.
- Spodní hrana vysunutého monitoru musí zůstat bezpečně nad deskami i při povoleném zpoždění os, brzdění, průhybu, vůlích a výrobních tolerancích.
- Mechanická výška monitoru není jediným bezpečnostním opatřením; Workstation Coordinator současně hlídá relativní výšky P/S/T.

Počáteční prototypové limity, které musí být později odvozeny z měření rychlosti, latence, přesnosti snímání a brzdné dráhy:

```text
FOLLOW_WARNING = 15 mm
FOLLOW_LIMIT   = 30 mm
FOLLOW_FAULT   = 50 mm
```

### Výšky a režimy

- Party výška: 700 mm.
- Aktuální CAD používá pracovní výšku 750 mm a provizorní servisní výšku 1200 mm.
- Dříve uvažované ergonomické rozsahy přibližně 650–1250 nebo 680–1280 mm je nutné sjednotit s reálně vybranými zdvihy.
- Hodnoty fyzického zdvihu 300–2000 mm a softwarového posunu na 700–2400 mm v prvních skriptech jsou simulační obálkou, nikoliv schválenou výrobní specifikací.
- Cílové zatížení jedné řízené jednotky bylo uvažováno až přibližně 200 kg; musí být rozděleno na dynamické, statické a bezpečnostní zatížení a potvrzeno výpočtem.

### Party vrstva

- Party režim není pouze sada úzkých spojovacích pásů.
- Druhá sada desek musí vytvořit souvislou horní vrstvu a kompletně překrýt pracovní desky, zaparkované monitory i technické mezery.
- Koncept V3.0 dělí party vrstvu na centrální modul `CENTRAL_TOP` a tři shodně odvozené ramenní moduly `PARTY_ARM_1/2/3`. Přímé spáry přesně navazují na uzavřený půdorys V2.3, moduly se půdorysně nepřekrývají a společně zakrývají všech devět pracovních desek i parkovací půdorysy monitorů.
- Horní rovina všech čtyř party modulů je 700 mm; v aktuálním statickém modelu ji tvoří 40mm krycí vrstva podepřená ve výšce 660 mm. Uložení v režimu Work/Hybrid a kinematika přestavení zatím nejsou navrženy ani validovány.
- Ramenní party desky mohou být v pracovním/hybridním režimu postavené jako vertikální přepážky.
- Koncept V3.1 ukládá tři ramenní moduly ve Work jako svislé přepážky v osách technologických kanálů: spodní hrana 780 mm, horní hrana 1880 mm. Centrální modul je vodorovně zaparkovaný nad monitorovou zónou v rozsahu 1900–1940 mm. Mezi polohami zůstává 20mm statická mezera; únosnost, vedení a pohybové obálky ještě nejsou validovány.
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
- Devět monitorových modulů má samostatně evidované vlastnictví; Workstation Coordinator koordinuje jejich pohyb s lokálními osami P/S/T.

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

Každý monitorový modul eviduje minimálně:

```text
vertical_position
horizontal_position
yaw_position
park_sensor
work_sensor
motion_state
fault_state
owner
```

Minimální stavový automat monitoru:

```text
PARKED
RAISING
SAFE_HEIGHT
TRANSLATING_IN
ROTATING_IN
WORK
ROTATING_OUT
TRANSLATING_OUT
LOWERING
FAULT
```

Axis controller řídí každou desku samostatně, ale nesmí přijmout pohyb porušující aktivní bezpečnostní obálku monitoru.

## 4. Bezpečnostní invarianty

- E-STOP, koncové spínače, ochrana proti sevření a základní bezpečnost nesmějí záviset na Raspberry Pi, GUI ani síťové službě.
- Service je povolen pouze s party deskami v poloze Work/uloženo a se všemi dotčenými monitory potvrzenými v parkovací poloze.
- Pohyb desky je blokován, pokud její mechanický zámek není ve stavu požadovaném danou procedurou.
- Ruční manipulace s party deskou: odemknout výchozí polohu → přemístit/překlopit → zamknout cílovou polohu → potvrdit. Koordinátor samostatně ověřuje polohu i zámek koncovými spínači.
- HMI nesmí pokračovat k dalšímu kroku, dokud nejsou splněny interlocky.
- Před transformací se kontroluje přítomnost osob a předmětů, poloha monitorů, výšky dotčených desek a stav zámků.
- Musí existovat definovaný bezpečný mezistav a postup obnovy po výpadku napájení, komunikace nebo senzoru.
- Bezpečnostní analýza musí pokrýt sevření, střih, převrácení, kolizi os, pád desky, přetížení, uvolněný zámek, přerušený kabel a neočekávaný restart.
- Horizontální posun monitoru je povolen pouze po potvrzení bezpečné vertikální polohy a nesmí vést přes desku mimo povolené výškové pásmo.
- Při vysunutých a přisunutých monitorech koordinátor průběžně sleduje rozdíly výšek P/S/T. Překročení `FOLLOW_WARNING` zobrazí varování, překročení `FOLLOW_LIMIT` zastaví ostatní dotčené desky a překročení `FOLLOW_FAULT` vyvolá řízené zastavení a stav `FAULT`.
- Porucha S/T nesmí vyvolat nekontrolovaný pohyb P ani přenos síly přes monitor do jiné desky nebo monitorového modulu.
- Ztráta komunikace blokuje pokračování horizontálního posunu monitoru.
- Party nebo servisní transformace není povolena bez potvrzeného `MONITOR_PARK` všech dotčených monitorů.

### Bezpečné rozložení monitorů

1. Zastavit samostatné pohyby dotčených P/S/T desek.
2. Srovnat P/S/T do povoleného výškového pásma.
3. Ověřit volný prostor a stav monitorových mechanismů.
4. Vysunout P/S/T monitory do bezpečné vertikální výšky.
5. Potvrdit koncové nebo absolutní polohy Z.
6. Horizontálně přisunout S/T monitory k primárnímu monitoru.
7. Natočit S/T monitory směrem k uživateli.
8. Ověřit pracovní a bezpečnou polohu všech monitorů.
9. Povolit koordinované výškové polohování pracovních desek.

### Bezpečné parkování monitorů

1. Zastavit samostatné pohyby dotčených P/S/T desek.
2. Srovnat desky do bezpečného výškového pásma.
3. Natočit S/T monitory do parkovací orientace.
4. Horizontálně odsunout S/T monitory od primárního monitoru.
5. Ověřit zasunutí horizontálních mechanismů.
6. Spustit monitory do parkovacích kapes.
7. Potvrdit `MONITOR_PARK` všech dotčených monitorů.
8. Teprve potom povolit party nebo servisní transformaci.

## 5. Softwarová architektura

Software se dělí na tři nezávislé roviny spojené scénickým enginem:

### Mechanical plane

- řízení os, monitorových liftů, party mechanismů a zámků,
- nezávislé řízení vertikální polohy, horizontálního posunu a natočení každého monitorového modulu,
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
- Každý monitorový modul potřebuje energetický řetěz a odlehčení tahu pro kombinovaný vertikální a horizontální pohyb i natočení.
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
- [x] Přidat `.gitignore` pro logy, cache a lokální buildy.
- [ ] Zapsat podporované verze FreeCADu, Pythonu a OpenCascade.
- [ ] Přidat CI smoke test: spuštění generátoru, neprázdný FCStd/STEP, počet očekávaných objektů.

**Hotovo, když:** čistý checkout vytvoří stejným příkazem model a oba STEP snapshoty.

### M1 — Ergonomický půdorys V2.1–V2.3

- [x] Nahradit pravidelný centrální šestiúhelník trojnásobně symetrickým nepravidelným obrysem.
- [x] Parametrizovat čelo 800 mm a pracovní hloubku; původní výchozí hodnota 550 mm je ve V3.0 upravena na 400 mm pro primární desku.
- [x] Odvodit P/S/T desky z ergonomických hran a odstranit všechny půdorysné překryvy.
- [x] Ve statické V2.1 studii natočit S/T monitory k uživateli a ověřit základní zorné úhly, vzdálenost a vzájemné zakrytí.
- [x] Dopočítat tvar a rozměry S/T místo použití pevné šířky 600 mm.
- [x] Doplnit 2D kótovaný půdorys a parametrické kontrolní rozměry.
- [x] Ověřit polohy židlí, prostor pro nohy, vstup a opuštění pracoviště v parametrickém půdorysu; fyzická uživatelská validace zůstává v M5.
- [ ] Definovat polohu očí uživatele, doporučenou pozorovací vzdálenost a cílový monitorový oblouk.
- [x] Ve V2.2 umístit P/S/T monitory podle zorného pole nezávisle na středech pracovních desek a přesunout jejich lifty mimo půdorysy desek.
- [x] Ve V2.2 stanovit cílové úhly natočení S/T monitorů a ověřit mezeru rámečků 20–40 mm.
- [x] Ve V2.2 ověřit, že monitorový oblouk neomezuje pracovní hloubku 500–600 mm.
- [x] Ve V2.3 sjednotit každou pracovní desku tak, aby její přední a zadní hrana byly rovnoběžné, a uzavřít půdorys pracovních desek.
- [ ] Ověřit viditelnost všech monitorů pro různé výšky uživatele.
- [ ] Parametrizovat pracovní a parkovací polohu každého monitoru.

**Hotovo, když:** žádné dvě pracovní desky se neprotínají, přední a zadní hrany všech desek jsou rovnoběžné, aktuální 400mm primární hloubka projde ergonomickým ověřením a tři nezávislé monitory vytvoří ověřený ergonomický oblouk s definovanými mezerami pro celý cílový rozsah uživatelů.

### M2 — Souvislá party vrstva a kinematika

- [x] Navrhnout kompletní druhou sadu horních desek překrývající pracovní vrstvu, monitory a mezery.
- [x] Rozdělit horní vrstvu na tři ramenní moduly a centrální modul s realizovatelnými spárami.
- [x] Navrhnout koncepční uložení party desek v režimech Work/Hybrid: ramena jako nezávislé svislé přepážky v kanálech, centrální modul vodorovně nad monitorovou zónou. Přesná kinematika a konstrukční validace zůstávají otevřené.
- [ ] Prověřit lift → rotate → lower sekvence a přesné pohybové obálky, nikoliv pouze bounding boxy.
- [ ] Navrhnout panty, vedení a ruční nebo motorické přestavení.
- [ ] Umístit mechanické zámky a dvojici potvrzení POSITION/LOCK.
- [x] Staticky prověřit souvislé geometrické zarovnání celého party povrchu na 700 mm; bezpečnost pohybu zůstává součástí otevřené kinematické validace.
- [ ] Navrhnout samostatný vertikální lift každého monitoru.
- [ ] Navrhnout horizontální kolejnicový nebo teleskopický posun S/T monitorů.
- [ ] Porovnat motorické a pasivně vedené natočení monitoru.
- [ ] Vytvořit přesné pohybové obálky vertikálního výsunu, horizontálního posunu a natočení monitorů.
- [ ] Ověřit kolize monitorů, desek, kabelů, party vrstvy a sousedních mechanismů.
- [ ] Navrhnout energetický řetěz pro kombinovaný vertikální a horizontální pohyb monitoru.
- [ ] Ověřit přístupnost monitorových mechanismů v režimu Service.
- [ ] Navrhnout mechanické dorazy, nouzové ruční zasunutí a ochranu proti pádu monitoru.

**Hotovo, když:** CAD přehraje bezkolizní posloupnost Work ↔ Party, všech devět monitorů bezpečně projde mezi `PARKED` a `WORK` a horní vrstva vytvoří souvislý použitelný povrch.

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
- [ ] Implementovat monitorové stavové automaty a koordinované sekvence rozložení/parkování.
- [ ] Implementovat a změřenými daty kalibrovat `FOLLOW_WARNING`, `FOLLOW_LIMIT` a `FOLLOW_FAULT`.
- [ ] Ověřit blokování horizontálního posunu bez potvrzené bezpečné výšky a při ztrátě komunikace.
- [ ] Implementovat lokální Work a Service procedury.
- [ ] Vyrobit kabelové svazky a energetické řetězy pro každou pohyblivou část.
- [ ] Ověřit ergonomii na uživatelích různých výšek.

**Hotovo, když:** stanice pracuje samostatně, bezpečně přejde Work ↔ Service, každý monitor lze samostatně zaparkovat a diagnostikovat a porucha jedné osy nepřenese sílu do sousedního modulu.

#### Akceptační kritéria monitorového subsystému

- Žádný monitor není mechanicky spojen se sousedním monitorem.
- Každý monitor lze samostatně zaparkovat a diagnostikovat.
- Pracovní sestava vytváří ergonomický oblouk s cílovými mezerami 20–40 mm.
- Horizontální posun nemůže začít v nebezpečné výšce ani pokračovat po ztrátě komunikace.
- Povolené zpoždění P/S/T nevede ke kolizi s monitorem.
- Porucha jedné osy nevyvolá přenos síly do sousední desky nebo monitoru.
- Systém bezpečně zastaví při překročení povoleného rozdílu výšek.
- Party transformace není povolena bez potvrzeného `MONITOR_PARK`.

### M6 — Sdílené rameno a party mechanismus

- [ ] Spojit dvě sousední stanice jedním fyzickým ramenem.
- [ ] Implementovat PARTY_AB jako první sdílený modul.
- [ ] Ověřit dočasné převzetí os Central Coordinator-em.
- [ ] Ověřit mechanické zámky, koncové spínače a krokovou ruční proceduru.
- [ ] Otestovat rozdílné výšky sousedních pracovišť a odmítnuté transformace.
- [ ] Ověřit technický kanál 300 mm s reálnými lifty a kabeláží.

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
- **Property tests:** zakázané přechody, exkluzivita vlastníka osy, invarianty zámků a monitorů, zákaz horizontálního posunu mimo `SAFE_HEIGHT` a blokování Party bez `MONITOR_PARK`.
- **CAD tests:** nulové průniky P/S/T, monitorový oblouk a mezery rámečků, přesné monitorové pohybové obálky, minimální mezery a rozměry party povrchu.
- **Simulation:** virtuální axis controllers, senzory, latence, poruchy a restart uprostřed procedury.
- **Hardware-in-the-loop:** reálný MCU/PLC, bezpečnostní I/O a simulované pohony před připojením nábytku.
- **Fault injection:** odpojený senzor, zaseknutý zámek, ztráta Ethernetu během horizontálního posunu monitoru, nesouhlas poloh, překročení rozdílu výšek, přetížení a výpadek napájení.
- **Cycle tests:** opakování Work/Party/Service s průběžným měřením vůlí, driftu a teplot.
- **Ergonomie:** dosah, zorné úhly, prostor nohou, přístupnost, odlesky a dlouhodobé používání.

## 10. Nejbližší backlog

1. Navrhnout panty, vedení, způsob přestavení a mechanické zámky party modulů.
2. Vytvořit přesné pohybové obálky party modulů a ověřit sekvenci Work ↔ Party.
3. Definovat polohu očí, doporučenou pozorovací vzdálenost, poloměr monitorového oblouku a cílové úhly S/T.
4. Ověřit monitorovou sestavu pro různé výšky uživatele a parametrizovat pracovní i parkovací polohy.
5. Navrhnout vertikální lift, horizontální posun a způsob natočení monitorových modulů.
6. Vytvořit přesné pohybové obálky monitorů a ověřit kolize s deskami, kabely a party vrstvou.
7. Změřit potřebnou šířku technického kanálu podle reálných monitorových liftů, horizontálních posunů a kabelových řetězů.
8. Založit softwarový simulátor stavových automatů dříve, než se vyberou finální pohony.
9. Sepsat první tabulku I/O, stavů, interlocků a vlastnictví os včetně monitorových modulů.

## 11. Otevřené otázky

- Přesný tvar a rozměry P/S/T po ergonomickém odvození.
- Poloha očí pro cílový rozsah uživatelů, poloměr monitorového oblouku, pozorovací vzdálenost a finální mezera rámečků.
- Skutečná šířka technického kanálu a uspořádání dvojice monitorových liftů.
- Konstrukce vertikálního liftu a horizontálního posunu monitoru; motorické versus pasivně vedené natočení.
- Bezpečná výška spodní hrany monitorů a konečné hodnoty `FOLLOW_WARNING`, `FOLLOW_LIMIT` a `FOLLOW_FAULT` podle naměřené dynamiky.
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
