<div align="center"><img width="100" height="100" alt="Snode Logo" src="https://github.com/user-attachments/assets/6000ccb0-90d3-4d73-a40e-e599fb3f5b77" />
  
# Snode

**Un piccolo runtime scritto in Python che ricrea l'esperienza di Node.js.**

[![CI](https://github.com/snodeproject/snode/actions/workflows/ci.yml/badge.svg)](https://github.com/snodeproject/snode/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Top Language](https://img.shields.io/github/languages/top/snodeproject/snode)](https://github.com/snodeproject/snode)
[![Stars](https://img.shields.io/github/stars/snodeproject/snode)](https://github.com/snodeproject/snode/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/snodeproject/snode)](https://github.com/snodeproject/snode/commits/main)


</div>

---

## Avvio rapido

### 1. Clona il repository

```bash
git clone https://github.com/snodeproject/snode.git
cd snode
```

### 2. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Avvia la REPL

```bash
python snode.py
```

### 4. Crea il tuo primo programma

Crea un file chiamato `hello_world.js`:

```javascript
console.log("Hello Snode World");
```

### 5. Esegui il file

```bash
python snode.py hello_world.js
```

---

## Guida ai comandi

Visualizza tutti i comandi disponibili di Snode:

```bash
python snode.py -h
```

Visualizza i comandi del gestore di pacchetti SPM:

```bash
python snode.py spm -h
```

---

## SPM (Snode Package Manager)

Installa un pacchetto globalmente:

```bash
python snode.py spm install tip -g
```

Installa un pacchetto nel progetto corrente:

```bash
python snode.py spm install tip
```

---

## Licenza

Questo progetto è distribuito sotto la licenza MIT.

Per maggiori dettagli consulta il file [LICENSE](https://github.com/snodeproject/snode/blob/main/LICENSE).
