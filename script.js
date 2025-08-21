const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const menu = document.getElementById("menu");

let gameLoop;
let width = 640, height = 480;
let scale = 1.0;

// Suoni sintetizzati
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
  if (currentGame && currentGame.resize) currentGame.resize();
}

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
  currentGame.update();
  currentGame.draw();
  gameLoop = requestAnimationFrame(loop);
}

// ================== INPUT ==================
const keys = {};
window.addEventListener("keydown", e => {
  keys[e.keyCode] = true;
  if (e.keyCode === 71 && currentGame && currentGame.waiting) {
    currentGame.waiting = false;
    if (currentGame.reset) currentGame.reset();
  }
  if (e.keyCode === 80 && !currentGame.waiting && !currentGame.gameOver) {
    currentGame.paused = !currentGame.paused;
  }
});
window.addEventListener("keyup", e => {
  keys[e.keyCode] = false;
});

// Avvia boot
changeResolution();