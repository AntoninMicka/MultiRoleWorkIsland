# Party mechanismus V3.1 — koncepční návrh

Tento dokument popisuje vybranou geometrii vedení a zámků. Nejde o výrobní
dokumentaci ani o potvrzení únosnosti, životnosti nebo funkční bezpečnosti.

## Ramenní modul

- Délka Party ramene je nezávislá na délce S/T pracovního křídla; kvůli
  pokrytí pracovní vrstvy musí platit `party_arm_length >= side_desk_length`.
- Dva synchronizované svislé vozíky leží na podélné ose technologického kanálu,
  jeden u centrální spáry a druhý na vnějším konci modulu.
- Vozíky nesou společnou podélnou osu pro otočení desky o 90°.
- Střed osy se mezi Party a otočnou výškou přesune o 650 mm.
- V Party poloze modul dosedá do čtyř nosných zámků. Ve svislé Work poloze jej
  zajišťují dva zámky vozíků; pohon nesmí být jediným nosným prvkem.
- Předběžná varianta je motorická: mechanicky synchronizovaný svislý pohon obou
  vozíků a samostatný rotační pohon s brzdou nebo samosvorným převodem.

## Centrální modul

- Modul zůstává vodorovný a pohybuje se pouze svisle.
- Tři synchronizovaná teleskopická vedení jsou na roztečném poloměru 140 mm
  uvnitř centrálního technického jádra.
- Střed modulu má mezi Party a Work uložením zdvih 1241 mm. Jeden milimetr navíc
  kompenzuje radiální přesah rohů ramenní desky při rotaci a zachovává nejméně
  20mm vůli od uloženého centrálního modulu.
- Party polohu nesou tři mechanické zámky. Uložená poloha vyžaduje další tři
  mechanické zámky nezávislé na pohonu.

## Potvrzení a blokování

Každá cílová poloha má dvě nezávislé informace: `POSITION` potvrzuje dosažení
geometrické polohy a `LOCK` potvrzuje mechanické zajištění. Pohyb další osy je
povolen až po shodě obou signálů. Při neshodě, ztrátě napájení nebo překročení
synchronizační odchylky se pohyb zastaví a modul musí zůstat mechanicky držen.

## Geometrická sekvence

Přechod Party → Work nejprve zvedne centrální modul o 1241 mm. Každé rameno
se potom samostatně zvedne o 650 mm a otočí o 90° do svislé polohy. Work → Party
probíhá v opačném pořadí: rameno se otočí do vodorovné polohy, spustí na nosné
zámky a centrální modul se spustí jako poslední.

FreeCAD kontrola používá 119 skutečných poloh těles s krokem nejvýše 50 mm a
5°. Navíc kontroluje spojité přesné hranoly svislých zdvihů a konzervativní
válcovou obálku celé rotace. Obě kontroly prošly bez objemové kolize; minimální
vůle rotační obálky k centrálnímu modulu je 20,64 mm. Výsledek dokládá
geometrickou průchodnost, nikoliv dynamiku, průhyb ani bezpečnost pohonů.

## Otevřené ověření

- dimenzování osy, ložisek, vozíků, pohonů, brzd a zámků,
- průhyb a stabilita velkého centrálního modulu,
- servisní přístup, nouzové ruční spuštění a zachycení při poruše.
