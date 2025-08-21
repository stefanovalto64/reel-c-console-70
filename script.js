const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const menu = document.getElementById("menu");

let gameLoop;
let width = 640, height = 480;
let scale = 1.0;

// ================== SUONI SINTETIZZATI ==================
function playTone(freq, dur, vol = 0.3) {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const osc = audioContext.createOscillator();
  const gain = audioContext.createGain();
  osc.connect(gain);
  gain.connect(audioContext.destination);
  osc.frequency.value = freq;
  gain.gain.value = vol;
  osc.start();
  setTimeout(() => osc.stop(), dur);
}

const sounds = {
  paddle: () => playTone(523, 60),
  wall: () => playTone(392, 80),
  point: () => playTone(220, 150),
  goal: () => {
    [659, 784, 1047, 1318].forEach((f, i) => setTimeout(() => playTone(f, 100), i * 100));
  },
  victory: () => {
    [523, 659, 784, 1047].forEach((f, i) => setTimeout(() => playTone(f, 150), i * 150));
  }
};

// ================== GESTIONE RISOLUZIONE ==================
function changeResolution() {
  const value = document.getElementById("resolution").value;
  if (value === "1") {
    width = 640; height = 480; scale = 1.0;
  } else if (value === "1.6") {
    width = 1024; height = 768; scale = 1.6;
  } else {
    const w = window.screen.width * 0.98;
    const h = window.screen.height * 0.98;
    width = Math.floor(w); height = Math.floor(h);
    scale = height / 480;
  }
  canvas.width = width;
  canvas.height = height;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(scale, scale);
}

// ================== BOOT SEQUENCE ==================
function bootSequence() {
  menu.style.display = "none";
  canvas.style.display = "block";

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(scale, scale);

  // Reset canvas
  ctx.fillStyle = "black";
  ctx.fillRect(0, 0, 640, 480);

  // Testi fissi
  const title = "REEL C";
  const version = "1978";
  const loading = "LOADING...";

  // Posizioni
  const titleX = 320 - 60;
  const versionX = 320 - 40;
  const loadingX = 320 - 70;
  const titleY = 240 - 60;
  const versionY = 240 - 30;
  const loadingY = 240 + 10;

  // Font
  ctx.font = "24px Courier";
  ctx.fillStyle = "green";

  // Fase 1: mostra "REEL C", "1978", "LOADING..." + suono
  ctx.fillText(title, titleX, titleY);
  ctx.fillText(version, versionX, versionY);
  ctx.fillText(loading, loadingX, loadingY);
  applyCRT();
  canvas.style.display = "block";
  sounds.point(); // Suono iniziale (220 Hz)

  let flashCount = 0;
  let showLoading = true;

  // Fase 2: lampeggio per 5 cicli (0.5s on / 0.5s off)
  const flashInterval = setInterval(() => {
    ctx.clearRect(0, 0, 640, 480);

    if (showLoading) {
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, 640, 480);
      ctx.fillStyle = "green";
      ctx.fillText(title, titleX, titleY);
      ctx.fillText(version, versionX, versionY);
      ctx.fillText(loading, loadingX, loadingY);
      applyCRT();
    } else {
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, 640, 480);
    }

    showLoading = !showLoading;
    flashCount++;

    if (flashCount >= 10) { // 5 cicli * 2 (on/off) = 10
      clearInterval(flashInterval);
      // Fase 3: "READY TO PLAY"
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, 640, 480);
      ctx.fillStyle = "green";
      ctx.fillText("READY TO PLAY", 320 - 100, 240);
      applyCRT();
      sounds.paddle(); // Suono acuto

      // Dopo 1 secondo, mostra il menu
      setTimeout(() => {
        showResolutionMenu();
      }, 1000);
    }
  }, 500); // 0.5 secondi per stato
}

// ================== APPLICA EFFETTO CRT ==================
function applyCRT() {
  // Il CSS gestisce le scanlines via ::after
  // Ma possiamo aggiungere un leggero filtro se voluto (opzionale)
}

// ================== MENU RISOLUZIONE ==================
function showResolutionMenu() {
  canvas.style.display = "none";
  menu.style.display = "flex";
  document.getElementById("resolution").value = "1";
}

// ================== INPUT ==================
const keys = {};
window.addEventListener("keydown", e => {
  keys[e.keyCode] = true;
  if (e.keyCode === 71 && currentGame && currentGame.waiting) {
    currentGame.waiting = false;
    if (currentGame.reset) currentGame.reset();
  }
  if (e.keyCode === 80 && currentGame && !currentGame.waiting && !currentGame.gameOver && !currentGame.matchOver) {
    if (!currentGame.paused) {
      currentGame.paused = true;
    } else {
      currentGame.paused = false;
    }
  }
});
window.addEventListener("keyup", e => {
  keys[e.keyCode] = false;
});

// ================== GIOCHI ==================
let currentGame = null;

function startGame(game) {
  menu.style.display = "none";
  canvas.style.display = "block";
  cancelAnimationFrame(gameLoop);

  if (game === "tennis") currentGame = new Tennis();
  if (game === "calcio") currentGame = new Soccer();
  if (game === "pelota") currentGame = new Pelota();
  if (game === "squash") currentGame = new Squash();

  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(scale, scale);
  loop();
}

function loop() {
  ctx.clearRect(0, 0, 640, 480);
  if (currentGame && currentGame.update && currentGame.draw) {
    currentGame.update();
    currentGame.draw();
  }
  gameLoop = requestAnimationFrame(loop);
}

// --- Inserisci qui i giochi: Tennis, Soccer, Pelota, Squash ---
// (usa il codice dei giochi che ti ho già inviato, senza modifiche)
// Assicurati che siano tutti presenti dopo questa sezione

// ================== AVVIO ==================
// Avvia il boot quando la pagina è pronta
window.onload = function () {
  changeResolution(); // Inizializza risoluzione
  bootSequence();     // Avvia il boot
};