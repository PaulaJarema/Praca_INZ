# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import * #import DataBase (elementy modelu (ściany, stropy), parametry, geometrię (linie, punkty) itp.)
from Autodesk.Revit.UI import * #import UserInterface (okna dialogowe, polecenia)
import clr #import Common Language Runtime
import sys #import System (zatrzymanie skryptu w przypadku błędu)

clr.AddReference("Microsoft.VisualBasic") #załadowanie zewnętrznej biblioteki .NET --> Interaction.InputBox
from Microsoft.VisualBasic import Interaction #możliwość .InputBox() --> zbieranie uwagi od użytkownika
from System.Collections.Generic import List #możiwość tworzenia list

doc = __revit__.ActiveUIDocument.Document #aktualnie pobierany projekt Revit
foot = 3.28084  # konwersja ft -> m

# --------------------------------------------------------------------------------------------------------------------------- global parameters -------------------------------------------------------------------------------------------------------------------------------------------------------------
max_glebokosc_m = 25.0
wys_standard_pietra_m = 3.0
wys_standard_pietra_ft = wys_standard_pietra_m * foot
liczba_pieter = 4
cofniecie_lica_m = 2.4
cofniecie_lica_ft = cofniecie_lica_m * foot

# --------------------------------------------------------------------------------------------------------------------------- startup message -------------------------------------------------------------------------------------------------------------------------------------------------------------
main_message = (
    "The urban composition will be created taking into account fixed design parameters, functional assumptions, and formal and legal conditions in accordance with the Local Spatial Development Plan:\n\n"
    "1) Maximum building area: 60%.\n"
    "2) Minimum percentage of biologically active area: 25%.\n"
    "3) Permissible building density: 1,2 – 3,2.\n\n"
    "Additional functional provisions and assumptions:\n\n"
    " - The building's structure will be designed in accordance with its intended functionality for educational services with cultural, catering, or commercial services on the ground floors of the buildings.\n"
    " - The total area of the ground floor may not exceed 60% of the total area of the first floor.\n"
    " - The planning provisions allow for the use of a flat roof.\n\n"
    "Note regarding plots and building lines:\n\n"
    " - For plots No. 7/3, 7/4, and 7/5, the maximum building height is set at 12.0 m.\n"
    " - For plot no. 7/6, the maximum building height is 16.0 m, provided that all other provisions of the local zoning plan are complied with.\n"
    " - The location of building structures is inextricably linked to the location of the applicable building line and the building line that cannot be crossed.\n"
    " - In order to ensure compositional consistency, auxiliary reference geometries have been defined.\n"
    " - Earthworks are prohibited in the vicinity of valuable trees within the crown projection or at a distance of < 3.0 m from the trunk (except for non-invasive methods).\n"
)

TaskDialog.Show("Start", main_message)

# ------------------------------------------------------------------------------------------------------------------ retrieving values from the user --------------------------------------------------------------------------------------------------------------------------------------------------------------
try:
   
    glebokosc_kolumn_m = float(Interaction.InputBox( #DK
        "Depth of the undercut zone [m] (min 6.0, max 20.0)",
        "Depth of the undercut zone", "8.5").replace(',', '.'))
    if not (6.0 <= glebokosc_kolumn_m <= 20.0):
        TaskDialog.Show("Error", "The value the depth of the underpass zone must be between 6.0m and 20.0m.")
        sys.exit()

    glebokosc_budynku_m = float(Interaction.InputBox( #DB
        "Depth of the building behind the columns  [m] (min 6.0, max 20.0)",
        "Depth of the building behind the columns", "8.5").replace(',', '.'))
    if not (6.0 <= glebokosc_budynku_m <= 20.0):
        TaskDialog.Show("Error", "Value The depth of the building structure behind the columns must be between 6.0m a 20.0m.")
        sys.exit()

    col_spacing_m = float(Interaction.InputBox(
        "Axle spacing of columns [m] (min 4.0, max 8.0)",
        "Axle spacing of columns", "5.0").replace(',', '.'))
    if not (4.0 <= col_spacing_m <= 8.0):
        TaskDialog.Show("Error", "The value of the column center distance must be between 4.0 m and 8.0 m.")
        sys.exit()

    cofniecie_iv_m = float(Interaction.InputBox(
        "Withdrawal of the fifth floor into the facade [m] (min 2.4, max 6.0)",
        "Withdrawal of the fifth floor into the facade", "4.5").replace(',', '.'))
    if not (2.4 <= cofniecie_iv_m <= 6.0):
        TaskDialog.Show("Error", "Wartość 'The recess of the fifth floor into the facade must be between 2.4m a 6.0m.")
        sys.exit()

    glebokosc_audytorium_ns_m = float(Interaction.InputBox(
        "The depth of the auditorium area cut into the plot [m] (min 15.0, max 30.0)",
        "The depth of the auditorium area cut into the plot", "20.0").replace(',', '.'))
    if not (15.0 <= glebokosc_audytorium_ns_m <= 30.0):
        TaskDialog.Show("Error", "Wartość 'Value The depth of the auditorium zone must be between 15.0m a 30.0m.")
        sys.exit()

except:
    TaskDialog.Show("Error", "An invalid value has been entered. The script has been terminated.")
    sys.exit()

# validations of local zoning plans; the need to accept “extreme” data ---------------------------------------------------
if glebokosc_kolumn_m + glebokosc_budynku_m > max_glebokosc_m:
    TaskDialog.Show("Non-compliance with the local zoning plan“, ”The total depth exceeds {} m.".format(max_glebokosc_m))
    sys.exit()

min_glebokosc_podcienia_m = (2.0 / 3.0) * glebokosc_budynku_m
if glebokosc_kolumn_m < min_glebokosc_podcienia_m:
    TaskDialog.Show("Non-compliance with the local zoning plan“, ”The total area of the ground floor constitutes more than 60% of the total area of the first floor; The depth of the columns is too small in relation to the depth of the building. (min {:.2f}m).".format(min_glebokosc_podcienia_m))
    sys.exit()

# data operations and unit conversions ---------------------------------------------------------------
col_spacing_ft = col_spacing_m * foot 
col_depth_ft = (glebokosc_kolumn_m / 2.0) * foot
glebokosc_kolumn_ft = glebokosc_kolumn_m * foot
glebokosc_budynku_ft = glebokosc_budynku_m * foot
calkowita_glebokosc_ft = glebokosc_kolumn_ft + glebokosc_budynku_ft
cofniecie_iv_ft = cofniecie_iv_m * foot
glebokosc_audytorium_ns_ft = glebokosc_audytorium_ns_m * foot
glebokosc_audytorium_35m_ft = 35.0 * foot

# ----------------------------------------------------------------------------------------------------------------------------------- Model line and arc ID -----------------------------------------------------------------------------
line_ids = [ElementId(1266833), ElementId(1267037), ElementId(1267137), ElementId(1267259),
            ElementId(1265069), ElementId(1265253), ElementId(1265357), ElementId(1266049),
            ElementId(1266217), ElementId(1267547), ElementId(1267677), ElementId(1268120),
            ElementId(1268276),
            ElementId(1299369), ElementId(1299422), ElementId(1299485), ElementId(1299536),
            ElementId(1303106)
           ]
ids_do_odwrocenia = [1260740, 1265069, 1265253, 1265357, 1266049, 1299485]
arc_ids = [ElementId(1289914), ElementId(1290384)]
auditorium_line_ids = [ElementId(1282579), ElementId(1283599), ElementId(1283696),
                       ElementId(1285389), ElementId(1285445), ElementId(1288166)]

# ------------------------------------------------------------------------------------------------------- levels, internal security, if the minimum number of o had not been created  --------------------
levels = sorted(list(FilteredElementCollector(doc).OfClass(Level)), key=lambda x: x.Elevation) #kolektor przeszukujący cały dokument projektowy, tworzy całą listę ze zmiennymi X jako współżędna
if len(levels) < 2: #wybranie elementu level czyli poziom, sprawdza ile elementów znajduej się na liście "levels" --> obliczanie wysokości parteru (jeden poziom lub zadnego --> wróba dowołania przerwie się błędem)
    TaskDialog.Show("Error“, ”The project must contain at least two levels.")
    sys.exit()
poziom_0 = levels[0] #przypisanie poziomów do zmiennych
poziom_1 = levels[1]
wysokosc_parteru_ft = poziom_1.Elevation - poziom_0.Elevation #obliczanie na jakiej wysokości jest ściana (jedna kondygnacja)
liczba_pieter_wyzszych = liczba_pieter - 1
wys_powyzej_ft = liczba_pieter_wyzszych * wys_standard_pietra_ft
wysokosc_calkowita_ft = wysokosc_parteru_ft + wys_powyzej_ft

# --- Find Level IV (level_iv) earlier ---
level_iv = None
for lvl in levels:
    if "IV" in lvl.Name.upper() or lvl.Name.startswith("4") or "POZIOM 4" in lvl.Name.upper():
        level_iv = lvl
        break

# --------------------------------------------------------------------------------------------- select wall/column type --------------------
wall_type = None
wall_type_generic = None
wall_type_first = None

all_wall_types = FilteredElementCollector(doc).OfClass(WallType).ToElements()

if all_wall_types:
    wall_type_first = all_wall_types[0] # Fallback 2 (pierwszy z brzegu)

for wt in all_wall_types:
    try:
        name = wt.Name.lower()
    except:
        name = ""
    
    if "brick" in name or "cegła" in name: #priorytetowo wyszukuje cegłę z projektu
        wall_type = wt
        break # Znaleziono najlepszy
    
    if not wall_type_generic and ("generic" in name or "basic" in name or "podstawowa" in name): #jeśli nie znajdzie, to podstawowa ściana
        wall_type_generic = wt

if not wall_type: # Jeśli nie ma "brick"
    wall_type = wall_type_generic # Użyj "generic"
if not wall_type: # Jeśli nie ma "generic"
    wall_type = wall_type_first # Użyj pierwszego z brzegu

col_type = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_StructuralColumns).FirstElement()

if not wall_type or not col_type:
    TaskDialog.Show("Error“, ”No wall or column type in the design.")
    sys.exit()

# ----------Choice of ceiling type; for design purposes - identical ---
floor_type = FilteredElementCollector(doc).OfClass(FloorType).FirstElement()
if not floor_type:
    TaskDialog.Show("Error“, ”No floor type (FloorType) in the project.")
    sys.exit()
    
# -------------------------------------------------------------------------------------------------------- transaction --------------------

# --- DODANO: Funkcja pomocnicza do tworzenia stropów ---
def create_floor_from_curves(curves_list, level, f_type, height_offset=0.0): #definiowanie kształtu stropu
    """
    Tworzy strop na podanym poziomie z listy krzywych (Lines lub Arcs).
    Krzywe MUSZĄ tworzyć zamkniętą pętlę w odpowiedniej kolejności.
    """
    try:
        loop = CurveLoop() #tworzy pusty kontener na pętlę krzywych
        for c in curves_list:
            if c and c.Length > 0.001: # Zabezpieczenie
                loop.Append(c)
        
        if loop.IsOpen():
            print("Warning: The loop for ceiling at level ‘{}’ is open. I am ignoring it. Pomijam.".format(level.Name))
            return None

        profile = List[CurveLoop]()
        profile.Add(loop)
        
        floor = Floor.Create(doc, profile, f_type.Id, level.Id) #Tworzy nowe stropy w obrębie obrysów
        
        if floor and height_offset != 0.0: #to jest zawsze ustawione jako strop tworzący się na ostatnim piętrze --> zawiera offset od punktu bazowego
            offset_param = floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
            if offset_param:
                offset_param.Set(height_offset)
        return floor
    except Exception as e:
        print("Error creating ceiling at level {}: {}".format(level.Name, e))
        return None
        
# ---------------------------------------------------------------------transaction initiation------------

t = Transaction(doc, "Generative building with safe offsets")
t.Start()

if not col_type.IsActive:
    col_type.Activate()
    doc.Regenerate()

# -------------------------------------------------------------------------------------------------Loop I - main buildings (straight lines) --------------------
for line_id in line_ids:
    try:
        line_elem = doc.GetElement(line_id) #metoda pobiera element z bazy danych na podstawie jego ID 
        if not line_elem or not hasattr(line_elem, "Location"):
            continue
        curve = line_elem.Location.Curve #tu zwraca faktyczną geometrię
        if not curve:
            continue

        start = curve.GetEndPoint(0) #zwraca punkt startowy lub kończowy jako wartość XYZ
        end = curve.GetEndPoint(1) #reprezentacja punktu 3D lub wektoru
        direction = (end - start).Normalize() #skaluje obiekt tak, aby miał długość 1
        normal = XYZ(-direction.Y, direction.X, 0).Normalize() #nadanie głębokości, tworzy nowy wektor obrócony o 90 stopni od "direction" 
        
        if line_id.Value in ids_do_odwrocenia:
            normal = -normal

        length = curve.Length
        if length <= 0.0:
            print("The line was skipped {}: długość 0.".format(line_id.Value))
            continue

        num_cols = int(length / col_spacing_ft) + 1

        # kolumny
        for i in range(num_cols):
            p = start + direction * (i * col_spacing_ft)
            col = doc.Create.NewFamilyInstance(p, col_type, poziom_0, Structure.StructuralType.Column)
            h = col.LookupParameter("Unconnected Height")
            if h: h.Set(wysokosc_parteru_ft)

        for i in range(num_cols - 1):
            p = start + direction * ((i + 0.5) * col_spacing_ft) + normal * col_depth_ft
            col = doc.Create.NewFamilyInstance(p, col_type, poziom_0, Structure.StructuralType.Column)
            h = col.LookupParameter("Unconnected Height")
            if h: h.Set(wysokosc_parteru_ft)

        # parter - ściany (cztery boki)
        glebokosc_do_uzycia_ft = calkowita_glebokosc_ft
        if line_id.Value == 1267677:
            glebokosc_do_uzycia_ft = calkowita_glebokosc_ft * 1.10

        p1_dol = start + normal * glebokosc_kolumn_ft
        p2_dol = end + normal * glebokosc_kolumn_ft
        p3_dol = end + normal * glebokosc_do_uzycia_ft
        p4_dol = start + normal * glebokosc_do_uzycia_ft

        for a, b in [(p1_dol, p2_dol), (p2_dol, p3_dol), (p3_dol, p4_dol), (p4_dol, p1_dol)]:
            if a.IsAlmostEqualTo(b):
                continue
            try:
                Wall.Create(doc, Line.CreateBound(a, b), wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
            except Exception as e:
                print("The ground floor wall has not been created (line {}): {}".format(line_id.Value, e))

        # piętra
        p1_gora = start
        p2_gora = end
        p3_gora = end + normal * glebokosc_do_uzycia_ft
        p4_gora = start + normal * glebokosc_do_uzycia_ft
        for a, b in [(p1_gora, p2_gora), (p2_gora, p3_gora), (p3_gora, p4_gora), (p4_gora, p1_gora)]:
            if a.IsAlmostEqualTo(b):
                continue
            try:
                Wall.Create(doc, Line.CreateBound(a, b), wall_type.Id, poziom_1.Id, wys_powyzej_ft, 0.0, False, False)
            except Exception as e:
                print("No floor walls have been created (line {}): {}".format(line_id.Value, e))

        # --- DODANO: Strop dla pięter (na poziomie IV, jako "dach" bryły 1-III / podłoga IV) ---
        if level_iv: # Używamy poziomu IV jako dachu dla bryły I-III
            floor_curves = List[Curve]()
            floor_curves.Add(Line.CreateBound(p1_gora, p2_gora))
            floor_curves.Add(Line.CreateBound(p2_gora, p3_gora))
            floor_curves.Add(Line.CreateBound(p3_gora, p4_gora))
            floor_curves.Add(Line.CreateBound(p4_gora, p1_gora))
            create_floor_from_curves(floor_curves, level_iv, floor_type) # To jest strop na 12m
        # --- KONIEC DODANO ---

    except Exception as e:
        print("Error in line {}: {}".format(line_id.Value, e))

# -------------------------------------------------------------------------------------------------- additional floor IV (without rollback) --------------------
wys_dodatkowej_kondygnacji_m = 4.0 #wskazanie wysokości
wys_dodatkowej_kondygnacji_ft = wys_dodatkowej_kondygnacji_m * foot #konwersja jednostek
linie_dodatkowej_kondygnacji = [ElementId(1265253), ElementId(1268120), ElementId(1278942)] #tworzą sie na jej podstawie

if level_iv: #rozpoczyna pętlę dla Level IV
    for line_id in linie_dodatkowej_kondygnacji:
        try: #zabezpieczenie, kiedy linia nie jest elementem liniowym, np krzywa lub jej brak, przeskakuje i kod idzie dalej
            line_elem = doc.GetElement(line_id)
            if not line_elem or not hasattr(line_elem, "Location"):
                print("Line IV omitted (element missing): {}".format(line_id.Value))
                continue
            curve = line_elem.Location.Curve
            if not curve:
                print("Line IV omitted (no geometry): {}".format(line_id.Value))
                continue

            start = curve.GetEndPoint(0) #lokalizauje punkt XYZ
            end = curve.GetEndPoint(1) #lokalizauje punkt XYZ
            direction = (end - start).Normalize() #stwarza możliwość wektora kierunkowego
            normal = XYZ(-direction.Y, direction.X, 0).Normalize() #wektor prostopadły, stwarza kierunek odwrócenia
            if line_id.Value in ids_do_odwrocenia or line_id.Value == 1278942: #odwraca ten kierunek
                normal = -normal

            p1 = start + normal * cofniecie_iv_ft # frontowe, oblicza narożniki podstawy, które są odsunięte o daną wartość "odsunięcia kondygnacji"
            p2 = end + normal * cofniecie_iv_ft #frontowe
            p3 = end + normal * calkowita_glebokosc_ft # tylne narożniki odsunięte od linii bazowej o wartość cofnięcia 
            p4 = start + normal * calkowita_glebokosc_ft #tylne 

            for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]: #pętla która tworzy 4 ściany 
                if a.IsAlmostEqualTo(b): #zabezpieczenie aby nie tworzyć ściany o długości 0
                    continue
                try: #tworzy nową ścianę 
                    Wall.Create(doc, Line.CreateBound(a, b), wall_type.Id, level_iv.Id, #w danym dokumencie; wzdłuż wybranej krzywej, ze ścianą o danym ID; która jest na poziomie IV; o wysokości 4m
                                wys_dodatkowej_kondygnacji_ft, 0.0, False, False) #offset, flip, structural
                except Exception as e:
                    print("No wall IV (line {}): {}".format(line_id.Value, e))

            floor_curves_iv = List[Curve]() #dodanie stropu dachowego --> obrys stworzony na podstawie obrysu ścian
            floor_curves_iv.Add(Line.CreateBound(p1, p2))
            floor_curves_iv.Add(Line.CreateBound(p2, p3))
            floor_curves_iv.Add(Line.CreateBound(p3, p4))
            floor_curves_iv.Add(Line.CreateBound(p4, p1))
            create_floor_from_curves(floor_curves_iv, level_iv, floor_type, wys_dodatkowej_kondygnacji_ft) #tworzenie danego stropu na poziomie IV ale z offsetem na wysokości 12 + 4 = 16 m

        except Exception as e: #wyszukuje błąd w całej pętli
            print("Błąd kondygnacji IV (linia {}): {}".format(line_id.Value, e))
else:
    TaskDialog.Show("Attention,“ ”Level ‘IV’ not found. The floor has not been created.")

# ----------------------------------------------------------------------------------------------------------------------- auditorium --------------------
wysokosc_audytorium_6m_ft = 6.0 * foot #konwersja jednostek
ids_audytorium_6m = [1283599, 1283696, 1285389, 1285445]

for auditorium_line_id in auditorium_line_ids: #rozpoczęcie po wszystkich liniach zdefiniowanych jako audytorium
    try:
        line_elem = doc.GetElement(auditorium_line_id) #pobranie geometrii z projektu
        if not line_elem or not hasattr(line_elem, "Location"):
            continue
        curve = line_elem.Location.Curve
        if not curve:
            continue

        glebokosc_audytorium_do_uzycia_ft = calkowita_glebokosc_ft #ustawienie głębokości domyślnej na pelną głębokość budynku oraz użycie głębokości podanej przez użytkownika
        if auditorium_line_id.Value == 1283599:
            glebokosc_audytorium_do_uzycia_ft = glebokosc_audytorium_ns_ft
        elif auditorium_line_id.Value == 1283696:
            glebokosc_audytorium_do_uzycia_ft = glebokosc_audytorium_35m_ft

        wysokosc_do_uzycia = wysokosc_audytorium_6m_ft if auditorium_line_id.Value in ids_audytorium_6m else wysokosc_calkowita_ft #sprawdza czy dane ID znajduje się na liście

        if isinstance(curve, Line):
            start = curve.GetEndPoint(0)
            end = curve.GetEndPoint(1)
            direction = (end - start).Normalize()
            normal = XYZ(-direction.Y, direction.X, 0).Normalize()
            normal = -normal
            p1 = start
            p2 = end
            p3 = end + normal * glebokosc_audytorium_do_uzycia_ft
            p4 = start + normal * glebokosc_audytorium_do_uzycia_ft
            for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]: #tworzy 4 ściany na poziomie o obliczonej wysokości - wysokość do użycia
                if a.IsAlmostEqualTo(b):
                    continue
                try:
                    Wall.Create(doc, Line.CreateBound(a, b), wall_type.Id, poziom_0.Id, wysokosc_do_uzycia, 0.0, False, False)
                except Exception as e:
                    print("Nie utworzono ściany audytorium (linia {}): {}".format(auditorium_line_id.Value, e))

            # --- ZMODYFIKOWANO: Strop nad audytorium (POPRAWKA DLA 1282579) ---
            if auditorium_line_id.Value in ids_audytorium_6m: # Jeśli ściany mają wysokość 6m to zpiera krzywe p1-p4 i tworzy strop na poziomie 0 z offsetem 6 m
                floor_curves_aud = List[Curve]()
                floor_curves_aud.Add(Line.CreateBound(p1, p2))
                floor_curves_aud.Add(Line.CreateBound(p2, p3))
                floor_curves_aud.Add(Line.CreateBound(p3, p4))
                floor_curves_aud.Add(Line.CreateBound(p4, p1))
                # Tworzymy na poziomie 0, ale z offsetem 6m
                create_floor_from_curves(floor_curves_aud, poziom_0, floor_type, wysokosc_audytorium_6m_ft)
            else: # Dla pozostałych (w tym 1282579), które mają wysokość 12m
                if level_iv: # Sprawdźmy czy poziom IV istnieje
                    floor_curves_aud = List[Curve]()
                    floor_curves_aud.Add(Line.CreateBound(p1, p2))
                    floor_curves_aud.Add(Line.CreateBound(p2, p3))
                    floor_curves_aud.Add(Line.CreateBound(p3, p4))
                    floor_curves_aud.Add(Line.CreateBound(p4, p1))
                    # Tworzymy na poziomie IV (12m) bez offsetu
                    create_floor_from_curves(floor_curves_aud, level_iv, floor_type, 0.0)
            # --- KONIEC ZMODYFIKOWANO ---

        elif isinstance(curve, Arc): #tworzenie obrysu dla łuków polega na utworzeniu dwóch łuków i domknięcie ich krańców prostymi liniami 
            offset_sign = -1.0
            radius_ft = curve.Radius
            if glebokosc_audytorium_do_uzycia_ft >= (radius_ft - 0.1):
                print("The arc of the auditorium {}: depth >= radius has been omitted.".format(auditorium_line_id.Value))
                continue

            arc_front = curve
            arc_back = curve.CreateOffset(offset_sign * glebokosc_audytorium_do_uzycia_ft, XYZ.BasisZ)
            if (arc_front is None) or (arc_back is None):
                print("The auditorium (offsets) for the arch has been omitted. {}".format(auditorium_line_id.Value))
                continue

            try: #tworzy 4 ściany --> dwa łuki i dwie linie proste
                Wall.Create(doc, arc_front, wall_type.Id, poziom_0.Id, wysokosc_do_uzycia, 0.0, False, False)
                Wall.Create(doc, arc_back, wall_type.Id, poziom_0.Id, wysokosc_do_uzycia, 0.0, False, False)
                Wall.Create(doc, Line.CreateBound(arc_front.GetEndPoint(0), arc_back.GetEndPoint(0)), wall_type.Id, poziom_0.Id, wysokosc_do_uzycia, 0.0, False, False)
                Wall.Create(doc, Line.CreateBound(arc_front.GetEndPoint(1), arc_back.GetEndPoint(1)), wall_type.Id, poziom_0.Id, wysokosc_do_uzycia, 0.0, False, False)
            except Exception as e:
                print("The walls of the auditorium arch were not created (arch {}): {}".format(auditorium_line_id.Value, e))

            if auditorium_line_id.Value in ids_audytorium_6m: # Dla tych o wysokości 6m, z 'arc_front' i 'arc_back' do def kształtu i stwarza strop na poziomie 0 z offsetem 6m
                floor_curves_aud_arc = List[Curve]()
                floor_curves_aud_arc.Add(arc_front)
                floor_curves_aud_arc.Add(Line.CreateBound(arc_front.GetEndPoint(1), arc_back.GetEndPoint(1)))
                floor_curves_aud_arc.Add(arc_back.CreateReversed()) # Ważne: odwrócony łuk
                floor_curves_aud_arc.Add(Line.CreateBound(arc_back.GetEndPoint(0), arc_front.GetEndPoint(0)))
                create_floor_from_curves(floor_curves_aud_arc, poziom_0, floor_type, wysokosc_audytorium_6m_ft)
            else: # Dla pozostałych (12m)
                if level_iv:
                    floor_curves_aud_arc = List[Curve]()
                    floor_curves_aud_arc.Add(arc_front)
                    floor_curves_aud_arc.Add(Line.CreateBound(arc_front.GetEndPoint(1), arc_back.GetEndPoint(1)))
                    floor_curves_aud_arc.Add(arc_back.CreateReversed())
                    floor_curves_aud_arc.Add(Line.CreateBound(arc_back.GetEndPoint(0), arc_front.GetEndPoint(0)))
                    # Tworzymy na poziomie IV (12m) bez offsetu
                    create_floor_from_curves(floor_curves_aud_arc, level_iv, floor_type, 0.0)
            # --- KONIEC ZMODYFIKOWANO ---
    except Exception as e:
        print("Auditorium error (line {}): {}".format(auditorium_line_id.Value, e))

# ------------------------------------------------------------------------------------------------------------------ safe offsety --------------------
adjusted_arcs = []
buffer_ft = 0.2  # większy bufor niż wcześniej (ok. 6 cm), żeby uniknąć równości promienia/offset --> unjoin

for arc_id in arc_ids:
    try:
        arc_elem = doc.GetElement(arc_id)
        if not arc_elem or not hasattr(arc_elem, "Location"):
            continue
        curve = arc_elem.Location.Curve
        if not isinstance(curve, Arc):
            continue

        radius_ft = curve.Radius #pobieranie geomoerii łuku
        length = curve.Length
        if length <= 0.0:
            print("The { } arc was omitted: length 0.".format(arc_id.Value))
            continue

        # jeśli całkowita głębokość >= radius - buffer -> przycinamy do safe depth
        if calkowita_glebokosc_ft >= (radius_ft - buffer_ft):
            effective_depth_ft = max(0.0, radius_ft - buffer_ft)
            if effective_depth_ft <= 0.01:
                print("Arc {}: effective depth too small.".format(arc_id.Value))
                continue
            adjusted_arcs.append((arc_id.Value, calkowita_glebokosc_ft / foot, effective_depth_ft / foot)) #zapisanie informacji o modyfikacji do dziennika
            depth_for_use_ft = effective_depth_ft #używanie bezpiecznej głębokości do dalszych obliczeń
        else:
            depth_for_use_ft = calkowita_glebokosc_ft #jeśli głebokość była mniejsza niż promień to używaj pełnej głębokości

        offset_sign = -1.0 #zwrócenie odsunięcia do wewnątrz 

        num_cols = int(length / col_spacing_ft) + 1 #obliczenie ile się zmieści słupów 

        for i in range(num_cols): #tworzenie kolumn na łuku (pierwszy rząd)
            param = (i * col_spacing_ft) / length
            if param < 0.0: param = 0.0
            if param > 1.0: param = 1.0
            p = curve.Evaluate(param, True) # Pobiera punkt XYZ na łuku na podstawie znormalizowanego parametru
            col = doc.Create.NewFamilyInstance(p, col_type, poziom_0, Structure.StructuralType.Column)
            h = col.LookupParameter("Unconnected Height")
            if h: h.Set(wysokosc_parteru_ft)

        offset_curve_cols = None # drugi rząd kolumn (odsunięty)
        try:
            offset_curve_cols = curve.CreateOffset(offset_sign * col_depth_ft, XYZ.BasisZ) # Stwórz nowy, tymczasowy łuk odsunięty do wewnątrz o 'col_depth_ft'
        except:
            offset_curve_cols = None # Błąd: offset pewnie > promień

        if offset_curve_cols:
            for i in range(num_cols - 1):
                param = ((i + 0.5) * col_spacing_ft) / length # Przesunięte
                if param < 0.0: param = 0.0
                if param > 1.0: param = 1.0
                p = offset_curve_cols.Evaluate(param, True) # Pobierz punkt XYZ, ale tym razem z 'offset_curve_cols'
                col = doc.Create.NewFamilyInstance(p, col_type, poziom_0, Structure.StructuralType.Column)
                h = col.LookupParameter("Unconnected Height")
                if h: h.Set(wysokosc_parteru_ft)

        desired_front_offset = offset_sign * glebokosc_kolumn_ft # bezpieczne offsety dla ścian: nie przekraczaj promienia - zostaw buffer
        desired_back_offset = offset_sign * depth_for_use_ft

        safe_front_abs = min(abs(desired_front_offset), max(0.0, radius_ft - buffer_ft)) #ponowne, bezpieczne obliczenie offsetów
        safe_back_abs = min(abs(desired_back_offset), max(0.0, radius_ft - buffer_ft))

        # jeśli safe offsety zbyt małe -> pominąć tworzenie po łuku
        if safe_front_abs <= 0.01 or safe_back_abs <= 0.01:
            print("Wall creation for arc {} omitted: safe offset too small.".format(arc_id.Value))
            continue

        try: #stworzenie końcowych łuków dla ścian
            arc_front = curve.CreateOffset(-1.0 * safe_front_abs, XYZ.BasisZ)
        except:
            arc_front = None
        try:
            arc_back = curve.CreateOffset(-1.0 * safe_back_abs, XYZ.BasisZ)
        except:
            arc_back = None

        if (arc_front is None) or (arc_back is None):
            print("Arc { } omitted: unable to create offsets (arc_front/arc_back None).".format(arc_id.Value))
            continue

        if arc_front.Length < 0.001 or arc_back.Length < 0.001: # pomijaj jeśli długość offsetów znikoma
            print("The arc { } has been omitted; the offsets are too short.".format(arc_id.Value))
            continue

        try: # tworzenie ścian parteru po łuku
            Wall.Create(doc, arc_front, wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
            Wall.Create(doc, arc_back, wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
        except Exception as e:
            print("Error creating ground floor walls for an arch {}: {}".format(arc_id.Value, e))
            # próbujemy zmniejszyć safe_back_abs i ponowić raz
            reduced = max(0.01, safe_back_abs - 0.1)
            try:
                arc_back_try = curve.CreateOffset(-1.0 * reduced, XYZ.BasisZ)
                if arc_back_try and arc_back_try.Length > 0.001:
                    Wall.Create(doc, arc_back_try, wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
            except Exception as e2:
                print("Another unsuccessful attempt for the bow {}: {}".format(arc_id.Value, e2))

        try: # łączące końcowe odcinki (zaślepki)
            a0 = arc_front.GetEndPoint(0)
            b0 = arc_back.GetEndPoint(0)
            a1 = arc_front.GetEndPoint(1)
            b1 = arc_back.GetEndPoint(1)
            if not a0.IsAlmostEqualTo(b0):
                Wall.Create(doc, Line.CreateBound(a0, b0), wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
            if not a1.IsAlmostEqualTo(b1):
                Wall.Create(doc, Line.CreateBound(a1, b1), wall_type.Id, poziom_0.Id, wysokosc_parteru_ft, 0.0, False, False)
        except Exception as e:
            print("Error closing the ground floor of the arch {}: {}".format(arc_id.Value, e))

        try: # piętra - podobnie z bezpiecznym offsetem
            arc_back_floor = curve.CreateOffset(-1.0 * safe_back_abs, XYZ.BasisZ)
            # utwórz front jako sam krzywa bazowa (curve)
            if arc_back_floor and arc_back_floor.Length > 0.001:
                try:
                    Wall.Create(doc, curve, wall_type.Id, poziom_1.Id, wys_powyzej_ft, 0.0, False, False)
                    Wall.Create(doc, arc_back_floor, wall_type.Id, poziom_1.Id, wys_powyzej_ft, 0.0, False, False)
                    # łączące
                    if not curve.GetEndPoint(0).IsAlmostEqualTo(arc_back_floor.GetEndPoint(0)):
                        Wall.Create(doc, Line.CreateBound(curve.GetEndPoint(0), arc_back_floor.GetEndPoint(0)), wall_type.Id, poziom_1.Id, wys_powyzej_ft, 0.0, False, False)
                    if not curve.GetEndPoint(1).IsAlmostEqualTo(arc_back_floor.GetEndPoint(1)):
                        Wall.Create(doc, Line.CreateBound(curve.GetEndPoint(1), arc_back_floor.GetEndPoint(1)), wall_type.Id, poziom_1.Id, wys_powyzej_ft, 0.0, False, False)
                except Exception as e:
                    print("Error creating floor for arc {}: {}".format(arc_id.Value, e))
        except Exception as e:
            print("Floor offset error for arc {}: {}".format(arc_id.Value, e))

        if level_iv: #Strop dla pięter (na poziomie IV, jako "dach" bryły 1-III) ---
            try:
                floor_curves_arc_12m = List[Curve]() 
                floor_curves_arc_12m.Add(curve) # 1. Dodaj przedni łuk (oryginalna linia bazowa)
                floor_curves_arc_12m.Add(Line.CreateBound(curve.GetEndPoint(1), arc_back_floor.GetEndPoint(1))) # 2. Dodaj boczną zaślepkę 1 (prostą linię)
                floor_curves_arc_12m.Add(arc_back_floor.CreateReversed()) # 3. Dodaj tylny łuk (odsunięty I ODWRÓCONY)
                floor_curves_arc_12m.Add(Line.CreateBound(arc_back_floor.GetEndPoint(0), curve.GetEndPoint(0))) # 4. Dodaj boczną zaślepkę 2 (prostą linię)
                create_floor_from_curves(floor_curves_arc_12m, level_iv, floor_type) # Wywołaj funkcję pomocniczą z gotowym profilem
            except Exception as e:
                print("Error creating 12m ceiling (arch {}) {}".format(arc_id.Value, e))

    except Exception as e:
        print("Failed to process the arc {}: {}".format(arc_id.Value, e))

# -------------------------------------------------------------------------------------------------------------- additional floor 4 m above the arches --------------------
try: # znajdź poziom "IV level"
    poziom_IV = None #ustawienie "pustej zmiennej"
    for lvl in FilteredElementCollector(doc).OfClass(Level): #szukanie poziomów w dokumencie 
        lvl_name_upper = lvl.Name.upper() #pobranie nazwy poziomu i zamiana na wielkie litery
        if "IV" in lvl_name_upper or "POZIOM 4" in lvl_name_upper or lvl_name_upper.startswith("4"): #dokladne, elastyczne wyszukiwanie, znajduje poziom który ma w nazwie VI, POZIOM 4  lub zaczyna się od 4
            poziom_IV = lvl # Znaleziono! Przypisz obiekt 'Level' do zmiennej
            break

    if poziom_IV is None: #jeśli pętla nie znalazła poziomu 4 w dokumencie 
        TaskDialog.Show("Error“, ”Level ‘IV’ / ‘Level 4’ not found — arch superstructure omitted.")
    else:
        wysokosc_dodatkowej_kondygnacji_m = 4.0 # --- Jeśli Poziom IV został znaleziony, kontynuuj ---
        wysokosc_dodatkowej_kondygnacji_ft = wysokosc_dodatkowej_kondygnacji_m * foot #konwersja jednostek

        for arc_id in arc_ids: # Używamy tych samych arc_ids co dla łuków głównych
            try:
                arc_elem = doc.GetElement(arc_id) #standardowe pobranie geometrii łuku
                if not arc_elem or not hasattr(arc_elem, "Location"):
                    continue
                curve = arc_elem.Location.Curve
                if not isinstance(curve, Arc): #jeśli to nie łuk to pomiń
                    continue

                radius_ft = curve.Radius #pobierz promień łuku
                if radius_ft <= 0.0:
                    continue
                    
                buffer_ft = 0.2 #bezpieczne offsety
                offset_sign = -1.0
                
                # Obliczamy TYLKO back_offset, bo front będzie na 'curve'
                back_offset_ft = offset_sign * calkowita_glebokosc_ft # odsunięcie o pełną głębokość budynku
                safe_back_abs = min(abs(back_offset_ft), max(0.0, radius_ft - buffer_ft)) # oblicz maksymalne bezpieczne odsunięcie (promień i bufor)

                # Sprawdzamy tylko 'safe_back_abs'
                if safe_back_abs <= 0.01:
                    print("The superstructure of the arc {}: safe_back_abs too small has been omitted.".format(arc_id.Value))
                    continue

                arc_back = None # utwórz TYLKO tylny łuk
                try:
                    arc_back = curve.CreateOffset(-1.0 * safe_back_abs, XYZ.BasisZ) #tworzenie nowego łuku odsuniętego o bezpieczną odległość
                except:
                    pass # Błąd offsetu, Zignoruj błąd

                if not arc_back or arc_back.Length < 0.001: # Sprawdź, czy 'arc_back' został pomyślnie utworzony
                    print("The superstructure of the arc {} has been omitted; arc_back could not be created.".format(arc_id.Value))
                    continue
                
                Wall.Create(doc, curve, wall_type.Id, poziom_IV.Id, wysokosc_dodatkowej_kondygnacji_ft, 0.0, False, False)  # 1. Tworzenie ściany frontowej DOKŁADNIE na 'curve'
                
                Wall.Create(doc, arc_back, wall_type.Id, poziom_IV.Id, wysokosc_dodatkowej_kondygnacji_ft, 0.0, False, False) # 2. Tworzenie ściany tylnej na 'arc_back'

                a0, b0 = curve.GetEndPoint(0), arc_back.GetEndPoint(0) # 3. Ściany boczne (Zaślepki), Pobierz punkty startowe (a0, b0) i końcowe (a1, b1) obu łuków
                a1, b1 = curve.GetEndPoint(1), arc_back.GetEndPoint(1)

                if not a0.IsAlmostEqualTo(b0): # Stwórz ścianę boczną na początku, jeśli punkty się nie pokrywają
                    Wall.Create(doc, Line.CreateBound(a0, b0), wall_type.Id, poziom_IV.Id, wysokosc_dodatkowej_kondygnacji_ft, 0.0, False, False)
                if not a1.IsAlmostEqualTo(b1): # Stwórz ścianę boczną na końcu
                    Wall.Create(doc, Line.CreateBound(a1, b1), wall_type.Id, poziom_IV.Id, wysokosc_dodatkowej_kondygnacji_ft, 0.0, False, False)

                floor_curves_arc_16m = List[Curve]() #zbieranie 4 krzywych obrysu dachu 
                floor_curves_arc_16m.Add(curve) # 1. Dodaj przedni łuk ('curve')
                floor_curves_arc_16m.Add(Line.CreateBound(a1, b1)) # 2. Dodaj prawą zaślepkę (linia od a1 do b1)
                floor_curves_arc_16m.Add(arc_back.CreateReversed()) # 3. Dodaj tylny łuk, ale w ODWROTNYM kierunku, aby zamknąć pętlę
                floor_curves_arc_16m.Add(Line.CreateBound(b0, a0)) # 4. Dodaj lewą zaślepkę (linia od b0 do a0)

                create_floor_from_curves(floor_curves_arc_16m, poziom_IV, floor_type, wysokosc_dodatkowej_kondygnacji_ft) #funkcja pomocnicza do profilu tworzenia stropu; o danym profilu, zaczepiony na danym poziomie, z użytym stropem ale odsuniety o 4m

            except Exception as e: # To jest 'except' dla wewnętrznego 'try' - łapie błąd dla JEDNEGO łuku
                print("Error when creating an arc superstructure {}: {}".format(arc_id.Value, e))

except Exception as e: # To jest 'except' dla zewnętrznego 'try' - łapie błąd np. przy wyszukiwaniu poziomu
    print("General error when creating floors above arches:", e)

# ---------------------------------------------------------------------------------------------------------------- special walls 16m on curves --------------------
try:
    wysokosc_16m_ft = 16.0 * foot # Ustawia docelową wysokość na 16.0 metrów i konwertuje ją na stopy
    high_arc_ids = [ElementId(1302356), ElementId(1302731)] #definicja nowych łuków

    for arc_id in high_arc_ids:
        try:
            arc_elem = doc.GetElement(arc_id) #pobieranie elementu z projektu
            if not arc_elem or not hasattr(arc_elem, "Location"): #sprawdznie czy dany element istnieje i czy ma właściwość 'location"
                print("The 16m arch has been omitted (element missing): {}".format(arc_id.Value))
                continue
            curve = arc_elem.Location.Curve #połącz geometrię czyli krzywą z elementu 
            if not isinstance(curve, Arc):
                print("The 16m arc has been omitted (it is not an arc): {}".format(arc_id.Value))
                continue
            
            if curve.Length < 0.01: #kolejne sprawdzenie czyli czy ma jakąś długość większą od 0
                print("The 16m arc was omitted (too short): {}".format(arc_id.Value))
                continue

            Wall.Create(doc, curve, wall_type.Id, poziom_0.Id, wysokosc_16m_ft, 0.0, False, False) # Tworzenie ściany o wysokości 16m na poziomie 0

        except Exception as e: #obsługa dla błędu wewnętrznego
            print("Error when creating a 16m wall on a curve {}".format(arc_id.Value, e))

except Exception as e: #obsługa dla błędu całego modułu
    print("General error when creating 16m walls:", e)

# ----------------------------------------------------------------------------------------------------------------------- CALCULATING THE AREA OF THE GROUND FLOOR --------------------
import math

pow_audytorium_m2 = glebokosc_audytorium_ns_m * 17.0 # 1. Audytorium; prostokąt: głębokość audytorium (użytkownik) x 17.0 m

pow_furmanska_m2 = glebokosc_budynku_m * 72.0 # 2. Bryła od ul. Furmańskiej; prostokąt: głębokość zabudowy za kolumnami x 72 m

pow_karowa_luk1_m2 = (math.pi * (glebokosc_budynku_m ** 2)) * 0.25 #  3. Łuk ul. Furmańska–Karowa, ćwiartka koła o promieniu R = głębokość zabudowy za kolumnami (DB)

pow_karowa_m2 = glebokosc_budynku_m * 66.0 # 4. Bryła ul. Karowa; prostokąt: głębokość zabudowy za kolumnami x 66 m

pow_karowa_dobra_luk2_m2 = (math.pi * (glebokosc_budynku_m ** 2)) * 0.25 # 5. Łuk Karowa–Dobra; ćwiartka koła o promieniu R = głębokość zabudowy za kolumnami (DB)

pow_dobra_m2 = glebokosc_budynku_m * 19.0 # 6. Bryła budynku od ul. Dobrej; prostokąt: głębokość zabudowy za kolumnami x 19 m

suma_parter_m2 = ( # --- SUMA PARTERU ---
    pow_audytorium_m2 +
    pow_furmanska_m2 +
    pow_karowa_luk1_m2 +
    pow_karowa_m2 +
    pow_karowa_dobra_luk2_m2 +
    pow_dobra_m2
)

pow_audytorium_m2 = round(pow_audytorium_m2, 2) # Zaokrąglenie wyników do 2 miejsc po przecinku
pow_furmanska_m2 = round(pow_furmanska_m2, 2)
pow_karowa_luk1_m2 = round(pow_karowa_luk1_m2, 2)
pow_karowa_m2 = round(pow_karowa_m2, 2)
pow_karowa_dobra_luk2_m2 = round(pow_karowa_dobra_luk2_m2, 2)
pow_dobra_m2 = round(pow_dobra_m2, 2)
suma_parter_m2 = round(suma_parter_m2, 2)

# --- RAPORT ---
raport = (
    "GROUND FLOOR AREA (m²)\n\n"
    "1. Auditorium: {} m²\n"
    "2. Building from Furmańska Street:  {} m²\n"
    "3. Furmańska–Karowa Street arch (R = {:.2f} m): {} m²\n"
    "4. Building on Karowa Street:  {} m²\n"
    "5. Karowa–Dobra arch (R = {:.2f} m): {} m²\n"
    "6. Building on Dobra Street: {} m²\n\n"
    "TOTAL GROUND FLOOR: {} m²".format(
        pow_audytorium_m2,
        pow_furmanska_m2,
        glebokosc_budynku_m, pow_karowa_luk1_m2,
        pow_karowa_m2,
        glebokosc_budynku_m, pow_karowa_dobra_luk2_m2,
        pow_dobra_m2,
        suma_parter_m2
    )
)

TaskDialog.Show("Building area – Ground floor", raport)

# ------------------------------------------------------------------------------------------------------------------ CALCULATION OF THE AREA OF THE FIRST TO THIRD FLOORS --------------------
import math

# --- ZMIENNE POMOCNICZE ---
glebokosc_calkowita_m = glebokosc_kolumn_m + glebokosc_budynku_m # Suma głębokości kolumn i zabudowy za kolumnami (wartość generatywna)

pow_furmanska_pietro_m2 = glebokosc_calkowita_m * 72.0 # --- 2.1 Bryła od ul. Furmańskiej ---; Prostokąt: (DK + DB) * 72 m

pow_karowa_luk1_pietro_m2 = (math.pi * (glebokosc_calkowita_m ** 2)) * 0.25 # --- 2.2 Łuk ul. Furmańska–Karowa ---; Ćwiartka koła o promieniu R = (DK + DB)

pow_karowa_pietro_m2 = glebokosc_calkowita_m * 66.0 # --- 2.3 Bryła ul. Karowa ---; Prostokąt: (DK + DB) * 66 m

pow_karowa_dobra_luk2_pietro_m2 = (math.pi * (glebokosc_calkowita_m ** 2)) * 0.25 # --- 2.4 Łuk Karowa–Dobra ---; Ćwiartka koła o promieniu R = (DK + DB)

pow_dobra_pietro_m2 = glebokosc_calkowita_m * 19.0 # --- 2.5 Bryła od ul. Dobrej ---; Prostokąt: (DK + DB) * 19 m

suma_pietro_m2 = ( # --- SUMA POWIERZCHNI JEDNEGO PIĘTRA ---
    pow_furmanska_pietro_m2 +
    pow_karowa_luk1_pietro_m2 +
    pow_karowa_pietro_m2 +
    pow_karowa_dobra_luk2_pietro_m2 +
    pow_dobra_pietro_m2
)

suma_trzy_pietra_m2 = suma_pietro_m2 * 3 # --- SUMA TRZECH PIĘTER ---

pow_furmanska_pietro_m2 = round(pow_furmanska_pietro_m2, 2) # --- ZAOKRĄGLENIA ---
pow_karowa_luk1_pietro_m2 = round(pow_karowa_luk1_pietro_m2, 2)
pow_karowa_pietro_m2 = round(pow_karowa_pietro_m2, 2)
pow_karowa_dobra_luk2_pietro_m2 = round(pow_karowa_dobra_luk2_pietro_m2, 2)
pow_dobra_pietro_m2 = round(pow_dobra_pietro_m2, 2)
suma_pietro_m2 = round(suma_pietro_m2, 2)
suma_trzy_pietra_m2 = round(suma_trzy_pietra_m2, 2)

# --- RAPORT ---
raport_pietra = (
    "AREA OF FLOORS I–III (m²)\n\n"
    "1. Building from Furmańska Street: {} m²\n"
    "2. Furmańska–Karowa Street arch (R = {:.2f} m): {} m²\n"
    "3. Building on Karowa Street: {} m²\n"
    "4. Arch Karowa–Dobra  (R = {:.2f} m): {} m²\n"
    "5. Building from Dobra Street:  {} m²\n\n"
    "Area of one floor: {} m²\n"
    "Area of 3 floors (I–III): {} m²".format(
        pow_furmanska_pietro_m2,
        glebokosc_calkowita_m, pow_karowa_luk1_pietro_m2,
        pow_karowa_pietro_m2,
        glebokosc_calkowita_m, pow_karowa_dobra_luk2_pietro_m2,
        pow_dobra_pietro_m2,
        suma_pietro_m2,
        suma_trzy_pietra_m2
    )
)

TaskDialog.Show("Area – 1st–3rd floor", raport_pietra)

# ----------------------------------------------------------------------------------------------------- CALCULATION OF ADDITIONAL FLOOR AREA (FOURTH LEVEL) --------------------
import math

# --- ZMIENNE POMOCNICZE --- Wzór: (DK + DB - cofnięcie_IV)
glebokosc_iv_m = glebokosc_kolumn_m + glebokosc_budynku_m - cofniecie_iv_m
if glebokosc_iv_m < 0:
    glebokosc_iv_m = 0  # zabezpieczenie na wypadek nieprawidłowych wartości

glebokosc_calkowita_m = glebokosc_kolumn_m + glebokosc_budynku_m

pow_furmanska_iv_m2 = glebokosc_iv_m * 19.5 # --- 3.1 Bryła od ul. Furmańskiej ---; Prostokąt: (DK + DB - cofnięcie_IV) * 19.5 m

pow_karowa_luk1_iv_m2 = (math.pi * (glebokosc_calkowita_m ** 2)) * 0.25 # --- 3.2 Łuk Furmańska–Karowa ---; Pełne koło o promieniu R = (DK + DB)

pow_karowa_iv_m2 = glebokosc_iv_m * 66.0 # --- 3.3 Bryła ul. Karowa --- Prostokąt: (DK + DB - cofnięcie_IV) * 66 m

pow_karowa_dobra_luk2_iv_m2 = (math.pi * (glebokosc_calkowita_m ** 2)) * 0.25 # --- 3.4 Łuk Karowa–Dobra ---Pełne koło o promieniu R = (DK + DB)

pow_dobra_iv_m2 = glebokosc_iv_m * 19.0 # --- 3.5 Bryła od ul. Dobrej --- Prostokąt: (DK + DB - cofnięcie_IV) * 19 m

suma_iv_m2 = ( # --- SUMA POWIERZCHNI IV POZIOMU ---
    pow_furmanska_iv_m2 +
    pow_karowa_luk1_iv_m2 +
    pow_karowa_iv_m2 +
    pow_karowa_dobra_luk2_iv_m2 +
    pow_dobra_iv_m2
)

pow_furmanska_iv_m2 = round(pow_furmanska_iv_m2, 2) # --- ZAOKRĄGLENIA ---
pow_karowa_luk1_iv_m2 = round(pow_karowa_luk1_iv_m2, 2)
pow_karowa_iv_m2 = round(pow_karowa_iv_m2, 2)
pow_karowa_dobra_luk2_iv_m2 = round(pow_karowa_dobra_luk2_iv_m2, 2)
pow_dobra_iv_m2 = round(pow_dobra_iv_m2, 2)
suma_iv_m2 = round(suma_iv_m2, 2)

# --- RAPORT ---
raport_iv = (
    "ADDITIONAL STORY AREA (IV LEVEL)\n\n"
    "1. Building from Furmańska Street: {} m²\n"
    "2. Furmańska–Karowa arch (R = {:.2f} m): {} m²\n"
    "3. Building on Karowa Street: {} m²\n"
    "4. Karowa–Dobra arch (R = {:.2f} m): {} m²\n"
    "5. Structure from Dobra Street: {} m²\n\n"
    "TOTAL OF LEVEL IV: {} m²".format(
        pow_furmanska_iv_m2,
        glebokosc_calkowita_m, pow_karowa_luk1_iv_m2,
        pow_karowa_iv_m2,
        glebokosc_calkowita_m, pow_karowa_dobra_luk2_iv_m2,
        pow_dobra_iv_m2,
        suma_iv_m2
    )
)

TaskDialog.Show("Area – Additional floor (IV)", raport_iv)

# -------------------------------------------------------------------------------------------------------------- TOTAL AREA SUMMARY --------------------

try: # wybranie wszystkich trzech zmiennych
    total_all_m2 = suma_parter_m2 + suma_trzy_pietra_m2 + suma_iv_m2
except:
    total_all_m2 = 0.0

total_all_m2 = round(total_all_m2, 2)

raport_total = (
    "SUMMARY OF BUILT-UP AREA\n\n"
    "Ground floor:  {} m²\n"
    "Floors I–III (total): {} m²\n"
    "IV (additional floor): {} m²\n\n"
    "=== TOTAL: {} m² ===".format(
        suma_parter_m2,
        suma_trzy_pietra_m2,
        suma_iv_m2,
        total_all_m2
    )
)

TaskDialog.Show("TOTAL SUMMARY", raport_total)

# -------------------------------------------------------------------------------------MPZP VALIDATION MODULE – version with PBC% and above-ground coefficient
import math

# --- Stałe MPZP / parametry działki ---
site_area_m2 = 8986.07
max_building_coverage_pct = 0.60  # 60%
max_building_area_m2 = site_area_m2 * max_building_coverage_pct  # 5391.64 m²

min_PBC_pct = 0.25  # 25%
min_PBC_m2 = site_area_m2 * min_PBC_pct  # 2246.52 m²

# Intensywność zabudowy (całkowita)
I_min = 1.2
I_max = 3.2
I_min_area = site_area_m2 * I_min  # 10783.28 m²
I_max_area = site_area_m2 * I_max  # 28755.42 m²

# Intensywność nadziemia (max 2.0)
I_nadziem_max = 2.0

# Rezerwa na utwardzenia (np. place, chodniki)
paved_allowance = 1000.00

# --- Pobranie powierzchni z wcześniejszych modułów ---
try:
    floor_area = float(round(suma_pietro_m2, 2))  # jedno piętro
except:
    floor_area = 0.0

try:
    three_floors_area = float(round(suma_trzy_pietra_m2, 2))
except:
    three_floors_area = 0.0

try:
    iv_area = float(round(suma_iv_m2, 2))
except:
    iv_area = 0.0

try:
    total_all_area = float(round(total_all_m2, 2))
except:
    total_all_area = 0.0

# ----------------------------------------------------------------------------------- CALCULATIONS -----------------------------------------------------------------------------------

PBC_current = site_area_m2 - floor_area - paved_allowance # Powierzchnia biologicznie czynna (PBC)
if PBC_current < 0:
    PBC_current = 0.0

PBC_percent = (PBC_current / site_area_m2) * 100.0

# 1️⃣ Maksymalna powierzchnia zabudowy (1 piętro + 1000 m²) ≤ 60% działki
max_zabudowa_check_value = floor_area + paved_allowance
ok_max_coverage = (max_zabudowa_check_value <= max_building_area_m2 + 1e-6) #notacja naukowa oznaczająca 1x10^-6 --> floating-point errors

# 2️⃣ Minimalna powierzchnia biologicznie czynna
ok_min_PBC = (PBC_current >= min_PBC_m2 - 1e-6)

# 3️⃣ Intensywność zabudowy całkowita (I)
I_value = total_all_area / site_area_m2 if site_area_m2 > 0 else 0.0
ok_intensity = (I_value >= I_min - 1e-6) and (I_value <= I_max + 1e-6)

# 4️⃣ Intensywność nadziemia (I_nadziem)
above_ground_area = three_floors_area + iv_area
I_nadziem_value = above_ground_area / site_area_m2 if site_area_m2 > 0 else 0.0
ok_above_ground = (I_nadziem_value <= I_nadziem_max + 1e-6)

# 5️⃣ Wysokość zabudowy (max 16 m)
max_allowed_height_m = 16.0
try:
    wysokosc_calkowita_m = float(wysokosc_calkowita_ft) / foot
except:
    wysokosc_calkowita_m = 0.0
ok_height = (wysokosc_calkowita_m <= max_allowed_height_m + 1e-6)

# 6️⃣ Linia zabudowy
line_of_building_check = "UNVERIFIED – requires analysis of geometry in the model"

# --------------------------------------------------------------------- VALIDATION AND REPORTING ------------------------------------------------------------

errors = []

if not ok_max_coverage:
    errors.append(
        "1️⃣ Building area (1 floor + 1000 m² = {:.2f} m²) "
        "exceeds the permissible 60% of the plot ({:.2f} m²).".format(
            max_zabudowa_check_value, max_building_area_m2))

if not ok_min_PBC:
    errors.append(
        "2️⃣ Biologically active surface area too small: {:.2f} m² ({:.2f}%) < {:.2f} m² (25%).".format(
            PBC_current, PBC_percent, min_PBC_m2))

if not ok_intensity:
    errors.append(
        "3️⃣ Building density I = {:.2f} outside the range [{:.2f}, {:.2f}] "
        "(which corresponds to {:.2f}–{:.2f} m²).".format(
            I_value, I_min, I_max, I_min_area, I_max_area))

if not ok_above_ground:
    errors.append(
        "4️⃣ The above-ground intensity I = {:.2f} exceeds the permissible {:.2f}.".format(
            I_nadziem_value, I_nadziem_max))

if not ok_height:
    errors.append(
        "5️⃣ The height of the building {:.2f} m exceeds the permissible limit {:.2f} m.".format(
            wysokosc_calkowita_m, max_allowed_height_m))

# -------------------------------------------------------------------------VALIDATION RESULT--------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

if errors:
    msg = "❌ Non-compliance with the local zoning plan detected:\n\n"
    for e in errors:
        msg += " - " + e + "\n"
    msg += "\n⚠️ Operation interrupted due to violations of the local zoning plan."
    TaskDialog.Show("Local development plan error – Validation", msg)
    t.RollBack()
    sys.exit()

else:
    raport_mpzp = (
        "✅ VALIDATION OF THE LOCAL SPATIAL DEVELOPMENT PLAN – RESULTS\n\n"
        "Area of land 6.3 UN: {:.2f} m²\n"
        "Total building area: {:.2f} m²\n"
        "───────────────────────────────────────────────────────\n\n"
        "1️⃣ Building area: {:.2f} m² / max {:.2f} m² → COMPLIANT ✅\n\n"
        "2️⃣ Biologically active area: {:.2f} m² ({:.2f}%) / min {:.2f} m² (25%) → COMPLIANT ✅\n\n"
        "3️⃣ Building intensity (I): {:.2f} w zakresie [{:.2f}-{:.2f}] → COMPLIANT ✅\n\n"
        "4️⃣ Above-ground intensity (I): {:.2f} / max {:.2f} → COMPLIANT ✅\n\n"
        "───────────────────────────────────────────────────────\n"
    ).format(
        site_area_m2,
        total_all_area,
        max_zabudowa_check_value, max_building_area_m2,
        PBC_current, PBC_percent, min_PBC_m2,
        I_value, I_min, I_max,
        I_nadziem_value, I_nadziem_max
    )

    TaskDialog.Show("✅ Zoning Plan Validation – Compliance", raport_mpzp)

# ----------------------------------------------------------------------------------------------- commit ---------------------------------------------------------------------------------------------------------
t.Commit()
TaskDialog.Show("Completed", "Building generation complete.")
