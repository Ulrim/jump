/*!
 * 전남줄넘기협회 — main.js
 * Vanilla JS. No dependencies. Progressive enhancement only.
 */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------- utils */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function on(el, ev, fn, opt) { if (el) el.addEventListener(ev, fn, opt); }

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };

  /* --------------------------------------------------------- theme toggle */
  (function theme() {
    var saved = store.get("jnrsa-theme");
    if (saved === "dark" || saved === "light") document.documentElement.setAttribute("data-theme", saved);

    $$("[data-theme-toggle]").forEach(function (btn) {
      on(btn, "click", function () {
        var root = document.documentElement;
        var current = root.getAttribute("data-theme");
        if (!current) {
          current = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        var next = current === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        store.set("jnrsa-theme", next);
        btn.setAttribute("aria-label", next === "dark" ? "밝은 화면으로 전환" : "어두운 화면으로 전환");
      });
    });
  })();

  /* ------------------------------------------------------- sticky header */
  (function stickyHeader() {
    var header = $(".header");
    if (!header) return;
    var toTop = $(".to-top");
    function onScroll() {
      var y = window.scrollY || window.pageYOffset;
      header.classList.toggle("is-stuck", y > 8);
      if (toTop) toTop.classList.toggle("is-shown", y > 520);
    }
    on(window, "scroll", onScroll, { passive: true });
    onScroll();
    on(toTop, "click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  })();

  /* -------------------------------------------------------- mobile drawer */
  (function drawer() {
    var drawer = $("#gnb-drawer");
    var openBtn = $("[data-drawer-open]");
    if (!drawer || !openBtn) return;
    var panel = $(".drawer__panel", drawer);
    var lastFocus = null;

    function focusables() {
      return $$("a[href], button:not([disabled]), select, input, [tabindex]:not([tabindex='-1'])", panel)
        .filter(function (el) { return el.offsetParent !== null; });
    }
    function open() {
      lastFocus = document.activeElement;
      drawer.classList.add("is-open");
      drawer.removeAttribute("aria-hidden");
      openBtn.setAttribute("aria-expanded", "true");
      document.body.classList.add("is-locked");
      var f = focusables();
      if (f.length) f[0].focus();
    }
    function close() {
      drawer.classList.remove("is-open");
      drawer.setAttribute("aria-hidden", "true");
      openBtn.setAttribute("aria-expanded", "false");
      document.body.classList.remove("is-locked");
      if (lastFocus) lastFocus.focus();
    }
    on(openBtn, "click", open);
    $$("[data-drawer-close]", drawer).forEach(function (b) { on(b, "click", close); });
    on($(".drawer__scrim", drawer), "click", close);
    on(document, "keydown", function (e) {
      if (!drawer.classList.contains("is-open")) return;
      if (e.key === "Escape") { close(); return; }
      if (e.key !== "Tab") return;
      var f = focusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    // Drawer accordions
    $$(".drawer__trigger", drawer).forEach(function (btn) {
      var sub = document.getElementById(btn.getAttribute("aria-controls"));
      if (!sub) return;
      sub.hidden = true;
      on(btn, "click", function () {
        var expanded = btn.getAttribute("aria-expanded") === "true";
        $$(".drawer__trigger", drawer).forEach(function (other) {
          if (other === btn) return;
          other.setAttribute("aria-expanded", "false");
          var s = document.getElementById(other.getAttribute("aria-controls"));
          if (s) s.hidden = true;
        });
        btn.setAttribute("aria-expanded", String(!expanded));
        sub.hidden = expanded;
      });
    });
  })();

  /* ----------------------------------------------------------- hero slider */
  (function hero() {
    var root = $("[data-slider]");
    if (!root) return;
    var slides = $$(".hero__slide", root);
    if (slides.length < 2) return;
    var dots = $$(".hero__dot", root);
    var cur = $("[data-slider-current]", root);
    var total = $("[data-slider-total]", root);
    var playBtn = $("[data-slider-play]", root);
    var index = 0, timer = null, playing = !reduceMotion;
    var DELAY = 6500;

    if (total) total.textContent = String(slides.length).padStart(2, "0");

    function show(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) {
        var active = n === index;
        s.classList.toggle("is-active", active);
        s.setAttribute("aria-hidden", active ? "false" : "true");
        $$("a, button", s).forEach(function (el) {
          if (active) el.removeAttribute("tabindex"); else el.setAttribute("tabindex", "-1");
        });
      });
      dots.forEach(function (d, n) {
        d.classList.toggle("is-active", n === index);
        d.setAttribute("aria-selected", n === index ? "true" : "false");
      });
      if (cur) cur.textContent = String(index + 1).padStart(2, "0");
    }
    function start() { stop(); if (playing) timer = setInterval(function () { show(index + 1); }, DELAY); }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }

    on($("[data-slider-prev]", root), "click", function () { show(index - 1); start(); });
    on($("[data-slider-next]", root), "click", function () { show(index + 1); start(); });
    dots.forEach(function (d, n) { on(d, "click", function () { show(n); start(); }); });
    on(playBtn, "click", function () {
      playing = !playing;
      playBtn.setAttribute("aria-pressed", String(!playing));
      playBtn.setAttribute("aria-label", playing ? "슬라이드 자동재생 정지" : "슬라이드 자동재생 시작");
      $(".icon-play", playBtn).hidden = playing;
      $(".icon-pause", playBtn).hidden = !playing;
      if (playing) start(); else stop();
    });
    on(root, "mouseenter", stop);
    on(root, "mouseleave", start);
    on(root, "focusin", stop);
    on(root, "focusout", start);
    on(document, "visibilitychange", function () { document.hidden ? stop() : start(); });
    on(root, "keydown", function (e) {
      if (e.key === "ArrowLeft") { show(index - 1); start(); }
      if (e.key === "ArrowRight") { show(index + 1); start(); }
    });

    show(0);
    start();
  })();

  /* ------------------------------------------------------------------ tabs */
  (function tabs() {
    $$("[data-tabs]").forEach(function (group) {
      var buttons = $$("[role='tab']", group);
      var panels = $$("[role='tabpanel']", group);
      if (!buttons.length) return;

      function select(i) {
        buttons.forEach(function (b, n) {
          var on_ = n === i;
          b.setAttribute("aria-selected", String(on_));
          b.setAttribute("tabindex", on_ ? "0" : "-1");
        });
        panels.forEach(function (p, n) { p.hidden = n !== i; });
      }
      buttons.forEach(function (b, i) {
        on(b, "click", function () { select(i); });
        on(b, "keydown", function (e) {
          var next = null;
          if (e.key === "ArrowRight") next = (i + 1) % buttons.length;
          if (e.key === "ArrowLeft") next = (i - 1 + buttons.length) % buttons.length;
          if (e.key === "Home") next = 0;
          if (e.key === "End") next = buttons.length - 1;
          if (next === null) return;
          e.preventDefault();
          select(next);
          buttons[next].focus();
        });
      });
      var initial = buttons.findIndex(function (b) { return b.getAttribute("aria-selected") === "true"; });
      select(initial > -1 ? initial : 0);
    });
  })();

  /* ------------------------------------------------------------- accordion */
  (function accordion() {
    $$(".acc__btn").forEach(function (btn) {
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      if (!panel) return;
      if (btn.getAttribute("aria-expanded") !== "true") panel.hidden = true;
      on(btn, "click", function () {
        var expanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", String(!expanded));
        panel.hidden = expanded;
      });
    });
  })();

  /* --------------------------------------------------------- scroll reveal */
  (function reveal() {
    var items = $$("[data-reveal]");
    if (!items.length) return;
    if (!("IntersectionObserver" in window) || reduceMotion) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) { io.observe(el); });
  })();

  /* -------------------------------------------------------- number counter */
  (function counters() {
    var nums = $$("[data-count]");
    if (!nums.length) return;

    function run(el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var decimals = (el.getAttribute("data-decimals") | 0);
      if (isNaN(target)) return;
      if (reduceMotion) { el.textContent = target.toLocaleString("ko-KR", { minimumFractionDigits: decimals }); return; }
      var dur = 1500, t0 = null;
      function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min((ts - t0) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * eased).toLocaleString("ko-KR", {
          minimumFractionDigits: decimals, maximumFractionDigits: decimals
        });
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    if (!("IntersectionObserver" in window)) { nums.forEach(run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        run(entry.target);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { io.observe(el); });
  })();

  /* ------------------------------------------------------- local nav state */
  (function localnav() {
    var list = $(".localnav__list");
    if (!list) return;
    var active = $("[aria-current='true']", list);
    if (active && active.scrollIntoView) {
      active.scrollIntoView({ block: "nearest", inline: "center" });
    }
  })();

  /* ------------------------------------------------------------ family site */
  (function family() {
    $$("[data-family]").forEach(function (sel) {
      on(sel, "change", function () {
        if (!sel.value) return;
        window.open(sel.value, "_blank", "noopener");
        sel.selectedIndex = 0;
      });
    });
  })();

  /* ------------------------------------------------------- demo form guard */
  (function forms() {
    $$("[data-demo-form]").forEach(function (form) {
      on(form, "submit", function (e) {
        e.preventDefault();
        var note = $("[data-form-note]", form);
        var invalid = $$("[required]", form).filter(function (el) {
          return el.type === "checkbox" ? !el.checked : !el.value.trim();
        });
        if (invalid.length) {
          if (note) {
            note.textContent = "필수 항목을 모두 입력해 주세요.";
            note.style.color = "var(--danger)";
          }
          invalid[0].focus();
          return;
        }
        if (note) {
          note.textContent = "데모 페이지입니다. 실제 접수는 협회 사무국(061-000-0000)으로 문의해 주세요.";
          note.style.color = "var(--green-600)";
        }
      });
    });
  })();

  /* ------------------------------------------------------------- footer year */
  (function year() {
    $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  })();
})();
