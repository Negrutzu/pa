# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Negru Adam Andrei Pablo
**Data:** 21-11-2025

---

## Introducere

Acest proiect urmărește dezvoltarea unui sistem bazat pe rețele neuronale capabil să identifice și să clasifice automat diferite elemente de caroserie auto pe baza formei lor:

ușă stângă

ușă dreaptă

aripă față

capotă

portbagaj

Sistemul este util în aplicații industriale, în special în procesele de control calitate și logistică din industria automotive, unde identificarea rapidă și sigură a pieselor reduce erorile umane și optimizează fluxul de lucru.

Etapa 3 se concentrează pe analiza și pregătirea setului de date, astfel încât modelul neural să poată fi instruit ulterior în condiții optime.

---

## Structura Repository-ului Github (versiunea Etapei 3)

Pentru etapa curentă am creat structura completă a repository-ului, astfel încât toate componentele proiectului să fie organizate clar și ușor de accesat. Structura include foldere pentru date brute, date preprocesate, cod sursă, documentație și configurații. Această organizare respectă cerințele laboratorului și facilitează următoarele etape ale proiectului, mai ales preprocesarea și antrenarea rețelei neuronale.

```
project-name/
├── README.md
├── docs/
│   └── datasets/          # descriere seturi de date, surse, diagrame
├── data/
│   ├── raw/               # date brute
│   ├── processed/         # date curățate și transformate
│   ├── train/             # set de instruire
│   ├── validation/        # set de validare
│   └── test/              # set de testare
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
└── requirements.txt       # dependențe Python (dacă aplicabil)
```
