/* Laboratoire apprentissage et douleur / Pain and Learning Lab */
(function () {
  'use strict';

  /* ---- Dark mode toggle: overrides the system setting and is remembered ---- */
  var themeBtn = document.querySelector('.theme-btn');
  if (themeBtn) {
    var root = document.documentElement;
    var sysDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
    var isDark = function () { return root.dataset.theme ? root.dataset.theme === 'dark' : !!(sysDark && sysDark.matches); };
    var sync = function () { themeBtn.setAttribute('aria-pressed', isDark() ? 'true' : 'false'); };
    themeBtn.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('pll-theme', next); } catch (e) {}
      sync();
    });
    if (sysDark && sysDark.addEventListener) sysDark.addEventListener('change', sync);
    sync();
  }

  /* ---- Language switch: remember choice and keep the same section ---- */
  document.querySelectorAll('a[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('pll-lang', a.dataset.lang); } catch (e) {}
      if (location.hash) a.href = a.href.split('#')[0] + location.hash;
    });
  });

  /* ---- Mobile menu ---- */
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  /* ---- EEG traces (decorative) ---- */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initEEG(canvas) {
    var ctx = canvas.getContext('2d');
    if (!ctx) return;
    var labels = (canvas.dataset.labels || 'Fz FCz Cz CPz Pz C3 C4 Oz').split(' ');
    var isStatic = reduce || canvas.hasAttribute('data-static');
    var speed = +canvas.dataset.speed || 150;     // px per second
    var period = +canvas.dataset.period || 4.2;  // seconds between stimuli
    var seed = +canvas.dataset.seed || 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

    var freqs = [1.1, 2.6, 5.2, 9.8, 13.5];
    var amps = [1, .75, .4, .22, .08];
    var chans = labels.map(function (l) {
      return {
        label: l,
        comps: freqs.map(function (f, k) {
          return { f: f * (.88 + rnd() * .25), p: rnd() * 6.283, a: amps[k] * (.7 + rnd() * .6) };
        }),
        erp: (l.charAt(0) === 'C' ? 1.15 : .7) * (.8 + rnd() * .4),
        lat: rnd() * .05
      };
    });

    var W = 0, H = 0;
    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var r = canvas.getBoundingClientRect();
      W = r.width; H = r.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function g(x, m, s) { return Math.exp(-((x - m) * (x - m)) / (2 * s * s)); }
    function evoked(dt, c) {
      if (dt < 0 || dt > 1.3) return 0;
      return c.erp * (-1.1 * g(dt, .22 + c.lat, .045) + 1.7 * g(dt, .39 + c.lat, .075) - .35 * g(dt, .66, .11));
    }

    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      var n = chans.length;
      var top = H * .1, bottom = H * .94;
      var lane = (bottom - top) / n;
      var amp = lane * .2;
      var t0 = t - W / speed;

      // stimulus markers
      ctx.save();
      ctx.strokeStyle = 'rgba(244,183,64,.6)';
      ctx.fillStyle = 'rgba(244,183,64,.9)';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 5]);
      for (var s = Math.ceil(t0 / period) * period; s <= t; s += period) {
        var sx = (s - t0) * speed;
        ctx.beginPath(); ctx.moveTo(sx, top - lane * .35); ctx.lineTo(sx, bottom); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(sx - 4, top - lane * .35 - 6); ctx.lineTo(sx + 4, top - lane * .35 - 6); ctx.lineTo(sx, top - lane * .35); ctx.closePath(); ctx.fill();
      }
      ctx.restore();

      // traces
      ctx.lineWidth = 1.15;
      ctx.lineJoin = 'round';
      ctx.font = '600 11px Archivo, Arial, sans-serif';
      ctx.textAlign = 'right';
      for (var i = 0; i < n; i++) {
        var c = chans[i];
        var y0 = top + lane * (i + .5);
        ctx.strokeStyle = 'rgba(95,227,210,.55)';
        ctx.beginPath();
        for (var x = 0; x <= W + 2; x += 2) {
          var tt = t0 + x / speed;
          var v = 0;
          for (var k = 0; k < c.comps.length; k++) {
            var cp = c.comps[k];
            v += cp.a * Math.sin(6.283 * cp.f * tt + cp.p);
          }
          v *= .5;
          v += evoked(tt - Math.floor(tt / period) * period, c) * 2.4;
          var y = y0 - v * amp;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.fillStyle = 'rgba(207,227,234,.45)';
        ctx.fillText(c.label, W - 14, y0 - lane * .28);
      }
    }

    // Static frame places a stimulus at ~70% of the width
    function staticTime() { return 10 * period + (W * .3) / speed; }

    resize();
    if (isStatic) {
      draw(staticTime());
      window.addEventListener('resize', function () { resize(); draw(staticTime()); });
      return;
    }

    var running = true, raf = 0;
    var start = performance.now() / 1000 - staticTime();
    function loop(ms) {
      draw(ms / 1000 - start);
      if (running) raf = requestAnimationFrame(loop);
    }
    function setRunning(on) {
      if (on === running) return;
      running = on;
      if (on) raf = requestAnimationFrame(loop); else cancelAnimationFrame(raf);
    }
    raf = requestAnimationFrame(loop);
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', function () { setRunning(!document.hidden); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        setRunning(entries[0].isIntersecting && !document.hidden);
      }).observe(canvas);
    }
  }

  /* ---- fMRI: MNI152 axial slices (z = 4, 36, 56 mm) with activation + BOLD time courses (decorative) ----
     Slice from the ICBM 2009a nonlinear symmetric template, (c) 1993-2009 Louis Collins,
     McConnell Brain Imaging Centre, Montreal Neurological Institute, McGill University. */
  function initFMRI(canvas) {
    var ctx = canvas.getContext('2d');
    if (!ctx) return;
    var isStatic = reduce || canvas.hasAttribute('data-static');
    var seed = +canvas.dataset.seed || 11;
    function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

    var ON = 10, PERIOD = 26, DT = .1, SPEED = 14;   // block design (s) and scroll speed (px/s)
    // Canonical double-gamma HRF, sampled every DT seconds for 32 s
    function gamma(t, a) { var f = 1; for (var i = 2; i < a; i++) f *= i; return Math.pow(t, a - 1) * Math.exp(-t) / f; }
    var hrf = [];
    for (var t = 0; t < 32; t += DT) hrf.push(gamma(t, 6) - gamma(t, 16) / 6);
    // Steady-state response to the periodic block design, one period long
    var n = Math.round(PERIOD / DT), bold = [], peak = 0;
    for (var i = 0; i < n; i++) {
      var v = 0;
      for (var k = 0; k < hrf.length; k++) {
        var tt = ((i - k) * DT % PERIOD + PERIOD) % PERIOD;
        if (tt < ON) v += hrf[k];
      }
      bold.push(v); if (v > peak) peak = v;
    }
    bold = bold.map(function (v) { return v / peak; });
    function boldAt(t, lag) {
      var x = ((t - lag) / DT % n + n) % n, i0 = Math.floor(x), f = x - i0;
      return bold[i0] * (1 - f) + bold[(i0 + 1) % n] * f;
    }

    // One region per slice; blobs at MNI coordinates (mm) on that slice
    var regions = [
      { label: 'aINS', z: 4, gain: 1, lag: 0, noise: [], blobs: [[36, 16], [-36, 16]], r: 9 },
      { label: 'dACC', z: 36, gain: .85, lag: .6, noise: [], blobs: [[0, 14]], r: 9 },
      { label: 'S1', z: 56, gain: .9, lag: .3, noise: [], blobs: [[48, -38]], r: 8 }
    ];
    // Sprite with the three slices side by side, all cropped to the same extent in MNI millimetres
    var slice = new Image(), sliceReady = false;
    var XMM = [-76, 77], YMM = [-111, 79], TILES = 3;
    slice.onload = function () { sliceReady = true; if (isStatic) draw(staticTime()); };
    slice.src = canvas.dataset.src;
    regions.forEach(function (r) {
      for (var k = 0; k < 4; k++) r.noise.push({ f: .05 + rnd() * .35, p: rnd() * 6.283, a: .05 + rnd() * .06 });
    });
    function signal(r, t) {
      var v = r.gain * boldAt(t, r.lag);
      r.noise.forEach(function (c) { v += c.a * Math.sin(6.283 * c.f * t + c.p); });
      return v;
    }

    var W = 0, H = 0;
    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var r = canvas.getBoundingClientRect();
      W = r.width; H = r.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      var top = H * .08, bottom = H * .96, lane = (bottom - top) / regions.length;
      var tileW = slice.width / TILES || 459, tileH = slice.height || 570;
      var sh = lane * 1.12, sw = sh * tileW / tileH;          // each slice sits at the end of its lane
      var sxc = W - Math.max(sw * .9, W * .06) - 18;           // slice column (centre x)
      var tlRight = sxc - sw / 2 - 14;

      // stimulation blocks (shaded) scrolling with the time courses
      var t0 = t - tlRight / SPEED;
      ctx.fillStyle = 'rgba(244,183,64,.13)';
      for (var s = Math.floor(t0 / PERIOD) * PERIOD; s < t; s += PERIOD) {
        var x0 = (s - t0) * SPEED, x1 = (s + ON - t0) * SPEED;
        ctx.fillRect(Math.max(0, x0), top, Math.min(tlRight, x1) - Math.max(0, x0), bottom - top);
      }

      ctx.font = '600 11px Archivo, Arial, sans-serif';
      regions.forEach(function (r, i) {
        var yc = top + lane * (i + .5), y0 = yc + lane * .22, amp = lane * .42;
        // BOLD time course
        ctx.lineWidth = 1.8; ctx.lineJoin = 'round';
        ctx.strokeStyle = 'rgba(95,227,210,.85)';
        ctx.beginPath();
        for (var x = 0; x <= tlRight; x += 2) {
          var y = y0 - signal(r, t0 + x / SPEED) * amp;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.fillStyle = 'rgba(207,227,234,.8)'; ctx.textAlign = 'right';
        ctx.fillText(r.label, tlRight - 6, yc - lane * .3);
        if (!sliceReady) return;

        // MNI slice for this region, with its activation
        var sx0 = sxc - sw / 2, sy0 = yc - sh / 2;
        var mmx = function (x) { return sx0 + (x - XMM[0]) / (XMM[1] - XMM[0]) * sw; };
        var mmy = function (y) { return sy0 + (YMM[1] - y) / (YMM[1] - YMM[0]) * sh; };
        var pxmm = sw / (XMM[1] - XMM[0]);
        ctx.globalAlpha = .6;
        ctx.drawImage(slice, i * tileW, 0, tileW, tileH, sx0, sy0, sw, sh);
        ctx.globalAlpha = 1;
        var v = Math.max(0, Math.min(1.1, signal(r, t)));
        ctx.globalCompositeOperation = 'lighter';
        r.blobs.forEach(function (b) {
          var bx = mmx(b[0]), by = mmy(b[1]), br = Math.max(3, r.r * pxmm * (.75 + .5 * v));
          var gg = ctx.createRadialGradient(bx, by, 0, bx, by, br);
          gg.addColorStop(0, 'rgba(255,236,120,' + (.95 * v) + ')');
          gg.addColorStop(.45, 'rgba(244,120,40,' + (.75 * v) + ')');
          gg.addColorStop(1, 'rgba(210,40,30,0)');
          ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(bx, by, br, 0, 6.2832); ctx.fill();
        });
        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = 'rgba(207,227,234,.55)'; ctx.textAlign = 'left';
        ctx.fillText('z = ' + r.z, sx0 + sw + 4, sy0 + sh - 4);
        // a thin connector from the time course into the slice
        ctx.strokeStyle = 'rgba(95,227,210,.35)'; ctx.lineWidth = 1; ctx.setLineDash([2, 4]);
        ctx.beginPath(); ctx.moveTo(tlRight + 2, y0 - signal(r, t) * amp); ctx.lineTo(mmx(r.blobs[0][0]), mmy(r.blobs[0][1])); ctx.stroke();
        ctx.setLineDash([]);
      });
    }

    function staticTime() { return 3 * PERIOD + ON + 3; }   // a frame near the response peak
    resize();
    if (isStatic) {
      draw(staticTime());
      window.addEventListener('resize', function () { resize(); draw(staticTime()); });
      return;
    }
    var running = true, raf = 0, start = performance.now() / 1000 - staticTime();
    function loop(ms) { draw(ms / 1000 - start); if (running) raf = requestAnimationFrame(loop); }
    function setRunning(on) {
      if (on === running) return;
      running = on;
      if (on) raf = requestAnimationFrame(loop); else cancelAnimationFrame(raf);
    }
    raf = requestAnimationFrame(loop);
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', function () { setRunning(!document.hidden); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { setRunning(entries[0].isIntersecting && !document.hidden); }).observe(canvas);
    }
  }

  function boot() {
    document.querySelectorAll('canvas.eeg').forEach(initEEG);
    document.querySelectorAll('canvas.fmri').forEach(initFMRI);
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(boot); else boot();
  // Figure carousels: advance every few seconds, pause on hover/focus, never autoplay with reduced motion.
  document.querySelectorAll('.carousel').forEach(function (c) {
    var slides = c.querySelectorAll('.slide'), dots = c.querySelectorAll('.dot');
    if (slides.length < 2) return;
    var i = 0, timer = null, paused = false, DELAY = 6000;
    function show(n) {
      slides[i].hidden = true; dots[i].removeAttribute('aria-current');
      i = (n + slides.length) % slides.length;
      slides[i].hidden = false; slides[i].classList.remove('is-in'); void slides[i].offsetWidth; slides[i].classList.add('is-in');
      dots[i].setAttribute('aria-current', 'true');
      var next = slides[(i + 1) % slides.length].querySelector('img');
      if (next) next.loading = 'eager';
    }
    function start() { if (reduce || paused || timer) return; timer = setInterval(function () { show(i + 1); }, DELAY); }
    function stop() { clearInterval(timer); timer = null; }
    c.querySelector('.prev').addEventListener('click', function () { stop(); show(i - 1); start(); });
    c.querySelector('.next').addEventListener('click', function () { stop(); show(i + 1); start(); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { stop(); show(k); start(); }); });
    c.addEventListener('mouseenter', function () { paused = true; stop(); });
    c.addEventListener('mouseleave', function () { paused = false; start(); });
    // Pause for keyboard users only: a mouse click on an arrow also focuses it, and should not stop autoplay.
    c.addEventListener('focusin', function (e) {
      var kb = true;
      try { kb = e.target.matches(':focus-visible'); } catch (err) {}
      if (kb) { paused = true; stop(); }
    });
    c.addEventListener('focusout', function () { paused = false; start(); });
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
    start();
  });
})();
