# Party mechanismus V3.1 — koncepční návrh

Tento dokument popisuje vybranou geometrii vedení a zámků. Nejde o výrobní
dokumentaci ani o potvrzení únosnosti, životnosti nebo funkční bezpečnosti.

## Ramenní modul

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
- Střed modulu má mezi Party a Work uložením zdvih 1240 mm.
- Party polohu nesou tři mechanické zámky. Uložená poloha vyžaduje další tři
  mechanické zámky nezávislé na pohonu.

## Potvrzení a blokování

Každá cílová poloha má dvě nezávislé informace: `POSITION` potvrzuje dosažení
geometrické polohy a `LOCK` potvrzuje mechanické zajištění. Pohyb další osy je
povolen až po shodě obou signálů. Při neshodě, ztrátě napájení nebo překročení
synchronizační odchylky se pohyb zastaví a modul musí zůstat mechanicky držen.

## Otevřené ověření

- přesné nekonvexní pohybové obálky pro zdvih a rotaci,
- kolize během pohybu, nikoli pouze v koncových polohách,
- dimenzování osy, ložisek, vozíků, pohonů, brzd a zámků,
- průhyb a stabilita velkého centrálního modulu,
- servisní přístup, nouzové ruční spuštění a zachycení při poruše.
