# Contributing to Snode

Grazie per il tuo interesse nel contribuire a Snode.  
Queste linee guida spiegano come partecipare allo sviluppo del progetto, proporre modifiche e segnalare problemi.

---

## Tipi di contributi accettati

Puoi contribuire in diversi modi:

- Segnalare bug  
- Proporre nuove funzionalità  
- Migliorare la documentazione  
- Aggiungere esempi o tutorial  
- Migliorare il codice Python del runtime  
- Migliorare i moduli JavaScript integrati  
- Proporre miglioramenti al package manager SPM  

---

## Segnalare un bug

Per segnalare un bug, utilizza i template dedicati:

- Bug Report  
- Crash Report  
- Question / Help (per dubbi non tecnici)

Assicurati di includere:

- Versione di Snode  
- Versione di Python  
- Sistema operativo  
- Codice coinvolto  
- Log completi  

---

## Proporre una nuova funzionalità

Per proporre una feature, usa il template Feature Request.

Includi:

- Descrizione chiara della funzionalità  
- Motivazione  
- Esempio di utilizzo in JavaScript  
- Area del runtime coinvolta (HTTP, fs, event loop, SPM, ecc.)  
- Eventuali alternative considerate  

---

## Come contribuire al codice

### Fork del repository

Clona il repository sul tuo computer e accedi alla cartella del progetto.

### Crea un branch dedicato

Usa un nome chiaro, ad esempio:  
feature/nome-feature oppure fix/nome-bug.

### Rispetta lo stile del progetto

- Mantieni il codice Python semplice e leggibile  
- Evita dipendenze non necessarie  
- Mantieni i moduli JS coerenti con lo stile Node.js  
- Aggiungi commenti dove utile  
- Evita breaking changes senza discuterne prima  

### Testa le modifiche

Assicurati che:

- Snode si avvii correttamente  
- I comandi CLI funzionino (help, spm, ecc.)  
- I moduli coinvolti non introducano regressioni  

### Apri una Pull Request

La PR deve includere:

- Descrizione chiara del cambiamento  
- Motivazione  
- Eventuali screenshot o esempi  
- Riferimento all’issue correlata (se esiste)  

---

## Test e CI

Il progetto utilizza GitHub Actions per:

- Installare le dipendenze  
- Eseguire Snode  
- Verificare i comandi CLI  
- Testare SPM  

Assicurati che la tua PR non rompa la CI.

---

## Documentazione

Se aggiungi una nuova funzionalità:

- Aggiorna il README  
- Aggiungi esempi  
- Documenta eventuali nuove API JS  
- Aggiorna la sezione SPM se necessario  

---

## Comportamento nella community

Tutti i contributori devono rispettare il Codice di Condotta del progetto.

---

## Grazie

Snode è un progetto open‑source costruito dalla community.  
Ogni contributo, piccolo o grande, aiuta il runtime a crescere e migliorare.
