// Snode: pi greco semplice
// Reference: https://snode.js.org
const simplePi = "3.149389273920910063916301";

const selection = prompt("Dimmi un numero e ti dirò se è nel pi greco semplice:");

if (simplePi.includes(selection)) {
  console.log("È nel pi greco!");
} else {
  console.log("Non c'è!");
}

// Esempio output:
// Dimmi un numero e ti dirò se è nel pi greco semplice: 149
// È nel pi greco!
