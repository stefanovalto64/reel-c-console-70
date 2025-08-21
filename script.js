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

// ================== INPUT ==================
const keys = {};
window.addEventListener("keydown", e => {
  keys[e.keyCode] = true;
  if (e.keyCode === 71 && currentGame && currentGame.waiting) {
    currentGame.waiting = false;
    if (currentGame.reset) currentGame.reset();
  }
  if (e.keyCode === 80 && currentGame && !currentGame.waiting && !currentGame.gameOver && !currentGame.matchOver) {
    currentGame.paused = !currentGame.paused;
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

// ================== TENNIS ==================
class Tennis {
  constructor() {
    this.speed = 7;
    this.p1y = 200; this.p2y = 200;
    this.ball = { x: 320, y: 240, dx: 5, dy: 3 };
    this.score1 = 0; this.score2 = 0;
    this.level = 1;
    this.wins1 = 0; this.wins2 = 0;
    this.matchOver = false;
    this.waiting = true;
    this.starter = null;
    this.paused = false;
    this.showStarter = false;
    this.starterTime = 0;
  }

  reset() {
    const mag = 5 * (1 + 0.15 * (this.level - 1));
    this.ball = {
      x: 320,
      y: 240,
      dx: (Math.random() > 0.5 ? 1 : -1) * mag,
      dy: (Math.random() > 0.5 ? 1 : -1) * mag
    };
  }

  update() {
    if (this.waiting || this.matchOver || this.paused) return;

    this.ball.x += this.ball.dx;
    this.ball.y += this.ball.dy;

    if (this.ball.y < 0 || this.ball.y > 480) {
      this.ball.dy *= -1;
      sounds.wall();
    }

    if (this.ball.x < 20 && this.p1y < this.ball.y && this.ball.y < this.p1y + 66) {
      this.ball.dx *= -1.1;
      sounds.paddle();
    }
    if (this.ball.x > 620 && this.p2y < this.ball.y && this.ball.y < this.p2y + 66) {
      this.ball.dx *= -1.1;
      sounds.paddle();
    }

    if (this.ball.x < 0) {
      this.score2++;
      sounds.point();
      if (this.score2 >= 7) {
        this.wins2++;
        this.level++;
        this.score1 = this.score2 = 0;
        if (this.wins2 >= 3) {
          this.matchOver = true;
          return;
        }
      }
      this.reset();
    }
    if (this.ball.x > 640) {
      this.score1++;
      sounds.point();
      if (this.score1 >= 7) {
        this.wins1++;
        this.level++;
        this.score1 = this.score2 = 0;
        if (this.wins1 >= 3) {
          this.matchOver = true;
          return;
        }
      }
      this.reset();
    }

    if (keys[83] && this.p1y > 0) this.p1y -= this.speed;
    if (keys[88] && this.p1y < 414) this.p1y += this.speed;
    if (keys[38] && this.p2y > 0) this.p2y -= this.speed;
    if (keys[40] && this.p2y < 414) this.p2y += this.speed;
  }

  draw() {
    ctx.fillStyle = "black"; ctx.fillRect(0, 0, 640, 480);
    this.drawNet();
    ctx.fillStyle = "green"; ctx.fillRect(10, this.p1y, 8, 66);
    ctx.fillStyle = "white"; ctx.fillRect(622, this.p2y, 8, 66);
    ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(this.ball.x, this.ball.y, 6, 0, Math.PI*2); ctx.fill();

    this.drawScore();
    ctx.fillStyle = "yellow";
    ctx.fillText(`Livello: ${this.level}`, 540, 20);
    ctx.fillText(`Vittorie - Verde: ${this.wins1} Bianco: ${this.wins2}`, 10, 20);

    if (this.waiting) {
      ctx.fillStyle = "yellow";
      ctx.fillText("Premere G per iniziare", 240, 90);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per pausa", 240, 120);
    }
    if (this.matchOver) {
      ctx.fillStyle = "white";
      ctx.font = "bold 40px Courier";
      ctx.fillText("MATCH FINITO!", 200, 240);
    }
    if (this.paused) {
      ctx.fillStyle = "white";
      ctx.fillText("GIOCO IN PAUSA", 260, 240);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per riprendere", 220, 270);
    }
  }

  drawNet() {
    ctx.strokeStyle = "white";
    for (let y = 0; y < 480; y += 20) {
      ctx.beginPath();
      ctx.moveTo(318, y);
      ctx.lineTo(322, y + 10);
      ctx.stroke();
    }
  }

  drawScore() {
    ctx.font = "76px Arial";
    const s1 = this.score1.toString();
    const s2 = this.score2.toString();
    const total = ctx.measureText(s1 + ":" + s2).width;
    const x = 320 - total / 2;
    ctx.fillStyle = "white";
    ctx.fillText(s1, x, 80);
    ctx.fillText(":", x + ctx.measureText(s1).width, 80);
    ctx.fillText(s2, x + ctx.measureText(s1 + ":").width, 80);

    ctx.font = "24px Courier";
    ctx.fillStyle = "green"; ctx.fillText("VERDE", x + 5, 20);
    ctx.fillStyle = "white"; ctx.fillText("BIANCO", x + ctx.measureText(s1 + ":").width + 5, 20);
  }
}

// ================== CALCIO ==================
class Soccer {
  constructor() {
    this.ball = { x: 320, y: 240, dx: 4, dy: 3 };
    this.player1 = { y: 225, w: 10, h: 30 };
    this.player2 = { y: 225, w: 10, h: 30 };
    this.score1 = 0; this.score2 = 0;
    this.lastHitter = null;
    this.speedMult = 1.0;
    this.goalMode = false;
    this.goalTimer = 0;
    this.waiting = true;
    this.starter = null;
    this.paused = false;
  }

  collides(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }

  reset() {
    const mag = 4 * this.speedMult;
    this.ball = {
      x: 320,
      y: 240,
      dx: (Math.random() > 0.5 ? 1 : -1) * mag,
      dy: (Math.random() > 0.5 ? 1 : -1) * mag
    };
  }

  update() {
    if (this.waiting || this.goalMode || this.paused) return;

    this.ball.x += this.ball.dx;
    this.ball.y += this.ball.dy;

    if (this.ball.y < 0 || this.ball.y > 480) {
      this.ball.dy *= -1;
      sounds.wall();
    }

    const b = { x: this.ball.x - 12, y: this.ball.y - 12, w: 24, h: 24 };
    const p1 = { x: 30, y: this.player1.y, w: 10, h: 30 };
    const p2 = { x: 600, y: this.player2.y, w: 10, h: 30 };

    if (this.collides(b, p1)) {
      this.ball.dx *= -1.1;
      this.lastHitter = 'p1';
      sounds.paddle();
    }
    if (this.collides(b, p2)) {
      this.ball.dx *= -1.1;
      this.lastHitter = 'p2';
      sounds.paddle();
    }

    if (this.ball.x < 20 && 200 < this.ball.y && this.ball.y < 280) {
      this.score2 += 5;
      this.speedMult *= 1.05;
      sounds.goal();
      this.goalMode = true;
      this.goalTimer = 100;
      setTimeout(() => this.reset(), 1600);
      return;
    }
    if (this.ball.x > 620 && 200 < this.ball.y && this.ball.y < 280) {
      this.score1 += 5;
      this.speedMult *= 1.05;
      sounds.goal();
      this.goalMode = true;
      this.goalTimer = 100;
      setTimeout(() => this.reset(), 1600);
      return;
    }

    if (this.ball.x > 640 && this.lastHitter === 'p1') {
      this.score1++;
      sounds.point();
      this.reset();
    }
    if (this.ball.x < 0 && this.lastHitter === 'p2') {
      this.score2++;
      sounds.point();
      this.reset();
    }

    if (keys[83] && this.player1.y > 0) this.player1.y -= 6;
    if (keys[88] && this.player1.y < 450) this.player1.y += 6;
    if (keys[38] && this.player2.y > 0) this.player2.y -= 6;
    if (keys[40] && this.player2.y < 450) this.player2.y += 6;
  }

  draw() {
    ctx.fillStyle = "black"; ctx.fillRect(0, 0, 640, 480);
    this.drawField();
    ctx.fillStyle = "green"; ctx.fillRect(30, this.player1.y, 10, 30);
    ctx.fillStyle = "white"; ctx.fillRect(600, this.player2.y, 10, 30);
    ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(this.ball.x, this.ball.y, 12, 0, Math.PI*2); ctx.fill();

    this.drawScore();
    ctx.fillStyle = "yellow";
    ctx.fillText(`LIV: ${Math.floor(this.speedMult / 1.05) + 1}`, 540, 20);

    if (this.waiting) {
      ctx.fillStyle = "yellow";
      ctx.fillText("Premere G per iniziare", 240, 90);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per pausa", 240, 120);
    }
    if (this.goalMode) {
      ctx.fillStyle = "yellow";
      ctx.font = "bold 140px Arial";
      ctx.fillText("GOAL!", 180, 240);
      ctx.font = "24px Arial";
      const who = this.lastHitter === 'p1' ? "VERDE" : "BIANCO";
      ctx.fillStyle = who === "VERDE" ? "green" : "white";
      ctx.fillText(`Il giocatore ${who} ha segnato!`, 240, 280);
    }
    if (this.paused) {
      ctx.fillStyle = "white";
      ctx.fillText("GIOCO IN PAUSA", 260, 240);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per riprendere", 220, 270);
    }
  }

  drawField() {
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 620, 460);
    ctx.beginPath(); ctx.moveTo(320, 10); ctx.lineTo(320, 470); ctx.stroke();
    ctx.beginPath(); ctx.arc(320, 240, 70, 0, Math.PI*2); ctx.stroke();
    // Porte
    ctx.strokeRect(0, 200, 20, 80);
    ctx.strokeRect(620, 200, 20, 80);
    // Angoli
    for (let [x, y] of [[0,0], [620,0], [0,460], [620,460]]) {
      ctx.beginPath(); ctx.arc(x + 10, y + 10, 10, 0, Math.PI/2); ctx.stroke();
    }
  }

  drawScore() {
    ctx.font = "76px Arial";
    const s1 = this.score1.toString();
    const s2 = this.score2.toString();
    const total = ctx.measureText(s1 + ":" + s2).width;
    const x = 320 - total / 2;
    ctx.fillStyle = "white";
    ctx.fillText(s1, x, 80);
    ctx.fillText(":", x + ctx.measureText(s1).width, 80);
    ctx.fillText(s2, x + ctx.measureText(s1 + ":").width, 80);

    ctx.font = "24px Courier";
    ctx.fillStyle = "green"; ctx.fillText("VERDE", x + 5, 20);
    ctx.fillStyle = "white"; ctx.fillText("BIANCO", x + ctx.measureText(s1 + ":").width + 5, 20);
  }
}

// ================== PELOTA ==================
class Pelota {
  constructor() {
    this.ball = { x: 320, y: 240, dx: -5, dy: 3 };
    this.paddle = { y: 200, w: 10, h: 66 };
    this.baseSpeed = 5;
    this.level = 1;
    this.hits = 0;
    this.score = 0;
    this.best = 0;
    this.waiting = true;
    this.paused = false;
  }

  getSpeed() {
    return this.baseSpeed * (1 + 0.2 * (this.level - 1));
  }

  reset() {
    const mag = this.getSpeed();
    this.ball = {
      x: 320,
      y: 240,
      dx: -mag,
      dy: (Math.random() > 0.5 ? 1 : -1) * mag
    };
  }

  update() {
    if (this.waiting || this.paused) return;

    this.ball.x += this.ball.dx;
    this.ball.y += this.ball.dy;

    if (this.ball.y < 0 || this.ball.y > 480) {
      this.ball.dy *= -1;
      sounds.wall();
    }

    if (this.ball.x < 40) {
      this.ball.dx = Math.abs(this.ball.dx);
      sounds.wall();
    }

    if (this.ball.x > 590 && this.paddle.y < this.ball.y && this.ball.y < this.paddle.y + 66) {
      this.ball.dx = -this.getSpeed();
      this.hits++;
      this.score++;
      if (this.score > this.best) this.best = this.score;
      if (this.score % 10 === 0 && this.level < 6) this.level++;
      sounds.paddle();
    }

    if (this.ball.x > 640) {
      sounds.point();
      this.score = 0;
      this.hits = 0;
      this.level = 1;
      this.reset();
    }

    if (keys[38] && this.paddle.y > 0) this.paddle.y -= 7;
    if (keys[40] && this.paddle.y < 414) this.paddle.y += 7;
  }

  draw() {
    ctx.fillStyle = "black"; ctx.fillRect(0, 0, 640, 480);
    this.drawWall();
    ctx.fillStyle = "white"; ctx.fillRect(590, this.paddle.y, 10, 66);
    ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(this.ball.x, this.ball.y, 10, 0, Math.PI*2); ctx.fill();

    ctx.font = "76px Arial";
    ctx.fillStyle = "white";
    ctx.fillText(this.score, 320 - ctx.measureText(this.score).width / 2, 80);
    ctx.font = "24px Courier";
    ctx.fillText(`BEST: ${this.best}`, 500, 20);
    ctx.fillText(`HITS: ${this.hits} VEL: ${this.getSpeed().toFixed(2)} LIV: ${this.level}`, 10, 470);

    if (this.waiting) {
      ctx.fillStyle = "yellow";
      ctx.fillText("Premere G per iniziare", 240, 90);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per pausa", 240, 120);
    }
    if (this.paused) {
      ctx.fillStyle = "white";
      ctx.fillText("GIOCO IN PAUSA", 260, 240);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per riprendere", 220, 270);
    }
  }

  drawWall() {
    ctx.strokeStyle = "white";
    for (let y = 0; y < 480; y += 12) {
      const offset = (y % 24 === 0) ? 0 : 10;
      for (let x = -offset; x < 40; x += 20) {
        ctx.strokeRect(x, y, 20, 12);
      }
    }
  }
}

// ================== SQUASH ==================
class Squash {
  constructor() {
    this.ball = { x: 60, y: 240, dx: 5, dy: 3 };
    this.p1y = 200; this.p2y = 200;
    this.score1 = 0; this.score2 = 0;
    this.lastHitter = null;
    this.speedMult = 1.0;
    this.gameOver = false;
    this.winner = null;
    this.waiting = true;
    this.starter = Math.random() > 0.5 ? "VERDE" : "BIANCO";
    this.paused = false;
  }

  collides(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }

  reset() {
    const mag = 5 * this.speedMult;
    this.ball = {
      x: 60,
      y: 240,
      dx: mag,
      dy: (Math.random() > 0.5 ? 1 : -1) * mag
    };
  }

  update() {
    if (this.waiting || this.gameOver || this.paused) return;

    this.ball.x += this.ball.dx;
    this.ball.y += this.ball.dy;

    if (this.ball.y < 0 || this.ball.y > 480) {
      this.ball.dy *= -1;
      sounds.wall();
    }
    if (this.ball.x < 0) {
      this.ball.dx *= -1;
      sounds.wall();
    }

    const b = { x: this.ball.x - 10, y: this.ball.y - 10, w: 20, h: 20 };
    const p1 = { x: 580, y: this.p1y, w: 10, h: 66 }; // verde
    const p2 = { x: 610, y: this.p2y, w: 10, h: 66 }; // bianco

    if (this.collides(b, p1) && this.ball.dx > 0) {
      if (this.lastHitter === 'p2') {
        this.score1++;
        sounds.point();
        this.speedMult *= 1.15;
        this.reset();
        if (this.score1 >= 100) {
          this.gameOver = true;
          this.winner = "BIANCO";
        }
      } else {
        this.ball.dx *= -1.1;
        this.ball.dy += (this.ball.y - this.p1y - 33) / 10;
        this.lastHitter = 'p1';
        sounds.paddle();
      }
    }

    if (this.collides(b, p2) && this.ball.dx > 0) {
      if (this.lastHitter === 'p1') {
        this.score2++;
        sounds.point();
        this.speedMult *= 1.15;
        this.reset();
        if (this.score2 >= 100) {
          this.gameOver = true;
          this.winner = "VERDE";
        }
      } else {
        this.ball.dx *= -1.1;
        this.ball.dy += (this.ball.y - this.p2y - 33) / 10;
        this.lastHitter = 'p2';
        sounds.paddle();
      }
    }

    if (this.ball.x > 640) {
      if (this.lastHitter === 'p1') this.score2++;
      else if (this.lastHitter === 'p2') this.score1++;
      sounds.point();
      this.speedMult *= 1.15;
      this.reset();
      if (this.score1 >= 100) {
        this.gameOver = true;
        this.winner = "BIANCO";
      } else if (this.score2 >= 100) {
        this.gameOver = true;
        this.winner = "VERDE";
      }
    }

    if (keys[83] && this.p1y > 0) this.p1y -= 7;
    if (keys[88] && this.p1y < 414) this.p1y += 7;
    if (keys[38] && this.p2y > 0) this.p2y -= 7;
    if (keys[40] && this.p2y < 414) this.p2y += 7;
  }

  draw() {
    ctx.fillStyle = "black"; ctx.fillRect(0, 0, 640, 480);
    ctx.strokeStyle = "white"; ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, 640, 480);

    ctx.fillStyle = "green"; ctx.fillRect(580, this.p1y, 10, 66);
    ctx.fillStyle = "white"; ctx.fillRect(610, this.p2y, 10, 66);

    if (!this.gameOver && !this.waiting && !this.paused) {
      ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(this.ball.x, this.ball.y, 10, 0, Math.PI*2); ctx.fill();
    }

    this.drawScore();
    ctx.fillStyle = "yellow";
    ctx.fillText(`LIV: ${Math.max(1, Math.floor(Math.max(this.score1, this.score2) / 10) + 1)}`, 540, 20);

    const tocca = this.lastHitter === 'p1' ? "VERDE" : this.lastHitter === 'p2' ? "BIANCO" : this.starter;
    const col = tocca === "VERDE" ? "green" : "white";
    ctx.fillStyle = col;
    ctx.fillText(`Tocca al giocatore: ${tocca}`, 320 - ctx.measureText(`Tocca al giocatore: ${tocca}`).width / 2, 120);

    if (this.waiting) {
      ctx.fillStyle = "yellow";
      ctx.fillText("Premere G per iniziare", 240, 90);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per pausa", 240, 120);
      ctx.fillStyle = this.starter === "VERDE" ? "green" : "white";
      ctx.fillText(`Inizia: ${this.starter}`, 240, 150);
    }
    if (this.paused) {
      ctx.fillStyle = "white";
      ctx.fillText("GIOCO IN PAUSA", 260, 240);
      ctx.fillStyle = "orange";
      ctx.fillText("Premere P per riprendere", 220, 270);
    }
    if (this.gameOver) {
      ctx.fillStyle = this.winner === "VERDE" ? "green" : "white";
      ctx.font = "bold 40px Courier";
      ctx.fillText("VITTORIA:", 230, 240);
      ctx.fillText(this.winner, 280, 290);
      ctx.fillStyle = "white";
      ctx.font = "24px Courier";
      ctx.fillText("ESC per uscire", 270, 330);
    }
  }

  drawScore() {
    ctx.font = "76px Arial";
    const s1 = this.score1.toString();
    const s2 = this.score2.toString();
    const total = ctx.measureText(s1 + ":" + s2).width;
    const x = 320 - total / 2;
    ctx.fillStyle = "white";
    ctx.fillText(s1, x, 80);
    ctx.fillText(":", x + ctx.measureText(s1).width, 80);
    ctx.fillText(s2, x + ctx.measureText(s1 + ":").width, 80);

    ctx.font = "24px Courier";
    ctx.fillStyle = "green"; ctx.fillText("VERDE", x + 5, 20);
    ctx.fillStyle = "white"; ctx.fillText("BIANCO", x + ctx.measureText(s1 + ":").width + 5, 20);
  }
}

// ================== AVVIO ==================
changeResolution(); // Inizializza risoluzione