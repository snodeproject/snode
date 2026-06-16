<div align="center">
  
  <img width="100" height="100" alt="17253" src="https://github.com/user-attachments/assets/6000ccb0-90d3-4d73-a40e-e599fb3f5b77" />

  # Snode

</div>

Snode è un piccolo programma scritto in Python che ricrea l'esperienza di Node.js.

---

## Quick startup

- Inizia così:
  1. Scarica il codice sorgente: `git clone https://github.com/snodeproject/snode.git`
  2. Scarica le dipendenze: `pip install -r requirements.txt`
  3. Avvia la REPL: `python snode.py`
  4. Crea un file `hello_world.js` e scrivici `console.log("Hello Snode World")`
  5. Avvialo con `python snode.py hello_world.js`
- Poi esplora i comandi:
  1. Usa `python snode.py -h` per i comandi di Snode
  2. Poi usa `python snode.py spm -h` per quelli di SPM
- Esplora SPM:
  1. Installa un pacchetto: globalmente: `python snode.py spm install tip -g` per iniziare; per il progetto: `python snode.py spm install tip` per iniziare
 
---

## Licenza

Snode è secondo la licenza MIT. Vedi il file [LICENSE](https://github.com/snodeproject/snode/blob/main/LICENSE) per più informazioni.
