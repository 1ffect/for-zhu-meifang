const root = document.documentElement;
const body = document.body;
const petalLayer = document.querySelector("#petal-layer");
const sparkleLayer = document.querySelector("#sparkle-layer");
const revealTargets = document.querySelectorAll("[data-reveal]");
const letterScene = document.querySelector("#letter-scene");
const letter = document.querySelector("#letter");
const openExperienceButton = document.querySelector("#open-experience");
const toggleStageButton = document.querySelector("#toggle-stage");
const sealButton = document.querySelector("#seal-button");
const toggleNoteButton = document.querySelector("#toggle-note");

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const coarsePointer = window.matchMedia("(pointer: coarse)");

function createPetals(count = 28) {
  if (!petalLayer) return;

  const petalColors = [
    ["#f3d2da", "#d7889b"],
    ["#f5dcc8", "#e2a181"],
    ["#f7e6b0", "#edc766"],
  ];

  for (let index = 0; index < count; index += 1) {
    const petal = document.createElement("span");
    const size = 12 + Math.random() * 15;
    const duration = 11 + Math.random() * 12;
    const delay = Math.random() * -22;
    const drift = `${Math.round(Math.random() * 180 - 90)}px`;
    const spin = `${Math.round(180 + Math.random() * 260)}deg`;
    const [from, to] = petalColors[index % petalColors.length];

    petal.className = "falling-petal";
    petal.style.left = `${Math.random() * 100}%`;
    petal.style.width = `${size}px`;
    petal.style.height = `${size * 1.4}px`;
    petal.style.opacity = `${0.22 + Math.random() * 0.56}`;
    petal.style.animationDuration = `${duration}s`;
    petal.style.animationDelay = `${delay}s`;
    petal.style.setProperty("--drift", drift);
    petal.style.setProperty("--spin", spin);
    petal.style.background = `linear-gradient(180deg, ${from} 0%, ${to} 100%)`;

    petalLayer.appendChild(petal);
  }
}

function createSparkles(count = 24) {
  if (!sparkleLayer) return;

  for (let index = 0; index < count; index += 1) {
    const sparkle = document.createElement("span");

    sparkle.className = "sparkle";
    sparkle.style.left = `${Math.random() * 100}%`;
    sparkle.style.top = `${Math.random() * 100}%`;
    sparkle.style.animationDelay = `${Math.random() * -6}s`;
    sparkle.style.animationDuration = `${3.8 + Math.random() * 3}s`;
    sparkle.style.opacity = `${0.2 + Math.random() * 0.7}`;
    sparkle.style.scale = `${0.8 + Math.random() * 0.8}`;

    sparkleLayer.appendChild(sparkle);
  }
}

function openExperience({ scrollToLetter = false } = {}) {
  body.classList.add("experience-awake", "experience-opened");

  if (!scrollToLetter || !letter) return;

  window.setTimeout(() => {
    letter.scrollIntoView({
      behavior: prefersReducedMotion.matches ? "auto" : "smooth",
      block: "start",
    });
  }, prefersReducedMotion.matches ? 0 : 420);
}

function setupStageControls() {
  openExperienceButton?.addEventListener("click", () => {
    openExperience({ scrollToLetter: true });
  });

  toggleStageButton?.addEventListener("click", () => {
    if (body.classList.contains("experience-opened")) {
      body.classList.remove("experience-opened");
      return;
    }

    openExperience();
  });

  sealButton?.addEventListener("click", () => {
    openExperience({ scrollToLetter: coarsePointer.matches || window.innerWidth <= 720 });
  });
}

function setupLetterToggle() {
  if (!toggleNoteButton || !letterScene) return;

  toggleNoteButton.addEventListener("click", () => {
    const isOpen = letterScene.classList.toggle("open");
    toggleNoteButton.setAttribute("aria-expanded", String(isOpen));
    toggleNoteButton.querySelector("span").textContent = isOpen
      ? "把这封信轻轻合上"
      : "点一下，展开这封信";
  });
}

function setupReveal() {
  revealTargets.forEach((element) => {
    const delay = element.dataset.delay || "0";
    element.style.transitionDelay = `${delay}ms`;
  });

  if (!("IntersectionObserver" in window)) {
    revealTargets.forEach((element) => element.classList.add("revealed"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        entry.target.classList.add("revealed");
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.16,
      rootMargin: "0px 0px -32px 0px",
    }
  );

  revealTargets.forEach((element) => observer.observe(element));
}

function setupPointerParallax() {
  if (prefersReducedMotion.matches || coarsePointer.matches) return;

  let rafId = null;
  let pointerX = window.innerWidth / 2;
  let pointerY = window.innerHeight / 3;

  const render = () => {
    const xPercent = (pointerX / window.innerWidth) * 100;
    const yPercent = (pointerY / window.innerHeight) * 100;
    const tiltY = ((xPercent - 50) / 50) * 5;
    const tiltX = ((yPercent - 35) / 65) * -4;

    root.style.setProperty("--pointer-x", `${xPercent}%`);
    root.style.setProperty("--pointer-y", `${yPercent}%`);
    root.style.setProperty("--tilt-y", `${tiltY}deg`);
    root.style.setProperty("--tilt-x", `${tiltX}deg`);

    rafId = null;
  };

  window.addEventListener("pointermove", (event) => {
    pointerX = event.clientX;
    pointerY = event.clientY;

    if (rafId) return;
    rafId = window.requestAnimationFrame(render);
  });

  window.addEventListener("pointerleave", () => {
    pointerX = window.innerWidth / 2;
    pointerY = window.innerHeight / 3;

    if (rafId) return;
    rafId = window.requestAnimationFrame(render);
  });
}

function initializeExperience() {
  const compactMode = coarsePointer.matches || window.innerWidth <= 720;

  body.classList.add("experience-awake");
  if (compactMode) body.classList.add("touch-optimized", "experience-opened");
  createPetals(compactMode ? 18 : 28);
  createSparkles(compactMode ? 14 : 24);
  setupStageControls();
  setupLetterToggle();
  setupReveal();
  setupPointerParallax();

  if (compactMode) {
    letterScene?.classList.add("open");
    toggleNoteButton?.setAttribute("aria-expanded", "true");

    const label = toggleNoteButton?.querySelector("span");
    if (label) label.textContent = "把这封信轻轻合上";
  }
}

initializeExperience();
