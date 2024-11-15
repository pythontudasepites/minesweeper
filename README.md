# Aknakereső játék
Az aknakereső (Minesweeper) egy logikai játék, mely adott sor- és oszlopszámú táblázatban elrendezett mezőcellákat tartalmaz, amelyek közül, meghatározott számú, „aknát” rejt. A cél az egyes cellák felfedésével az összes akna megtalálása, illetve azok elkerülése. Ha sikerül az összes, nem aknát tartalmazó cellát felfedni, akkor a játék győzelemmel befejeződik. Ha egy felfedett cellában akna van, akkor a játék vereséggel azonnal véget ér. A részletszabályok az interneten megtalálhatók, többek között például magyarul az „Aknakereső” vagy angolul a „Minesweeper” Wikipedia szócikkeknél.

A játékfelület két részre tagolódik. Felül, egy sorban látható a zászlószámláló, illetve annak aktuális értéke, mellette az új játékot indító nyomógomb. Ettől jobbra pedig a játék megkezdése óta eltelt idő látható, ami másodpercenként növekszik. 
Ez alatt látható a játékmező, amely a feldezésre váró cellákat négyzethálós elrendezésben jeleníti meg.

A játék indításakor a zászlószámláló az elrejtett aknák számát mutatja. Ha a játéktér bármely fel nem fedett celláján zászlót jelenítünk meg, vagyis úgy gondoljuk, hogy ott akna van, a zászlószámláló értéke eggyel csökken, mutatva, hogy még mennyi felderítendő akna van hátra. Az időmérés a játékmezőn történő első cella felfedésével kezdődik, amin soha nincs akna.

Ha sem az aktuálisan felfedett cella, sem a közvetlen szomszédai nem tartalmaznak aknát, akkor a cellák automatikusan mindaddig felfedődnek, amíg a szomszédaikban nem lesz legalább egy akna. Ezen cellákra ki is lesz írva a szomszédos aknák száma.

Jobb egérgombbal történő kattintás esetén a cella nem lesz felfedve, hanem egy zászlót ábrázoló karakter jelenik meg és egyúttal a zászlószámláló eggyel csökken. Újabb jobb egérgomb kattintásra a zászló eltűnik és a zászlószámláló értéke eggyel nő. Vagyis a jobb egérgomb lenyomás oda-vissza kapcsoló (toggle) üzemmódú.

Az „ÚJ JÁTÉK” feliratú gombra kattintva változatlan játékparaméterekkel (sor- és oszlopszám, valamint az elrejtett aknák száma) kezdhető új játék. Ha más paraméterekkel akarunk játékot indítani, akkor az „ÚJ JÁTÉK” gombra a jobb egérgombbal kell kattintani. A felugró párbeszédablak beviteli mezőjébe lehet megadni vesszővel elválasztott egész számokkal az új sor- és oszlopszámot, valamint opcionálisan az aknák számát. Mivel az alapértelmezett játékterület 8x8 méretű 10 aknával, ez jelenik meg a párbeszédablakban kezdőértékként. Ha nem adunk meg aknaszámot, akkor a program számolja azt ki a sor- és oszlopértékekből kiadódó összcellaszám alapján. Ez a cellaszámmal úgy lesz arányos, ahogy a 10 akna a 8x8-as tábla 64 cellájával.

A játékot a **main** modul szkriptként futtatásával lehet indítani, amihez Python 3.10+ verzió szükséges. 

Az alábbi képernyőképek alapértelmezett és attól eltérő paraméterekkel indított játékokat mutat nyert vagy vesztett végállapotban, valamint az új játékjellemzők beviteli ablakát is láthatjuk.

<img src="https://github.com/pythontudasepites/minesweeper/blob/main/minesweeper_1.jpg" width="623" height="420">

<img src="https://github.com/pythontudasepites/minesweeper/blob/main/minesweeper_2.jpg" width="623" height="420">
