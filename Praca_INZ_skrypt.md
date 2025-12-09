\# -\*- coding: utf-8 -\*-

from Autodesk.Revit.DB import \* #import DataBase (elementy modelu (ściany, stropy), parametry, geometrię (linie, punkty) itp.)

from Autodesk.Revit.UI import \* #import UserInterface (okna dialogowe, polecenia)

import clr #import Common Language Runtime

import sys #import System (zatrzymanie skryptu w przypadku błędu)



clr.AddReference("Microsoft.VisualBasic") #załadowanie zewnętrznej biblioteki .NET --> Interaction.InputBox

from Microsoft.VisualBasic import Interaction #możliwość .InputBox() --> zbieranie uwagi od użytkownika

from System.Collections.Generic import List #możiwość tworzenia list



doc = \_\_revit\_\_.ActiveUIDocument.Document #aktualnie pobierany projekt Revit

foot = 3.28084  # konwersja ft -> m



\# --------------------------------------------------------------------------------------------------------------------------- parametry globalne -------------------------------------------------------------------------------------------------------------------------------------------------------------

max\_glebokosc\_m = 25.0

wys\_standard\_pietra\_m = 3.0

wys\_standard\_pietra\_ft = wys\_standard\_pietra\_m \* foot

liczba\_pieter = 4

cofniecie\_lica\_m = 2.4

cofniecie\_lica\_ft = cofniecie\_lica\_m \* foot



\# --------------------------------------------------------------------------------------------------------------------------- komunikat startowy -------------------------------------------------------------------------------------------------------------------------------------------------------------

main\_message = (

&nbsp;   "Generacja kompozycji urbanistycznej nastąpi z uwzględnieniem stałych parametrów projektowych, założeń funkcjonalnych oraz uwarunkowań formalno-prawnych zgodnie z Miejscowym Planem Zagospodarowania Przestrzennego:\\n\\n"

&nbsp;   "1) Maksymalna powierzchnia zabudowy: 60%.\\n"

&nbsp;   "2) Minimalny udział procentowy powierzchni biologicznie czynnej: 25%.\\n"

&nbsp;   "3) Zakres dopuszczalnej intensywności zabudowy: 1,2 – 3,2.\\n\\n"

&nbsp;   "Dodatkowe ustalenia i założenia funkcjonalne:\\n\\n"

&nbsp;   " - Wariantowanie brył budynku nastąpi zgodnie z funkcjonalnością przewidzianą dla usług nauki z usługami z zakresu kultury, gastronomii lub handlu w parterach budynków.\\n"

&nbsp;   " - Powierzchnia całkowita parteru nie może stanowić więcej niż 60% powierzchni całkowitej pierwszego piętra.\\n"

&nbsp;   " - Ustalenia planistyczne dopuszczają zastosowanie dachu płaskiego.\\n\\n"

&nbsp;   "Uwaga dot. działek i linii zabudowy:\\n\\n"

&nbsp;   " - Dla działek ewidencyjnych nr 7/3, 7/4 oraz 7/5 ustala się maksymalną wysokość zabudowy na 12,0 m.\\n"

&nbsp;   " - Dla działki ewidencyjnej nr 7/6 dopuszcza się maksymalną wysokość zabudowy do 16,0 m, pod warunkiem zgodności ze wszystkimi pozostałymi ustaleniami MPZP.\\n"

&nbsp;   " - Miejsce generacji brył budynku jest nierozerwalnie związane z usytuowaniem obowiązującej linii zabudowy oraz nieprzekraczalnej linii zabudowy.\\n"

&nbsp;   " - W celu zapewnienia spójności kompozycyjnej zdefiniowano pomocnicze geometrie referencyjne.\\n"

&nbsp;   " - Zakaz prac ziemnych dotyczy cennych drzew w obrębie rzutu korony lub w odległości < 3.0 m od pnia (z wyjątkiem metod nieinwazyjnych).\\n"

)



TaskDialog.Show("Start", main\_message)



\# ------------------------------------------------------------------------------------------------------------------ pobieranie wartości od użytkownika --------------------------------------------------------------------------------------------------------------------------------------------------------------

try:

&nbsp;  

&nbsp;   glebokosc\_kolumn\_m = float(Interaction.InputBox( #DK

&nbsp;       "Głębokość strefy podcienia \[m] (min 6.0, max 20.0)",

&nbsp;       "Głębokość strefy podcienia", "8.5").replace(',', '.'))

&nbsp;   if not (6.0 <= glebokosc\_kolumn\_m <= 20.0):

&nbsp;       TaskDialog.Show("Błąd", "Wartość 'Głębokość strefy podcienia musi być pomiędzy 6.0m a 20.0m.")

&nbsp;       sys.exit()



&nbsp;   glebokosc\_budynku\_m = float(Interaction.InputBox( #DB

&nbsp;       "Głębokość bryły budynku za kolumnami \[m] (min 6.0, max 20.0)",

&nbsp;       "Głębokość bryły budynku za kolumnami", "8.5").replace(',', '.'))

&nbsp;   if not (6.0 <= glebokosc\_budynku\_m <= 20.0):

&nbsp;       TaskDialog.Show("Błąd", "Wartość 'Głębokość bryły budynku za kolumnami musi być pomiędzy 6.0m a 20.0m.")

&nbsp;       sys.exit()



&nbsp;   col\_spacing\_m = float(Interaction.InputBox(

&nbsp;       "Rozstaw osiowy kolumn \[m] (min 4.0, max 8.0)",

&nbsp;       "Rozstaw osiowy kolumn", "5.0").replace(',', '.'))

&nbsp;   if not (4.0 <= col\_spacing\_m <= 8.0):

&nbsp;       TaskDialog.Show("Błąd", "Wartość 'Rozstaw osiowy kolumn' musi być pomiędzy 4.0m a 8.0m.")

&nbsp;       sys.exit()



&nbsp;   cofniecie\_iv\_m = float(Interaction.InputBox(

&nbsp;       "Wycofanie V kondygnacji w głąb lica \[m] (min 2.4, max 6.0)",

&nbsp;       "Wycofanie V kondygnacji w głąb lica", "4.5").replace(',', '.'))

&nbsp;   if not (2.4 <= cofniecie\_iv\_m <= 6.0):

&nbsp;       TaskDialog.Show("Błąd", "Wartość 'Wycofanie V kondygnacji w głąb lica' musi być pomiędzy 2.4m a 6.0m.")

&nbsp;       sys.exit()



&nbsp;   glebokosc\_audytorium\_ns\_m = float(Interaction.InputBox(

&nbsp;       "Głębokość strefy audytorium wciętej w głąb działki \[m] (min 15.0, max 30.0)",

&nbsp;       "Głębokość strefy audytorium wciętej w głąb działki", "20.0").replace(',', '.'))

&nbsp;   if not (15.0 <= glebokosc\_audytorium\_ns\_m <= 30.0):

&nbsp;       TaskDialog.Show("Błąd", "Wartość 'Głębokość strefy audytorium' musi być pomiędzy 15.0m a 30.0m.")

&nbsp;       sys.exit()



except:

&nbsp;   TaskDialog.Show("Błąd", "Wprowadzono nieprawidłową wartość. Przerwano skrypt.")

&nbsp;   sys.exit()



\# walidacje MPZP; na potrzebę przyjęcia danych "krańcowych" ---------------------------------------------------

if glebokosc\_kolumn\_m + glebokosc\_budynku\_m > max\_glebokosc\_m:

&nbsp;   TaskDialog.Show("Brak zgodności z MPZP", "Suma głębokości przekracza {} m.".format(max\_glebokosc\_m))

&nbsp;   sys.exit()



min\_glebokosc\_podcienia\_m = (2.0 / 3.0) \* glebokosc\_budynku\_m

if glebokosc\_kolumn\_m < min\_glebokosc\_podcienia\_m:

&nbsp;   TaskDialog.Show("Brak zgodności z MPZP", "Powierzchnia całkowita parteru stanowi więcej niż 60% powierzchni całkowitej pierwszego piętra; Głębokość kolumn zbyt mała względem głębokości budynku (min {:.2f}m).".format(min\_glebokosc\_podcienia\_m))

&nbsp;   sys.exit()



\# działania na danych i konwersje jednostek ---------------------------------------------------------------

col\_spacing\_ft = col\_spacing\_m \* foot 

col\_depth\_ft = (glebokosc\_kolumn\_m / 2.0) \* foot

glebokosc\_kolumn\_ft = glebokosc\_kolumn\_m \* foot

glebokosc\_budynku\_ft = glebokosc\_budynku\_m \* foot

calkowita\_glebokosc\_ft = glebokosc\_kolumn\_ft + glebokosc\_budynku\_ft

cofniecie\_iv\_ft = cofniecie\_iv\_m \* foot

glebokosc\_audytorium\_ns\_ft = glebokosc\_audytorium\_ns\_m \* foot

glebokosc\_audytorium\_35m\_ft = 35.0 \* foot



\# ----------------------------------------------------------------------------------------------------------------------------------- ID linii modelu i łuków -----------------------------------------------------------------------------

line\_ids = \[ElementId(1266833), ElementId(1267037), ElementId(1267137), ElementId(1267259),

&nbsp;           ElementId(1265069), ElementId(1265253), ElementId(1265357), ElementId(1266049),

&nbsp;           ElementId(1266217), ElementId(1267547), ElementId(1267677), ElementId(1268120),

&nbsp;           ElementId(1268276),

&nbsp;           ElementId(1299369), ElementId(1299422), ElementId(1299485), ElementId(1299536),

&nbsp;           ElementId(1303106)

&nbsp;          ]

ids\_do\_odwrocenia = \[1260740, 1265069, 1265253, 1265357, 1266049, 1299485]

arc\_ids = \[ElementId(1289914), ElementId(1290384)]

auditorium\_line\_ids = \[ElementId(1282579), ElementId(1283599), ElementId(1283696),

&nbsp;                      ElementId(1285389), ElementId(1285445), ElementId(1288166)]



\# ------------------------------------------------------------------------------------------------------- poziomy, wewnętrzne zabezpieczenie, gdyby nie było utworzonych minimalnej liczny o --------------------

levels = sorted(list(FilteredElementCollector(doc).OfClass(Level)), key=lambda x: x.Elevation) #kolektor przeszukujący cały dokument projektowy, tworzy całą listę ze zmiennymi X jako współżędna

if len(levels) < 2: #wybranie elementu level czyli poziom, sprawdza ile elementów znajduej się na liście "levels" --> obliczanie wysokości parteru (jeden poziom lub zadnego --> wróba dowołania przerwie się błędem)

&nbsp;   TaskDialog.Show("Błąd", "Projekt musi zawierać co najmniej dwa poziomy.")

&nbsp;   sys.exit()

poziom\_0 = levels\[0] #przypisanie poziomów do zmiennych

poziom\_1 = levels\[1]

wysokosc\_parteru\_ft = poziom\_1.Elevation - poziom\_0.Elevation #obliczanie na jakiej wysokości jest ściana (jedna kondygnacja)

liczba\_pieter\_wyzszych = liczba\_pieter - 1

wys\_powyzej\_ft = liczba\_pieter\_wyzszych \* wys\_standard\_pietra\_ft

wysokosc\_calkowita\_ft = wysokosc\_parteru\_ft + wys\_powyzej\_ft



\# --- Znajdź Poziom IV (level\_iv) wcześniej ---

level\_iv = None

for lvl in levels:

&nbsp;   if "IV" in lvl.Name.upper() or lvl.Name.startswith("4") or "POZIOM 4" in lvl.Name.upper():

&nbsp;       level\_iv = lvl

&nbsp;       break



\# --------------------------------------------------------------------------------------------- wybór typu ściany / kolumny --------------------

wall\_type = None

wall\_type\_generic = None

wall\_type\_first = None



all\_wall\_types = FilteredElementCollector(doc).OfClass(WallType).ToElements()



if all\_wall\_types:

&nbsp;   wall\_type\_first = all\_wall\_types\[0] # Fallback 2 (pierwszy z brzegu)



for wt in all\_wall\_types:

&nbsp;   try:

&nbsp;       name = wt.Name.lower()

&nbsp;   except:

&nbsp;       name = ""

&nbsp;   

&nbsp;   if "brick" in name or "cegła" in name: #priorytetowo wyszukuje cegłę z projektu

&nbsp;       wall\_type = wt

&nbsp;       break # Znaleziono najlepszy

&nbsp;   

&nbsp;   if not wall\_type\_generic and ("generic" in name or "basic" in name or "podstawowa" in name): #jeśli nie znajdzie, to podstawowa ściana

&nbsp;       wall\_type\_generic = wt



if not wall\_type: # Jeśli nie ma "brick"

&nbsp;   wall\_type = wall\_type\_generic # Użyj "generic"

if not wall\_type: # Jeśli nie ma "generic"

&nbsp;   wall\_type = wall\_type\_first # Użyj pierwszego z brzegu



col\_type = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST\_StructuralColumns).FirstElement()



if not wall\_type or not col\_type:

&nbsp;   TaskDialog.Show("Błąd", "Brak typu ściany lub kolumny w projekcie.")

&nbsp;   sys.exit()



\# ----------Wybór typu stropu; na potrzeby projekotwe - identyczny ---

floor\_type = FilteredElementCollector(doc).OfClass(FloorType).FirstElement()

if not floor\_type:

&nbsp;   TaskDialog.Show("Błąd", "Brak typu stropu (FloorType) w projekcie.")

&nbsp;   sys.exit()

&nbsp;   

\# -------------------------------------------------------------------------------------------------------- transakcja --------------------



\# --- DODANO: Funkcja pomocnicza do tworzenia stropów ---

def create\_floor\_from\_curves(curves\_list, level, f\_type, height\_offset=0.0): #definiowanie kształtu stropu

&nbsp;   """

&nbsp;   Tworzy strop na podanym poziomie z listy krzywych (Lines lub Arcs).

&nbsp;   Krzywe MUSZĄ tworzyć zamkniętą pętlę w odpowiedniej kolejności.

&nbsp;   """

&nbsp;   try:

&nbsp;       loop = CurveLoop() #tworzy pusty kontener na pętlę krzywych

&nbsp;       for c in curves\_list:

&nbsp;           if c and c.Length > 0.001: # Zabezpieczenie

&nbsp;               loop.Append(c)

&nbsp;       

&nbsp;       if loop.IsOpen():

&nbsp;           print("Ostrzeżenie: Pętla dla stropu na poziomie '{}' jest otwarta. Pomijam.".format(level.Name))

&nbsp;           return None



&nbsp;       profile = List\[CurveLoop]()

&nbsp;       profile.Add(loop)

&nbsp;       

&nbsp;       floor = Floor.Create(doc, profile, f\_type.Id, level.Id) #Tworzy nowe stropy w obrębie obrysów

&nbsp;       

&nbsp;       if floor and height\_offset != 0.0: #to jest zawsze ustawione jako strop tworzący się na ostatnim piętrze --> zawiera offset od punktu bazowego

&nbsp;           offset\_param = floor.get\_Parameter(BuiltInParameter.FLOOR\_HEIGHTABOVELEVEL\_PARAM)

&nbsp;           if offset\_param:

&nbsp;               offset\_param.Set(height\_offset)

&nbsp;       return floor

&nbsp;   except Exception as e:

&nbsp;       print("Błąd tworzenia stropu na poziomie {}: {}".format(level.Name, e))

&nbsp;       return None

&nbsp;       

\# ---------------------------------------------------------------------rozpoczęcie tranzakcji------------



t = Transaction(doc, "Generatywny budynek z bezpiecznymi offsetami")

t.Start()



if not col\_type.IsActive:

&nbsp;   col\_type.Activate()

&nbsp;   doc.Regenerate()



\# -------------------------------------------------------------------------------------------------Pętla I - budynki główne (linie proste) --------------------

for line\_id in line\_ids:

&nbsp;   try:

&nbsp;       line\_elem = doc.GetElement(line\_id) #metoda pobiera element z bazy danych na podstawie jego ID 

&nbsp;       if not line\_elem or not hasattr(line\_elem, "Location"):

&nbsp;           continue

&nbsp;       curve = line\_elem.Location.Curve #tu zwraca faktyczną geometrię

&nbsp;       if not curve:

&nbsp;           continue



&nbsp;       start = curve.GetEndPoint(0) #zwraca punkt startowy lub kończowy jako wartość XYZ

&nbsp;       end = curve.GetEndPoint(1) #reprezentacja punktu 3D lub wektoru

&nbsp;       direction = (end - start).Normalize() #skaluje obiekt tak, aby miał długość 1

&nbsp;       normal = XYZ(-direction.Y, direction.X, 0).Normalize() #nadanie głębokości, tworzy nowy wektor obrócony o 90 stopni od "direction" 

&nbsp;       

&nbsp;       if line\_id.Value in ids\_do\_odwrocenia:

&nbsp;           normal = -normal



&nbsp;       length = curve.Length

&nbsp;       if length <= 0.0:

&nbsp;           print("Pominięto linię {}: długość 0.".format(line\_id.Value))

&nbsp;           continue



&nbsp;       num\_cols = int(length / col\_spacing\_ft) + 1



&nbsp;       # kolumny

&nbsp;       for i in range(num\_cols):

&nbsp;           p = start + direction \* (i \* col\_spacing\_ft)

&nbsp;           col = doc.Create.NewFamilyInstance(p, col\_type, poziom\_0, Structure.StructuralType.Column)

&nbsp;           h = col.LookupParameter("Unconnected Height")

&nbsp;           if h: h.Set(wysokosc\_parteru\_ft)



&nbsp;       for i in range(num\_cols - 1):

&nbsp;           p = start + direction \* ((i + 0.5) \* col\_spacing\_ft) + normal \* col\_depth\_ft

&nbsp;           col = doc.Create.NewFamilyInstance(p, col\_type, poziom\_0, Structure.StructuralType.Column)

&nbsp;           h = col.LookupParameter("Unconnected Height")

&nbsp;           if h: h.Set(wysokosc\_parteru\_ft)



&nbsp;       # parter - ściany (cztery boki)

&nbsp;       glebokosc\_do\_uzycia\_ft = calkowita\_glebokosc\_ft

&nbsp;       if line\_id.Value == 1267677:

&nbsp;           glebokosc\_do\_uzycia\_ft = calkowita\_glebokosc\_ft \* 1.10



&nbsp;       p1\_dol = start + normal \* glebokosc\_kolumn\_ft

&nbsp;       p2\_dol = end + normal \* glebokosc\_kolumn\_ft

&nbsp;       p3\_dol = end + normal \* glebokosc\_do\_uzycia\_ft

&nbsp;       p4\_dol = start + normal \* glebokosc\_do\_uzycia\_ft



&nbsp;       for a, b in \[(p1\_dol, p2\_dol), (p2\_dol, p3\_dol), (p3\_dol, p4\_dol), (p4\_dol, p1\_dol)]:

&nbsp;           if a.IsAlmostEqualTo(b):

&nbsp;               continue

&nbsp;           try:

&nbsp;               Wall.Create(doc, Line.CreateBound(a, b), wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;           except Exception as e:

&nbsp;               print("Nie utworzono ściany parteru (linia {}): {}".format(line\_id.Value, e))



&nbsp;       # piętra

&nbsp;       p1\_gora = start

&nbsp;       p2\_gora = end

&nbsp;       p3\_gora = end + normal \* glebokosc\_do\_uzycia\_ft

&nbsp;       p4\_gora = start + normal \* glebokosc\_do\_uzycia\_ft

&nbsp;       for a, b in \[(p1\_gora, p2\_gora), (p2\_gora, p3\_gora), (p3\_gora, p4\_gora), (p4\_gora, p1\_gora)]:

&nbsp;           if a.IsAlmostEqualTo(b):

&nbsp;               continue

&nbsp;           try:

&nbsp;               Wall.Create(doc, Line.CreateBound(a, b), wall\_type.Id, poziom\_1.Id, wys\_powyzej\_ft, 0.0, False, False)

&nbsp;           except Exception as e:

&nbsp;               print("Nie utworzono ściany pięter (linia {}): {}".format(line\_id.Value, e))



&nbsp;       # --- DODANO: Strop dla pięter (na poziomie IV, jako "dach" bryły 1-III / podłoga IV) ---

&nbsp;       if level\_iv: # Używamy poziomu IV jako dachu dla bryły I-III

&nbsp;           floor\_curves = List\[Curve]()

&nbsp;           floor\_curves.Add(Line.CreateBound(p1\_gora, p2\_gora))

&nbsp;           floor\_curves.Add(Line.CreateBound(p2\_gora, p3\_gora))

&nbsp;           floor\_curves.Add(Line.CreateBound(p3\_gora, p4\_gora))

&nbsp;           floor\_curves.Add(Line.CreateBound(p4\_gora, p1\_gora))

&nbsp;           create\_floor\_from\_curves(floor\_curves, level\_iv, floor\_type) # To jest strop na 12m

&nbsp;       # --- KONIEC DODANO ---



&nbsp;   except Exception as e:

&nbsp;       print("Błąd w linii {}: {}".format(line\_id.Value, e))



\# -------------------------------------------------------------------------------------------------- dodatkowa kondygnacja IV (bez rollback) --------------------

wys\_dodatkowej\_kondygnacji\_m = 4.0 #wskazanie wysokości

wys\_dodatkowej\_kondygnacji\_ft = wys\_dodatkowej\_kondygnacji\_m \* foot #konwersja jednostek

linie\_dodatkowej\_kondygnacji = \[ElementId(1265253), ElementId(1268120), ElementId(1278942)] #tworzą sie na jej podstawie



if level\_iv: #rozpoczyna pętlę dla Level IV

&nbsp;   for line\_id in linie\_dodatkowej\_kondygnacji:

&nbsp;       try: #zabezpieczenie, kiedy linia nie jest elementem liniowym, np krzywa lub jej brak, przeskakuje i kod idzie dalej

&nbsp;           line\_elem = doc.GetElement(line\_id)

&nbsp;           if not line\_elem or not hasattr(line\_elem, "Location"):

&nbsp;               print("Pominięto linię IV (brak elementu): {}".format(line\_id.Value))

&nbsp;               continue

&nbsp;           curve = line\_elem.Location.Curve

&nbsp;           if not curve:

&nbsp;               print("Pominięto linię IV (brak geometrii): {}".format(line\_id.Value))

&nbsp;               continue



&nbsp;           start = curve.GetEndPoint(0) #lokalizauje punkt XYZ

&nbsp;           end = curve.GetEndPoint(1) #lokalizauje punkt XYZ

&nbsp;           direction = (end - start).Normalize() #stwarza możliwość wektora kierunkowego

&nbsp;           normal = XYZ(-direction.Y, direction.X, 0).Normalize() #wektor prostopadły, stwarza kierunek odwrócenia

&nbsp;           if line\_id.Value in ids\_do\_odwrocenia or line\_id.Value == 1278942: #odwraca ten kierunek

&nbsp;               normal = -normal



&nbsp;           p1 = start + normal \* cofniecie\_iv\_ft # frontowe, oblicza narożniki podstawy, które są odsunięte o daną wartość "odsunięcia kondygnacji"

&nbsp;           p2 = end + normal \* cofniecie\_iv\_ft #frontowe

&nbsp;           p3 = end + normal \* calkowita\_glebokosc\_ft # tylne narożniki odsunięte od linii bazowej o wartość cofnięcia 

&nbsp;           p4 = start + normal \* calkowita\_glebokosc\_ft #tylne 



&nbsp;           for a, b in \[(p1, p2), (p2, p3), (p3, p4), (p4, p1)]: #pętla która tworzy 4 ściany 

&nbsp;               if a.IsAlmostEqualTo(b): #zabezpieczenie aby nie tworzyć ściany o długości 0

&nbsp;                   continue

&nbsp;               try: #tworzy nową ścianę 

&nbsp;                   Wall.Create(doc, Line.CreateBound(a, b), wall\_type.Id, level\_iv.Id, #w danym dokumencie; wzdłuż wybranej krzywej, ze ścianą o danym ID; która jest na poziomie IV; o wysokości 4m

&nbsp;                               wys\_dodatkowej\_kondygnacji\_ft, 0.0, False, False) #offset, flip, structural

&nbsp;               except Exception as e:

&nbsp;                   print("Nie utworzono ściany IV (linia {}): {}".format(line\_id.Value, e))



&nbsp;           floor\_curves\_iv = List\[Curve]() #dodanie stropu dachowego --> obrys stworzony na podstawie obrysu ścian

&nbsp;           floor\_curves\_iv.Add(Line.CreateBound(p1, p2))

&nbsp;           floor\_curves\_iv.Add(Line.CreateBound(p2, p3))

&nbsp;           floor\_curves\_iv.Add(Line.CreateBound(p3, p4))

&nbsp;           floor\_curves\_iv.Add(Line.CreateBound(p4, p1))

&nbsp;           create\_floor\_from\_curves(floor\_curves\_iv, level\_iv, floor\_type, wys\_dodatkowej\_kondygnacji\_ft) #tworzenie danego stropu na poziomie IV ale z offsetem na wysokości 12 + 4 = 16 m



&nbsp;       except Exception as e: #wyszukuje błąd w całej pętli

&nbsp;           print("Błąd kondygnacji IV (linia {}): {}".format(line\_id.Value, e))

else:

&nbsp;   TaskDialog.Show("Uwaga", "Nie znaleziono poziomu 'IV'. Kondygnacja nie została utworzona.")



\# ----------------------------------------------------------------------------------------------------------------------- audytorium --------------------

wysokosc\_audytorium\_6m\_ft = 6.0 \* foot #konwersja jednostek

ids\_audytorium\_6m = \[1283599, 1283696, 1285389, 1285445]



for auditorium\_line\_id in auditorium\_line\_ids: #rozpoczęcie po wszystkich liniach zdefiniowanych jako audytorium

&nbsp;   try:

&nbsp;       line\_elem = doc.GetElement(auditorium\_line\_id) #pobranie geometrii z projektu

&nbsp;       if not line\_elem or not hasattr(line\_elem, "Location"):

&nbsp;           continue

&nbsp;       curve = line\_elem.Location.Curve

&nbsp;       if not curve:

&nbsp;           continue



&nbsp;       glebokosc\_audytorium\_do\_uzycia\_ft = calkowita\_glebokosc\_ft #ustawienie głębokości domyślnej na pelną głębokość budynku oraz użycie głębokości podanej przez użytkownika

&nbsp;       if auditorium\_line\_id.Value == 1283599:

&nbsp;           glebokosc\_audytorium\_do\_uzycia\_ft = glebokosc\_audytorium\_ns\_ft

&nbsp;       elif auditorium\_line\_id.Value == 1283696:

&nbsp;           glebokosc\_audytorium\_do\_uzycia\_ft = glebokosc\_audytorium\_35m\_ft



&nbsp;       wysokosc\_do\_uzycia = wysokosc\_audytorium\_6m\_ft if auditorium\_line\_id.Value in ids\_audytorium\_6m else wysokosc\_calkowita\_ft #sprawdza czy dane ID znajduje się na liście



&nbsp;       if isinstance(curve, Line):

&nbsp;           start = curve.GetEndPoint(0)

&nbsp;           end = curve.GetEndPoint(1)

&nbsp;           direction = (end - start).Normalize()

&nbsp;           normal = XYZ(-direction.Y, direction.X, 0).Normalize()

&nbsp;           normal = -normal

&nbsp;           p1 = start

&nbsp;           p2 = end

&nbsp;           p3 = end + normal \* glebokosc\_audytorium\_do\_uzycia\_ft

&nbsp;           p4 = start + normal \* glebokosc\_audytorium\_do\_uzycia\_ft

&nbsp;           for a, b in \[(p1, p2), (p2, p3), (p3, p4), (p4, p1)]: #tworzy 4 ściany na poziomie o obliczonej wysokości - wysokość do użycia

&nbsp;               if a.IsAlmostEqualTo(b):

&nbsp;                   continue

&nbsp;               try:

&nbsp;                   Wall.Create(doc, Line.CreateBound(a, b), wall\_type.Id, poziom\_0.Id, wysokosc\_do\_uzycia, 0.0, False, False)

&nbsp;               except Exception as e:

&nbsp;                   print("Nie utworzono ściany audytorium (linia {}): {}".format(auditorium\_line\_id.Value, e))



&nbsp;           # --- ZMODYFIKOWANO: Strop nad audytorium (POPRAWKA DLA 1282579) ---

&nbsp;           if auditorium\_line\_id.Value in ids\_audytorium\_6m: # Jeśli ściany mają wysokość 6m to zpiera krzywe p1-p4 i tworzy strop na poziomie 0 z offsetem 6 m

&nbsp;               floor\_curves\_aud = List\[Curve]()

&nbsp;               floor\_curves\_aud.Add(Line.CreateBound(p1, p2))

&nbsp;               floor\_curves\_aud.Add(Line.CreateBound(p2, p3))

&nbsp;               floor\_curves\_aud.Add(Line.CreateBound(p3, p4))

&nbsp;               floor\_curves\_aud.Add(Line.CreateBound(p4, p1))

&nbsp;               # Tworzymy na poziomie 0, ale z offsetem 6m

&nbsp;               create\_floor\_from\_curves(floor\_curves\_aud, poziom\_0, floor\_type, wysokosc\_audytorium\_6m\_ft)

&nbsp;           else: # Dla pozostałych (w tym 1282579), które mają wysokość 12m

&nbsp;               if level\_iv: # Sprawdźmy czy poziom IV istnieje

&nbsp;                   floor\_curves\_aud = List\[Curve]()

&nbsp;                   floor\_curves\_aud.Add(Line.CreateBound(p1, p2))

&nbsp;                   floor\_curves\_aud.Add(Line.CreateBound(p2, p3))

&nbsp;                   floor\_curves\_aud.Add(Line.CreateBound(p3, p4))

&nbsp;                   floor\_curves\_aud.Add(Line.CreateBound(p4, p1))

&nbsp;                   # Tworzymy na poziomie IV (12m) bez offsetu

&nbsp;                   create\_floor\_from\_curves(floor\_curves\_aud, level\_iv, floor\_type, 0.0)

&nbsp;           # --- KONIEC ZMODYFIKOWANO ---



&nbsp;       elif isinstance(curve, Arc): #tworzenie obrysu dla łuków polega na utworzeniu dwóch łuków i domknięcie ich krańców prostymi liniami 

&nbsp;           offset\_sign = -1.0

&nbsp;           radius\_ft = curve.Radius

&nbsp;           if glebokosc\_audytorium\_do\_uzycia\_ft >= (radius\_ft - 0.1):

&nbsp;               print("Pominięto łuk audytorium {}: głębokość >= promień.".format(auditorium\_line\_id.Value))

&nbsp;               continue



&nbsp;           arc\_front = curve

&nbsp;           arc\_back = curve.CreateOffset(offset\_sign \* glebokosc\_audytorium\_do\_uzycia\_ft, XYZ.BasisZ)

&nbsp;           if (arc\_front is None) or (arc\_back is None):

&nbsp;               print("Pominięto audytorium (offsety) dla łuku {}".format(auditorium\_line\_id.Value))

&nbsp;               continue



&nbsp;           try: #tworzy 4 ściany --> dwa łuki i dwie linie proste

&nbsp;               Wall.Create(doc, arc\_front, wall\_type.Id, poziom\_0.Id, wysokosc\_do\_uzycia, 0.0, False, False)

&nbsp;               Wall.Create(doc, arc\_back, wall\_type.Id, poziom\_0.Id, wysokosc\_do\_uzycia, 0.0, False, False)

&nbsp;               Wall.Create(doc, Line.CreateBound(arc\_front.GetEndPoint(0), arc\_back.GetEndPoint(0)), wall\_type.Id, poziom\_0.Id, wysokosc\_do\_uzycia, 0.0, False, False)

&nbsp;               Wall.Create(doc, Line.CreateBound(arc\_front.GetEndPoint(1), arc\_back.GetEndPoint(1)), wall\_type.Id, poziom\_0.Id, wysokosc\_do\_uzycia, 0.0, False, False)

&nbsp;           except Exception as e:

&nbsp;               print("Nie utworzono ścian audytorium (łuk {}): {}".format(auditorium\_line\_id.Value, e))



&nbsp;           if auditorium\_line\_id.Value in ids\_audytorium\_6m: # Dla tych o wysokości 6m, z 'arc\_front' i 'arc\_back' do def kształtu i stwarza strop na poziomie 0 z offsetem 6m

&nbsp;               floor\_curves\_aud\_arc = List\[Curve]()

&nbsp;               floor\_curves\_aud\_arc.Add(arc\_front)

&nbsp;               floor\_curves\_aud\_arc.Add(Line.CreateBound(arc\_front.GetEndPoint(1), arc\_back.GetEndPoint(1)))

&nbsp;               floor\_curves\_aud\_arc.Add(arc\_back.CreateReversed()) # Ważne: odwrócony łuk

&nbsp;               floor\_curves\_aud\_arc.Add(Line.CreateBound(arc\_back.GetEndPoint(0), arc\_front.GetEndPoint(0)))

&nbsp;               create\_floor\_from\_curves(floor\_curves\_aud\_arc, poziom\_0, floor\_type, wysokosc\_audytorium\_6m\_ft)

&nbsp;           else: # Dla pozostałych (12m)

&nbsp;               if level\_iv:

&nbsp;                   floor\_curves\_aud\_arc = List\[Curve]()

&nbsp;                   floor\_curves\_aud\_arc.Add(arc\_front)

&nbsp;                   floor\_curves\_aud\_arc.Add(Line.CreateBound(arc\_front.GetEndPoint(1), arc\_back.GetEndPoint(1)))

&nbsp;                   floor\_curves\_aud\_arc.Add(arc\_back.CreateReversed())

&nbsp;                   floor\_curves\_aud\_arc.Add(Line.CreateBound(arc\_back.GetEndPoint(0), arc\_front.GetEndPoint(0)))

&nbsp;                   # Tworzymy na poziomie IV (12m) bez offsetu

&nbsp;                   create\_floor\_from\_curves(floor\_curves\_aud\_arc, level\_iv, floor\_type, 0.0)

&nbsp;           # --- KONIEC ZMODYFIKOWANO ---

&nbsp;   except Exception as e:

&nbsp;       print("Błąd audytorium (linia {}): {}".format(auditorium\_line\_id.Value, e))



\# ------------------------------------------------------------------------------------------------------------------ łuki łączące (bezpieczne offsety) --------------------

adjusted\_arcs = \[]

buffer\_ft = 0.2  # większy bufor niż wcześniej (ok. 6 cm), żeby uniknąć równości promienia/offset --> unjoin



for arc\_id in arc\_ids:

&nbsp;   try:

&nbsp;       arc\_elem = doc.GetElement(arc\_id)

&nbsp;       if not arc\_elem or not hasattr(arc\_elem, "Location"):

&nbsp;           continue

&nbsp;       curve = arc\_elem.Location.Curve

&nbsp;       if not isinstance(curve, Arc):

&nbsp;           continue



&nbsp;       radius\_ft = curve.Radius #pobieranie geomoerii łuku

&nbsp;       length = curve.Length

&nbsp;       if length <= 0.0:

&nbsp;           print("Pominięto łuk {}: długość 0.".format(arc\_id.Value))

&nbsp;           continue



&nbsp;       # jeśli całkowita głębokość >= radius - buffer -> przycinamy do safe depth

&nbsp;       if calkowita\_glebokosc\_ft >= (radius\_ft - buffer\_ft):

&nbsp;           effective\_depth\_ft = max(0.0, radius\_ft - buffer\_ft)

&nbsp;           if effective\_depth\_ft <= 0.01:

&nbsp;               print("Pominięto łuk {}: efektywna głębokość zbyt mała.".format(arc\_id.Value))

&nbsp;               continue

&nbsp;           adjusted\_arcs.append((arc\_id.Value, calkowita\_glebokosc\_ft / foot, effective\_depth\_ft / foot)) #zapisanie informacji o modyfikacji do dziennika

&nbsp;           depth\_for\_use\_ft = effective\_depth\_ft #używanie bezpiecznej głębokości do dalszych obliczeń

&nbsp;       else:

&nbsp;           depth\_for\_use\_ft = calkowita\_glebokosc\_ft #jeśli głebokość była mniejsza niż promień to używaj pełnej głębokości



&nbsp;       offset\_sign = -1.0 #zwrócenie odsunięcia do wewnątrz 



&nbsp;       num\_cols = int(length / col\_spacing\_ft) + 1 #obliczenie ile się zmieści słupów 



&nbsp;       for i in range(num\_cols): #tworzenie kolumn na łuku (pierwszy rząd)

&nbsp;           param = (i \* col\_spacing\_ft) / length

&nbsp;           if param < 0.0: param = 0.0

&nbsp;           if param > 1.0: param = 1.0

&nbsp;           p = curve.Evaluate(param, True) # Pobiera punkt XYZ na łuku na podstawie znormalizowanego parametru

&nbsp;           col = doc.Create.NewFamilyInstance(p, col\_type, poziom\_0, Structure.StructuralType.Column)

&nbsp;           h = col.LookupParameter("Unconnected Height")

&nbsp;           if h: h.Set(wysokosc\_parteru\_ft)



&nbsp;       offset\_curve\_cols = None # drugi rząd kolumn (odsunięty)

&nbsp;       try:

&nbsp;           offset\_curve\_cols = curve.CreateOffset(offset\_sign \* col\_depth\_ft, XYZ.BasisZ) # Stwórz nowy, tymczasowy łuk odsunięty do wewnątrz o 'col\_depth\_ft'

&nbsp;       except:

&nbsp;           offset\_curve\_cols = None # Błąd: offset pewnie > promień



&nbsp;       if offset\_curve\_cols:

&nbsp;           for i in range(num\_cols - 1):

&nbsp;               param = ((i + 0.5) \* col\_spacing\_ft) / length # Przesunięte

&nbsp;               if param < 0.0: param = 0.0

&nbsp;               if param > 1.0: param = 1.0

&nbsp;               p = offset\_curve\_cols.Evaluate(param, True) # Pobierz punkt XYZ, ale tym razem z 'offset\_curve\_cols'

&nbsp;               col = doc.Create.NewFamilyInstance(p, col\_type, poziom\_0, Structure.StructuralType.Column)

&nbsp;               h = col.LookupParameter("Unconnected Height")

&nbsp;               if h: h.Set(wysokosc\_parteru\_ft)



&nbsp;       desired\_front\_offset = offset\_sign \* glebokosc\_kolumn\_ft # bezpieczne offsety dla ścian: nie przekraczaj promienia - zostaw buffer

&nbsp;       desired\_back\_offset = offset\_sign \* depth\_for\_use\_ft



&nbsp;       safe\_front\_abs = min(abs(desired\_front\_offset), max(0.0, radius\_ft - buffer\_ft)) #ponowne, bezpieczne obliczenie offsetów

&nbsp;       safe\_back\_abs = min(abs(desired\_back\_offset), max(0.0, radius\_ft - buffer\_ft))



&nbsp;       # jeśli safe offsety zbyt małe -> pominąć tworzenie po łuku

&nbsp;       if safe\_front\_abs <= 0.01 or safe\_back\_abs <= 0.01:

&nbsp;           print("Pominięto tworzenie ścian dla łuku {}: safe offset zbyt mały.".format(arc\_id.Value))

&nbsp;           continue



&nbsp;       try: #stworzenie końcowych łuków dla ścian

&nbsp;           arc\_front = curve.CreateOffset(-1.0 \* safe\_front\_abs, XYZ.BasisZ)

&nbsp;       except:

&nbsp;           arc\_front = None

&nbsp;       try:

&nbsp;           arc\_back = curve.CreateOffset(-1.0 \* safe\_back\_abs, XYZ.BasisZ)

&nbsp;       except:

&nbsp;           arc\_back = None



&nbsp;       if (arc\_front is None) or (arc\_back is None):

&nbsp;           print("Pominięto łuk {}: nie udało się utworzyć offsetów (arc\_front/arc\_back None).".format(arc\_id.Value))

&nbsp;           continue



&nbsp;       if arc\_front.Length < 0.001 or arc\_back.Length < 0.001: # pomijaj jeśli długość offsetów znikoma

&nbsp;           print("Pominięto łuk {}: offsety mają zbyt małą długość.".format(arc\_id.Value))

&nbsp;           continue



&nbsp;       try: # tworzenie ścian parteru po łuku

&nbsp;           Wall.Create(doc, arc\_front, wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;           Wall.Create(doc, arc\_back, wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;       except Exception as e:

&nbsp;           print("Błąd tworzenia ścian parteru dla łuku {}: {}".format(arc\_id.Value, e))

&nbsp;           # próbujemy zmniejszyć safe\_back\_abs i ponowić raz

&nbsp;           reduced = max(0.01, safe\_back\_abs - 0.1)

&nbsp;           try:

&nbsp;               arc\_back\_try = curve.CreateOffset(-1.0 \* reduced, XYZ.BasisZ)

&nbsp;               if arc\_back\_try and arc\_back\_try.Length > 0.001:

&nbsp;                   Wall.Create(doc, arc\_back\_try, wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;           except Exception as e2:

&nbsp;               print("Ponowna próba nieudana dla łuku {}: {}".format(arc\_id.Value, e2))



&nbsp;       try: # łączące końcowe odcinki (zaślepki)

&nbsp;           a0 = arc\_front.GetEndPoint(0)

&nbsp;           b0 = arc\_back.GetEndPoint(0)

&nbsp;           a1 = arc\_front.GetEndPoint(1)

&nbsp;           b1 = arc\_back.GetEndPoint(1)

&nbsp;           if not a0.IsAlmostEqualTo(b0):

&nbsp;               Wall.Create(doc, Line.CreateBound(a0, b0), wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;           if not a1.IsAlmostEqualTo(b1):

&nbsp;               Wall.Create(doc, Line.CreateBound(a1, b1), wall\_type.Id, poziom\_0.Id, wysokosc\_parteru\_ft, 0.0, False, False)

&nbsp;       except Exception as e:

&nbsp;           print("Błąd zamknięć parteru łuku {}: {}".format(arc\_id.Value, e))



&nbsp;       try: # piętra - podobnie z bezpiecznym offsetem

&nbsp;           arc\_back\_floor = curve.CreateOffset(-1.0 \* safe\_back\_abs, XYZ.BasisZ)

&nbsp;           # utwórz front jako sam krzywa bazowa (curve)

&nbsp;           if arc\_back\_floor and arc\_back\_floor.Length > 0.001:

&nbsp;               try:

&nbsp;                   Wall.Create(doc, curve, wall\_type.Id, poziom\_1.Id, wys\_powyzej\_ft, 0.0, False, False)

&nbsp;                   Wall.Create(doc, arc\_back\_floor, wall\_type.Id, poziom\_1.Id, wys\_powyzej\_ft, 0.0, False, False)

&nbsp;                   # łączące

&nbsp;                   if not curve.GetEndPoint(0).IsAlmostEqualTo(arc\_back\_floor.GetEndPoint(0)):

&nbsp;                       Wall.Create(doc, Line.CreateBound(curve.GetEndPoint(0), arc\_back\_floor.GetEndPoint(0)), wall\_type.Id, poziom\_1.Id, wys\_powyzej\_ft, 0.0, False, False)

&nbsp;                   if not curve.GetEndPoint(1).IsAlmostEqualTo(arc\_back\_floor.GetEndPoint(1)):

&nbsp;                       Wall.Create(doc, Line.CreateBound(curve.GetEndPoint(1), arc\_back\_floor.GetEndPoint(1)), wall\_type.Id, poziom\_1.Id, wys\_powyzej\_ft, 0.0, False, False)

&nbsp;               except Exception as e:

&nbsp;                   print("Błąd tworzenia piętra dla łuku {}: {}".format(arc\_id.Value, e))

&nbsp;       except Exception as e:

&nbsp;           print("Błąd offsetowania piętra dla łuku {}: {}".format(arc\_id.Value, e))



&nbsp;       if level\_iv: #Strop dla pięter (na poziomie IV, jako "dach" bryły 1-III) ---

&nbsp;           try:

&nbsp;               floor\_curves\_arc\_12m = List\[Curve]() 

&nbsp;               floor\_curves\_arc\_12m.Add(curve) # 1. Dodaj przedni łuk (oryginalna linia bazowa)

&nbsp;               floor\_curves\_arc\_12m.Add(Line.CreateBound(curve.GetEndPoint(1), arc\_back\_floor.GetEndPoint(1))) # 2. Dodaj boczną zaślepkę 1 (prostą linię)

&nbsp;               floor\_curves\_arc\_12m.Add(arc\_back\_floor.CreateReversed()) # 3. Dodaj tylny łuk (odsunięty I ODWRÓCONY)

&nbsp;               floor\_curves\_arc\_12m.Add(Line.CreateBound(arc\_back\_floor.GetEndPoint(0), curve.GetEndPoint(0))) # 4. Dodaj boczną zaślepkę 2 (prostą linię)

&nbsp;               create\_floor\_from\_curves(floor\_curves\_arc\_12m, level\_iv, floor\_type) # Wywołaj funkcję pomocniczą z gotowym profilem

&nbsp;           except Exception as e:

&nbsp;               print("Błąd tworzenia stropu 12m (łuk {}) {}".format(arc\_id.Value, e))



&nbsp;   except Exception as e:

&nbsp;       print("Nie udało się przetworzyć łuku {}: {}".format(arc\_id.Value, e))



\# -------------------------------------------------------------------------------------------------------------- dodatkowa kondygnacja 4 m nad łukami --------------------

try: # znajdź poziom "IV level"

&nbsp;   poziom\_IV = None #ustawienie "pustej zmiennej"

&nbsp;   for lvl in FilteredElementCollector(doc).OfClass(Level): #szukanie poziomów w dokumencie 

&nbsp;       lvl\_name\_upper = lvl.Name.upper() #pobranie nazwy poziomu i zamiana na wielkie litery

&nbsp;       if "IV" in lvl\_name\_upper or "POZIOM 4" in lvl\_name\_upper or lvl\_name\_upper.startswith("4"): #dokladne, elastyczne wyszukiwanie, znajduje poziom który ma w nazwie VI, POZIOM 4  lub zaczyna się od 4

&nbsp;           poziom\_IV = lvl # Znaleziono! Przypisz obiekt 'Level' do zmiennej

&nbsp;           break



&nbsp;   if poziom\_IV is None: #jeśli pętla nie znalazła poziomu 4 w dokumencie 

&nbsp;       TaskDialog.Show("Błąd", "Nie znaleziono poziomu 'IV' / 'Poziom 4' — pominięto nadbudowę łuków.")

&nbsp;   else:

&nbsp;       wysokosc\_dodatkowej\_kondygnacji\_m = 4.0 # --- Jeśli Poziom IV został znaleziony, kontynuuj ---

&nbsp;       wysokosc\_dodatkowej\_kondygnacji\_ft = wysokosc\_dodatkowej\_kondygnacji\_m \* foot #konwersja jednostek



&nbsp;       for arc\_id in arc\_ids: # Używamy tych samych arc\_ids co dla łuków głównych

&nbsp;           try:

&nbsp;               arc\_elem = doc.GetElement(arc\_id) #standardowe pobranie geometrii łuku

&nbsp;               if not arc\_elem or not hasattr(arc\_elem, "Location"):

&nbsp;                   continue

&nbsp;               curve = arc\_elem.Location.Curve

&nbsp;               if not isinstance(curve, Arc): #jeśli to nie łuk to pomiń

&nbsp;                   continue



&nbsp;               radius\_ft = curve.Radius #pobierz promień łuku

&nbsp;               if radius\_ft <= 0.0:

&nbsp;                   continue

&nbsp;                   

&nbsp;               buffer\_ft = 0.2 #bezpieczne offsety

&nbsp;               offset\_sign = -1.0

&nbsp;               

&nbsp;               # Obliczamy TYLKO back\_offset, bo front będzie na 'curve'

&nbsp;               back\_offset\_ft = offset\_sign \* calkowita\_glebokosc\_ft # odsunięcie o pełną głębokość budynku

&nbsp;               safe\_back\_abs = min(abs(back\_offset\_ft), max(0.0, radius\_ft - buffer\_ft)) # oblicz maksymalne bezpieczne odsunięcie (promień i bufor)



&nbsp;               # Sprawdzamy tylko 'safe\_back\_abs'

&nbsp;               if safe\_back\_abs <= 0.01:

&nbsp;                   print("Pominięto nadbudowę łuku {}: safe\_back\_abs zbyt mały.".format(arc\_id.Value))

&nbsp;                   continue



&nbsp;               arc\_back = None # utwórz TYLKO tylny łuk

&nbsp;               try:

&nbsp;                   arc\_back = curve.CreateOffset(-1.0 \* safe\_back\_abs, XYZ.BasisZ) #tworzenie nowego łuku odsuniętego o bezpieczną odległość

&nbsp;               except:

&nbsp;                   pass # Błąd offsetu, Zignoruj błąd



&nbsp;               if not arc\_back or arc\_back.Length < 0.001: # Sprawdź, czy 'arc\_back' został pomyślnie utworzony

&nbsp;                   print("Pominięto nadbudowę łuku {}: nie udało się utworzyć arc\_back.".format(arc\_id.Value))

&nbsp;                   continue

&nbsp;               

&nbsp;               Wall.Create(doc, curve, wall\_type.Id, poziom\_IV.Id, wysokosc\_dodatkowej\_kondygnacji\_ft, 0.0, False, False)  # 1. Tworzenie ściany frontowej DOKŁADNIE na 'curve'

&nbsp;               

&nbsp;               Wall.Create(doc, arc\_back, wall\_type.Id, poziom\_IV.Id, wysokosc\_dodatkowej\_kondygnacji\_ft, 0.0, False, False) # 2. Tworzenie ściany tylnej na 'arc\_back'



&nbsp;               a0, b0 = curve.GetEndPoint(0), arc\_back.GetEndPoint(0) # 3. Ściany boczne (Zaślepki), Pobierz punkty startowe (a0, b0) i końcowe (a1, b1) obu łuków

&nbsp;               a1, b1 = curve.GetEndPoint(1), arc\_back.GetEndPoint(1)



&nbsp;               if not a0.IsAlmostEqualTo(b0): # Stwórz ścianę boczną na początku, jeśli punkty się nie pokrywają

&nbsp;                   Wall.Create(doc, Line.CreateBound(a0, b0), wall\_type.Id, poziom\_IV.Id, wysokosc\_dodatkowej\_kondygnacji\_ft, 0.0, False, False)

&nbsp;               if not a1.IsAlmostEqualTo(b1): # Stwórz ścianę boczną na końcu

&nbsp;                   Wall.Create(doc, Line.CreateBound(a1, b1), wall\_type.Id, poziom\_IV.Id, wysokosc\_dodatkowej\_kondygnacji\_ft, 0.0, False, False)



&nbsp;               floor\_curves\_arc\_16m = List\[Curve]() #zbieranie 4 krzywych obrysu dachu 

&nbsp;               floor\_curves\_arc\_16m.Add(curve) # 1. Dodaj przedni łuk ('curve')

&nbsp;               floor\_curves\_arc\_16m.Add(Line.CreateBound(a1, b1)) # 2. Dodaj prawą zaślepkę (linia od a1 do b1)

&nbsp;               floor\_curves\_arc\_16m.Add(arc\_back.CreateReversed()) # 3. Dodaj tylny łuk, ale w ODWROTNYM kierunku, aby zamknąć pętlę

&nbsp;               floor\_curves\_arc\_16m.Add(Line.CreateBound(b0, a0)) # 4. Dodaj lewą zaślepkę (linia od b0 do a0)



&nbsp;               create\_floor\_from\_curves(floor\_curves\_arc\_16m, poziom\_IV, floor\_type, wysokosc\_dodatkowej\_kondygnacji\_ft) #funkcja pomocnicza do profilu tworzenia stropu; o danym profilu, zaczepiony na danym poziomie, z użytym stropem ale odsuniety o 4m



&nbsp;           except Exception as e: # To jest 'except' dla wewnętrznego 'try' - łapie błąd dla JEDNEGO łuku

&nbsp;               print("Błąd przy tworzeniu nadbudowy łuku {}: {}".format(arc\_id.Value, e))



except Exception as e: # To jest 'except' dla zewnętrznego 'try' - łapie błąd np. przy wyszukiwaniu poziomu

&nbsp;   print("Błąd ogólny przy tworzeniu kondygnacji nad łukami:", e)



\# ---------------------------------------------------------------------------------------------------------------- NOWA SEKCJA: ściany specjalne 16m na łukach --------------------

try:

&nbsp;   wysokosc\_16m\_ft = 16.0 \* foot # Ustawia docelową wysokość na 16.0 metrów i konwertuje ją na stopy

&nbsp;   high\_arc\_ids = \[ElementId(1302356), ElementId(1302731)] #definicja nowych łuków



&nbsp;   for arc\_id in high\_arc\_ids:

&nbsp;       try:

&nbsp;           arc\_elem = doc.GetElement(arc\_id) #pobieranie elementu z projektu

&nbsp;           if not arc\_elem or not hasattr(arc\_elem, "Location"): #sprawdznie czy dany element istnieje i czy ma właściwość 'location"

&nbsp;               print("Pominięto łuk 16m (brak elementu): {}".format(arc\_id.Value))

&nbsp;               continue

&nbsp;           curve = arc\_elem.Location.Curve #połącz geometrię czyli krzywą z elementu 

&nbsp;           if not isinstance(curve, Arc):

&nbsp;               print("Pominięto łuk 16m (nie jest łukiem): {}".format(arc\_id.Value))

&nbsp;               continue

&nbsp;           

&nbsp;           if curve.Length < 0.01: #kolejne sprawdzenie czyli czy ma jakąś długość większą od 0

&nbsp;               print("Pominięto łuk 16m (za krótki): {}".format(arc\_id.Value))

&nbsp;               continue



&nbsp;           Wall.Create(doc, curve, wall\_type.Id, poziom\_0.Id, wysokosc\_16m\_ft, 0.0, False, False) # Tworzenie ściany o wysokości 16m na poziomie 0



&nbsp;       except Exception as e: #obsługa dla błędu wewnętrznego

&nbsp;           print("Błąd przy tworzeniu ściany 16m na łuku {}: {}".format(arc\_id.Value, e))



except Exception as e: #obsługa dla błędu całego modułu

&nbsp;   print("Błąd ogólny przy tworzeniu ścian 16m:", e)



\# ----------------------------------------------------------------------------------------------------------------------- OBLICZANIE POWIERZCHNI PARTERU --------------------

import math



pow\_audytorium\_m2 = glebokosc\_audytorium\_ns\_m \* 17.0 # 1. Audytorium; prostokąt: głębokość audytorium (użytkownik) x 17.0 m



pow\_furmanska\_m2 = glebokosc\_budynku\_m \* 72.0 # 2. Bryła od ul. Furmańskiej; prostokąt: głębokość zabudowy za kolumnami x 72 m



pow\_karowa\_luk1\_m2 = (math.pi \* (glebokosc\_budynku\_m \*\* 2)) \* 0.25 #  3. Łuk ul. Furmańska–Karowa, ćwiartka koła o promieniu R = głębokość zabudowy za kolumnami (DB)



pow\_karowa\_m2 = glebokosc\_budynku\_m \* 66.0 # 4. Bryła ul. Karowa; prostokąt: głębokość zabudowy za kolumnami x 66 m



pow\_karowa\_dobra\_luk2\_m2 = (math.pi \* (glebokosc\_budynku\_m \*\* 2)) \* 0.25 # 5. Łuk Karowa–Dobra; ćwiartka koła o promieniu R = głębokość zabudowy za kolumnami (DB)



pow\_dobra\_m2 = glebokosc\_budynku\_m \* 19.0 # 6. Bryła budynku od ul. Dobrej; prostokąt: głębokość zabudowy za kolumnami x 19 m



suma\_parter\_m2 = ( # --- SUMA PARTERU ---

&nbsp;   pow\_audytorium\_m2 +

&nbsp;   pow\_furmanska\_m2 +

&nbsp;   pow\_karowa\_luk1\_m2 +

&nbsp;   pow\_karowa\_m2 +

&nbsp;   pow\_karowa\_dobra\_luk2\_m2 +

&nbsp;   pow\_dobra\_m2

)



pow\_audytorium\_m2 = round(pow\_audytorium\_m2, 2) # Zaokrąglenie wyników do 2 miejsc po przecinku

pow\_furmanska\_m2 = round(pow\_furmanska\_m2, 2)

pow\_karowa\_luk1\_m2 = round(pow\_karowa\_luk1\_m2, 2)

pow\_karowa\_m2 = round(pow\_karowa\_m2, 2)

pow\_karowa\_dobra\_luk2\_m2 = round(pow\_karowa\_dobra\_luk2\_m2, 2)

pow\_dobra\_m2 = round(pow\_dobra\_m2, 2)

suma\_parter\_m2 = round(suma\_parter\_m2, 2)



\# --- RAPORT ---

raport = (

&nbsp;   "POWIERZCHNIA PARTERU (m²)\\n\\n"

&nbsp;   "1. Audytorium: {} m²\\n"

&nbsp;   "2. Bryła od ul. Furmańskiej: {} m²\\n"

&nbsp;   "3. Łuk ul. Furmańska–Karowa (R = {:.2f} m): {} m²\\n"

&nbsp;   "4. Bryła ul. Karowa: {} m²\\n"

&nbsp;   "5. Łuk Karowa–Dobra (R = {:.2f} m): {} m²\\n"

&nbsp;   "6. Bryła ul. Dobrej: {} m²\\n\\n"

&nbsp;   "SUMA PARTERU: {} m²".format(

&nbsp;       pow\_audytorium\_m2,

&nbsp;       pow\_furmanska\_m2,

&nbsp;       glebokosc\_budynku\_m, pow\_karowa\_luk1\_m2,

&nbsp;       pow\_karowa\_m2,

&nbsp;       glebokosc\_budynku\_m, pow\_karowa\_dobra\_luk2\_m2,

&nbsp;       pow\_dobra\_m2,

&nbsp;       suma\_parter\_m2

&nbsp;   )

)



TaskDialog.Show("Powierzchnia zabudowy – Parter", raport)



\# ------------------------------------------------------------------------------------------------------------------ OBLICZANIE POWIERZCHNI I–III PIĘTRA --------------------

import math



\# --- ZMIENNE POMOCNICZE ---

glebokosc\_calkowita\_m = glebokosc\_kolumn\_m + glebokosc\_budynku\_m # Suma głębokości kolumn i zabudowy za kolumnami (wartość generatywna)



pow\_furmanska\_pietro\_m2 = glebokosc\_calkowita\_m \* 72.0 # --- 2.1 Bryła od ul. Furmańskiej ---; Prostokąt: (DK + DB) \* 72 m



pow\_karowa\_luk1\_pietro\_m2 = (math.pi \* (glebokosc\_calkowita\_m \*\* 2)) \* 0.25 # --- 2.2 Łuk ul. Furmańska–Karowa ---; Ćwiartka koła o promieniu R = (DK + DB)



pow\_karowa\_pietro\_m2 = glebokosc\_calkowita\_m \* 66.0 # --- 2.3 Bryła ul. Karowa ---; Prostokąt: (DK + DB) \* 66 m



pow\_karowa\_dobra\_luk2\_pietro\_m2 = (math.pi \* (glebokosc\_calkowita\_m \*\* 2)) \* 0.25 # --- 2.4 Łuk Karowa–Dobra ---; Ćwiartka koła o promieniu R = (DK + DB)



pow\_dobra\_pietro\_m2 = glebokosc\_calkowita\_m \* 19.0 # --- 2.5 Bryła od ul. Dobrej ---; Prostokąt: (DK + DB) \* 19 m



suma\_pietro\_m2 = ( # --- SUMA POWIERZCHNI JEDNEGO PIĘTRA ---

&nbsp;   pow\_furmanska\_pietro\_m2 +

&nbsp;   pow\_karowa\_luk1\_pietro\_m2 +

&nbsp;   pow\_karowa\_pietro\_m2 +

&nbsp;   pow\_karowa\_dobra\_luk2\_pietro\_m2 +

&nbsp;   pow\_dobra\_pietro\_m2

)



suma\_trzy\_pietra\_m2 = suma\_pietro\_m2 \* 3 # --- SUMA TRZECH PIĘTER ---



pow\_furmanska\_pietro\_m2 = round(pow\_furmanska\_pietro\_m2, 2) # --- ZAOKRĄGLENIA ---

pow\_karowa\_luk1\_pietro\_m2 = round(pow\_karowa\_luk1\_pietro\_m2, 2)

pow\_karowa\_pietro\_m2 = round(pow\_karowa\_pietro\_m2, 2)

pow\_karowa\_dobra\_luk2\_pietro\_m2 = round(pow\_karowa\_dobra\_luk2\_pietro\_m2, 2)

pow\_dobra\_pietro\_m2 = round(pow\_dobra\_pietro\_m2, 2)

suma\_pietro\_m2 = round(suma\_pietro\_m2, 2)

suma\_trzy\_pietra\_m2 = round(suma\_trzy\_pietra\_m2, 2)



\# --- RAPORT ---

raport\_pietra = (

&nbsp;   "POWIERZCHNIA I–III PIĘTRA (m²)\\n\\n"

&nbsp;   "1. Bryła od ul. Furmańskiej: {} m²\\n"

&nbsp;   "2. Łuk ul. Furmańska–Karowa (R = {:.2f} m): {} m²\\n"

&nbsp;   "3. Bryła ul. Karowa: {} m²\\n"

&nbsp;   "4. Łuk Karowa–Dobra (R = {:.2f} m): {} m²\\n"

&nbsp;   "5. Bryła od ul. Dobrej: {} m²\\n\\n"

&nbsp;   "Powierzchnia jednego piętra: {} m²\\n"

&nbsp;   "Powierzchnia 3 pięter (I–III): {} m²".format(

&nbsp;       pow\_furmanska\_pietro\_m2,

&nbsp;       glebokosc\_calkowita\_m, pow\_karowa\_luk1\_pietro\_m2,

&nbsp;       pow\_karowa\_pietro\_m2,

&nbsp;       glebokosc\_calkowita\_m, pow\_karowa\_dobra\_luk2\_pietro\_m2,

&nbsp;       pow\_dobra\_pietro\_m2,

&nbsp;       suma\_pietro\_m2,

&nbsp;       suma\_trzy\_pietra\_m2

&nbsp;   )

)



TaskDialog.Show("Powierzchnia – I–III Piętro", raport\_pietra)



\# ----------------------------------------------------------------------------------------------------- OBLICZANIE POWIERZCHNI DODATKOWEJ KONDYGNACJI (IV POZIOM) --------------------

import math



\# --- ZMIENNE POMOCNICZE --- Wzór: (DK + DB - cofnięcie\_IV)

glebokosc\_iv\_m = glebokosc\_kolumn\_m + glebokosc\_budynku\_m - cofniecie\_iv\_m

if glebokosc\_iv\_m < 0:

&nbsp;   glebokosc\_iv\_m = 0  # zabezpieczenie na wypadek nieprawidłowych wartości



glebokosc\_calkowita\_m = glebokosc\_kolumn\_m + glebokosc\_budynku\_m



pow\_furmanska\_iv\_m2 = glebokosc\_iv\_m \* 19.5 # --- 3.1 Bryła od ul. Furmańskiej ---; Prostokąt: (DK + DB - cofnięcie\_IV) \* 19.5 m



pow\_karowa\_luk1\_iv\_m2 = (math.pi \* (glebokosc\_calkowita\_m \*\* 2)) \* 0.25 # --- 3.2 Łuk Furmańska–Karowa ---; Pełne koło o promieniu R = (DK + DB)



pow\_karowa\_iv\_m2 = glebokosc\_iv\_m \* 66.0 # --- 3.3 Bryła ul. Karowa --- Prostokąt: (DK + DB - cofnięcie\_IV) \* 66 m



pow\_karowa\_dobra\_luk2\_iv\_m2 = (math.pi \* (glebokosc\_calkowita\_m \*\* 2)) \* 0.25 # --- 3.4 Łuk Karowa–Dobra ---Pełne koło o promieniu R = (DK + DB)



pow\_dobra\_iv\_m2 = glebokosc\_iv\_m \* 19.0 # --- 3.5 Bryła od ul. Dobrej --- Prostokąt: (DK + DB - cofnięcie\_IV) \* 19 m



suma\_iv\_m2 = ( # --- SUMA POWIERZCHNI IV POZIOMU ---

&nbsp;   pow\_furmanska\_iv\_m2 +

&nbsp;   pow\_karowa\_luk1\_iv\_m2 +

&nbsp;   pow\_karowa\_iv\_m2 +

&nbsp;   pow\_karowa\_dobra\_luk2\_iv\_m2 +

&nbsp;   pow\_dobra\_iv\_m2

)



pow\_furmanska\_iv\_m2 = round(pow\_furmanska\_iv\_m2, 2) # --- ZAOKRĄGLENIA ---

pow\_karowa\_luk1\_iv\_m2 = round(pow\_karowa\_luk1\_iv\_m2, 2)

pow\_karowa\_iv\_m2 = round(pow\_karowa\_iv\_m2, 2)

pow\_karowa\_dobra\_luk2\_iv\_m2 = round(pow\_karowa\_dobra\_luk2\_iv\_m2, 2)

pow\_dobra\_iv\_m2 = round(pow\_dobra\_iv\_m2, 2)

suma\_iv\_m2 = round(suma\_iv\_m2, 2)



\# --- RAPORT ---

raport\_iv = (

&nbsp;   "POWIERZCHNIA DODATKOWEJ KONDYGNACJI (IV POZIOM)\\n\\n"

&nbsp;   "1. Bryła od ul. Furmańskiej: {} m²\\n"

&nbsp;   "2. Łuk Furmańska–Karowa (R = {:.2f} m): {} m²\\n"

&nbsp;   "3. Bryła ul. Karowa: {} m²\\n"

&nbsp;   "4. Łuk Karowa–Dobra (R = {:.2f} m): {} m²\\n"

&nbsp;   "5. Bryła od ul. Dobrej: {} m²\\n\\n"

&nbsp;   "SUMA IV POZIOMU: {} m²".format(

&nbsp;       pow\_furmanska\_iv\_m2,

&nbsp;       glebokosc\_calkowita\_m, pow\_karowa\_luk1\_iv\_m2,

&nbsp;       pow\_karowa\_iv\_m2,

&nbsp;       glebokosc\_calkowita\_m, pow\_karowa\_dobra\_luk2\_iv\_m2,

&nbsp;       pow\_dobra\_iv\_m2,

&nbsp;       suma\_iv\_m2

&nbsp;   )

)



TaskDialog.Show("Powierzchnia – Dodatkowa kondygnacja (IV)", raport\_iv)



\# -------------------------------------------------------------------------------------------------------------- PODSUMOWANIE CAŁKOWITE POWIERZCHNI --------------------



try: # wybranie wszystkich trzech zmiennych

&nbsp;   total\_all\_m2 = suma\_parter\_m2 + suma\_trzy\_pietra\_m2 + suma\_iv\_m2

except:

&nbsp;   total\_all\_m2 = 0.0



total\_all\_m2 = round(total\_all\_m2, 2)



raport\_total = (

&nbsp;   "PODSUMOWANIE POWIERZCHNI ZABUDOWY\\n\\n"

&nbsp;   "Parter: {} m²\\n"

&nbsp;   "I–III piętro (łącznie): {} m²\\n"

&nbsp;   "IV (dodatkowa kondygnacja): {} m²\\n\\n"

&nbsp;   "=== SUMA CAŁKOWITA: {} m² ===".format(

&nbsp;       suma\_parter\_m2,

&nbsp;       suma\_trzy\_pietra\_m2,

&nbsp;       suma\_iv\_m2,

&nbsp;       total\_all\_m2

&nbsp;   )

)



TaskDialog.Show("PODSUMOWANIE CAŁKOWITE", raport\_total)



\# -------------------------------------------------------------------------------------MODUŁ WALIDACJI MPZP – wersja z PBC% i współczynnikiem nadziemia

import math



\# --- Stałe MPZP / parametry działki ---

site\_area\_m2 = 8986.07

max\_building\_coverage\_pct = 0.60  # 60%

max\_building\_area\_m2 = site\_area\_m2 \* max\_building\_coverage\_pct  # 5391.64 m²



min\_PBC\_pct = 0.25  # 25%

min\_PBC\_m2 = site\_area\_m2 \* min\_PBC\_pct  # 2246.52 m²



\# Intensywność zabudowy (całkowita)

I\_min = 1.2

I\_max = 3.2

I\_min\_area = site\_area\_m2 \* I\_min  # 10783.28 m²

I\_max\_area = site\_area\_m2 \* I\_max  # 28755.42 m²



\# Intensywność nadziemia (max 2.0)

I\_nadziem\_max = 2.0



\# Rezerwa na utwardzenia (np. place, chodniki)

paved\_allowance = 1000.00



\# --- Pobranie powierzchni z wcześniejszych modułów ---

try:

&nbsp;   floor\_area = float(round(suma\_pietro\_m2, 2))  # jedno piętro

except:

&nbsp;   floor\_area = 0.0



try:

&nbsp;   three\_floors\_area = float(round(suma\_trzy\_pietra\_m2, 2))

except:

&nbsp;   three\_floors\_area = 0.0



try:

&nbsp;   iv\_area = float(round(suma\_iv\_m2, 2))

except:

&nbsp;   iv\_area = 0.0



try:

&nbsp;   total\_all\_area = float(round(total\_all\_m2, 2))

except:

&nbsp;   total\_all\_area = 0.0



\# ----------------------------------------------------------------------------------- OBLICZENIA -----------------------------------------------------------------------------------



PBC\_current = site\_area\_m2 - floor\_area - paved\_allowance # Powierzchnia biologicznie czynna (PBC)

if PBC\_current < 0:

&nbsp;   PBC\_current = 0.0



PBC\_percent = (PBC\_current / site\_area\_m2) \* 100.0



\# 1️⃣ Maksymalna powierzchnia zabudowy (1 piętro + 1000 m²) ≤ 60% działki

max\_zabudowa\_check\_value = floor\_area + paved\_allowance

ok\_max\_coverage = (max\_zabudowa\_check\_value <= max\_building\_area\_m2 + 1e-6) #notacja naukowa oznaczająca 1x10^-6 --> floating-point errors



\# 2️⃣ Minimalna powierzchnia biologicznie czynna

ok\_min\_PBC = (PBC\_current >= min\_PBC\_m2 - 1e-6)



\# 3️⃣ Intensywność zabudowy całkowita (I)

I\_value = total\_all\_area / site\_area\_m2 if site\_area\_m2 > 0 else 0.0

ok\_intensity = (I\_value >= I\_min - 1e-6) and (I\_value <= I\_max + 1e-6)



\# 4️⃣ Intensywność nadziemia (I\_nadziem)

above\_ground\_area = three\_floors\_area + iv\_area

I\_nadziem\_value = above\_ground\_area / site\_area\_m2 if site\_area\_m2 > 0 else 0.0

ok\_above\_ground = (I\_nadziem\_value <= I\_nadziem\_max + 1e-6)



\# 5️⃣ Wysokość zabudowy (max 16 m)

max\_allowed\_height\_m = 16.0

try:

&nbsp;   wysokosc\_calkowita\_m = float(wysokosc\_calkowita\_ft) / foot

except:

&nbsp;   wysokosc\_calkowita\_m = 0.0

ok\_height = (wysokosc\_calkowita\_m <= max\_allowed\_height\_m + 1e-6)



\# 6️⃣ Linia zabudowy

line\_of\_building\_check = "NIEZWERYFIKOWANA – wymaga analizy geometrii w modelu"



\# --------------------------------------------------------------------- WALIDACJA I RAPORTOWANIE ------------------------------------------------------------



errors = \[]



if not ok\_max\_coverage:

&nbsp;   errors.append(

&nbsp;       "1️⃣ Powierzchnia zabudowy (1 piętro + 1000 m² = {:.2f} m²) "

&nbsp;       "przekracza dopuszczalne 60% działki ({:.2f} m²).".format(

&nbsp;           max\_zabudowa\_check\_value, max\_building\_area\_m2))



if not ok\_min\_PBC:

&nbsp;   errors.append(

&nbsp;       "2️⃣ Powierzchnia biologicznie czynna zbyt mała: {:.2f} m² ({:.2f}%) < {:.2f} m² (25%).".format(

&nbsp;           PBC\_current, PBC\_percent, min\_PBC\_m2))



if not ok\_intensity:

&nbsp;   errors.append(

&nbsp;       "3️⃣ Intensywność zabudowy I = {:.2f} poza zakresem \[{:.2f}, {:.2f}] "

&nbsp;       "(co odpowiada {:.2f}–{:.2f} m²).".format(

&nbsp;           I\_value, I\_min, I\_max, I\_min\_area, I\_max\_area))



if not ok\_above\_ground:

&nbsp;   errors.append(

&nbsp;       "4️⃣ Intensywność nadziemia I = {:.2f} przekracza dopuszczalne {:.2f}.".format(

&nbsp;           I\_nadziem\_value, I\_nadziem\_max))



if not ok\_height:

&nbsp;   errors.append(

&nbsp;       "5️⃣ Wysokość zabudowy {:.2f} m przekracza dopuszczalne {:.2f} m.".format(

&nbsp;           wysokosc\_calkowita\_m, max\_allowed\_height\_m))



\# -------------------------------------------------------------------------WYNIK WALIDACJI

\# -----------------------------------------------------------------------------------



if errors:

&nbsp;   msg = "❌ Wykryto niezgodności z MPZP:\\n\\n"

&nbsp;   for e in errors:

&nbsp;       msg += " - " + e + "\\n"

&nbsp;   msg += "\\n⚠️ Operacja przerwana z powodu naruszeń MPZP."

&nbsp;   TaskDialog.Show("Błąd MPZP – Walidacja", msg)

&nbsp;   t.RollBack()

&nbsp;   sys.exit()



else:

&nbsp;   raport\_mpzp = (

&nbsp;       "✅ WALIDACJA MPZP – WYNIKI\\n\\n"

&nbsp;       "Powierzchnia terenu 6.3 UN: {:.2f} m²\\n"

&nbsp;       "Całkowita powierzchnia zabudowy: {:.2f} m²\\n"

&nbsp;       "───────────────────────────────────────────────────────\\n\\n"

&nbsp;       "1️⃣ Powierzchnia zabudowy: {:.2f} m² / max {:.2f} m² → ZGODNE ✅\\n\\n"

&nbsp;       "2️⃣ Powierzchnia Biologicznie Czynna: {:.2f} m² ({:.2f}%) / min {:.2f} m² (25%) → ZGODNE ✅\\n\\n"

&nbsp;       "3️⃣ Intensywność zabudowy (I): {:.2f} w zakresie \[{:.2f}-{:.2f}] → ZGODNE ✅\\n\\n"

&nbsp;       "4️⃣ Intensywność nadziemia (I): {:.2f} / max {:.2f} → ZGODNE ✅\\n\\n"

&nbsp;       "───────────────────────────────────────────────────────\\n"

&nbsp;   ).format(

&nbsp;       site\_area\_m2,

&nbsp;       total\_all\_area,

&nbsp;       max\_zabudowa\_check\_value, max\_building\_area\_m2,

&nbsp;       PBC\_current, PBC\_percent, min\_PBC\_m2,

&nbsp;       I\_value, I\_min, I\_max,

&nbsp;       I\_nadziem\_value, I\_nadziem\_max

&nbsp;   )



&nbsp;   TaskDialog.Show("✅ Walidacja MPZP – Zgodność", raport\_mpzp)



\# ----------------------------------------------------------------------------------------------- commit ---------------------------------------------------------------------------------------------------------

t.Commit()

TaskDialog.Show("Zakończono", "Generowanie budynków zakończone.")

