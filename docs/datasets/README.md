##  1. Descrierea Setului de Date

### 1.1 Sursa datelor

Setul de date pentru acest proiect este compus din imagini ce reprezintă diferite elemente de caroserie auto: ușă stângă, ușă dreaptă, aripă, capotă și portbagaj.
Imaginile sunt obținute prin generare programatică (simulare), folosind contururi geometrice simple care imită formele reale ale acestor piese. Această abordare permite control total asupra datelor și o distribuție echilibrată între clase.

Modul de achiziție: generare programatică în Python
Condiții: toate imaginile sunt generate uniform, în rezoluție controlată, cu iluminare și fundal standardizate.

### 1.2 Caracteristicile dataset-ului

Număr total de imagini: se va actualiza după generare

Clase: 5 (ușă stânga, ușă dreaptă, aripă, capotă, portbagaj)

Format: PNG / grayscale

Tip date: imagini

Dimensiune finală: 128×128 px după preprocesare

Canale: 1 (grayscale)

### 1.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| pixel_intensity | numeric | 0-255 | valoarea fiecărui pixel din imagine | [0, 255] |
| width | numeric | px | lățimea imaginii (standardizată în preprocesare) | 128 |
| height | numeric | px | înălțimea imaginii (standardizată în preprocesare) | 128 |
| class_label | categorial | - | tipul piesei (una dintre cele 5 clasee) | {usa_stanga, usa_dreapta, aripa, capota, portbagaj} |

**Fișier recomandat:**  `data/README.md`

---

##  2. Analiza Exploratorie a Datelor (EDA) – Sintetic

### 2.1 Statistici descriptive aplicate

În această etapă, asupra dataset-ului au fost aplicate următoarele analize statistice:

Distribuția numărului de imagini per clasă

Verificarea rezoluției și consistenței imaginilor brute

Identificarea pixelilor nevalabili sau anomalii vizuale

Calcularea histogramelor de intensitate pentru un eșantion de imagini

Identificarea eventualelor diferențe mari între formele generate

### 2.2 Analiza calității datelor

Nu au fost identificate valori lipsă, deoarece dataset-ul este generat programatic.

Toate imaginile au fost verificate pentru consistență (dimensiuni similare).

Unele forme generate pot fi prea apropiate ca structură, ceea ce poate crea confuzii pentru model.

Distribuția claselor este echilibrată, deoarece toate părțile sunt generate în număr egal.

### 2.3 Probleme identificate

Unele contururi pot necesita netezire suplimentară pentru a evita zgomotul.

Marginile obiectelor pot apărea aliased la scalare.

Clase precum „ușă stângă” și „ușă dreaptă” sunt foarte apropiate ca formă, diferența majoră fiind orientarea, ceea ce necesită augmentări suplimentare pentru antrenare.

---

##  3. Preprocesarea Datelor

### 3.1 Curățarea datelor

Pașii care vor fi aplicați în scriptul de preprocesare:

Eliminarea imaginilor duplicate (dacă apar).

Eliminarea imaginilor corupte (în practică, puțin probabil la date generate).

Standardizarea dimensiunilor tuturor imaginilor.

Eliminarea zgomotului prin thresholding sau filtrare.

### 3.2 Transformarea caracteristicilor

Transformările planificate:

Conversia în grayscale (pentru consistență).

Redimensionarea tuturor imaginilor la 128×128 px.

Normalizarea valorilor pixelilor la intervalul [0, 1].

Extracția de contururi folosind Canny, dacă este necesar.

Calcularea unor descriptor geometrice (Hu Moments) dacă modelul va fi de tip MLP.

### 3.3 Structurarea seturilor de date

Imaginile vor fi împărțite după principii standard în machine learning:

Train: aproximativ 70%

Validation: aproximativ 15%

Test: aproximativ 15%

Împărțirea este realizată cu stratificare, astfel încât fiecare clasă să fie reprezentată proporțional în toate seturile.

### 3.4 Salvarea rezultatelor preprocesării

Toate datele rezultate în urma preprocesării sunt salvate astfel:

Imaginile curățate: data/processed/

Setul de antrenare: data/train/

Setul de validare: data/validation/

Setul de test: data/test/

Codul utilizat: src/preprocessing/

Parametrii de procesare (dacă sunt necesari): config/

---

##  4. Fișiere Generate în Această Etapă

În urma etapei 3 vor exista:

folderul data/raw/ cu imaginile brute

folderul data/processed/ cu imaginile standardizate

folderele train/, validation/, test/

scripturile de preprocesare în src/preprocessing/

documentația dataset-ului în data/README.md

structură GitHub complet funcțională

---

##  5. Stare Etapă (de completat de student)

- [✅] Structură repository configurată
- [✅] Dataset analizat (EDA realizată)
- [✅] Date preprocesate
- [✅] Seturi train/val/test generate
- [✅] Documentație actualizată în README + `data/README.md`

---
