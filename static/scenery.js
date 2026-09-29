/**
 * Sunless Gateway - Scenery Component & Motion Controller
 * Japanese fantasy landscape (shrine pagoda on hill, curved bridge, serene cranes, glowing lanterns)
 * Smoothly pops up after preloader; smoothly drops below when active chat messages appear.
 */

(function () {
  'use strict';

  const SCENERY_SVG_MARKUP = `
<svg class="sunless-scenery-svg" viewBox="0 0 1600 620" preserveAspectRatio="xMidYBottom meet" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Sky & Twilight Atmosphere Glow -->
    <radialGradient id="twilightGlow" cx="60%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#3d1d36" stop-opacity="0.5" />
      <stop offset="50%" stop-color="#241126" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#141414" stop-opacity="0" />
    </radialGradient>

    <!-- Mountain Silhouettes -->
    <linearGradient id="mountainsGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2c1635" stop-opacity="0.7" />
      <stop offset="100%" stop-color="#150a1a" stop-opacity="0.9" />
    </linearGradient>

    <!-- Pagoda Hill Gradients -->
    <linearGradient id="hillLeftGrad" x1="0" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#381b44" />
      <stop offset="60%" stop-color="#24112e" />
      <stop offset="100%" stop-color="#14091a" />
    </linearGradient>

    <linearGradient id="hillForegroundGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#291232" />
      <stop offset="100%" stop-color="#0f0513" />
    </linearGradient>

    <!-- Serene Water Pond -->
    <linearGradient id="pondGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a0c24" stop-opacity="0.9" />
      <stop offset="40%" stop-color="#14081c" />
      <stop offset="100%" stop-color="#09030c" />
    </linearGradient>

    <!-- Curved Bridge Wood -->
    <linearGradient id="bridgeWoodGrad" x1="0" y1="0" x2="1" y2="0.4">
      <stop offset="0%" stop-color="#732e2e" />
      <stop offset="50%" stop-color="#541f1f" />
      <stop offset="100%" stop-color="#3b1515" />
    </linearGradient>

    <!-- Pagoda Roof Gradient -->
    <linearGradient id="pagodaRoofGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2b4b5e" />
      <stop offset="50%" stop-color="#1c3342" />
      <stop offset="100%" stop-color="#11202b" />
    </linearGradient>

    <!-- Warm Amber Lantern Glow -->
    <radialGradient id="lanternAmberGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fff2a8" stop-opacity="1" />
      <stop offset="35%" stop-color="#ff9e24" stop-opacity="0.8" />
      <stop offset="70%" stop-color="#d95414" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#b83800" stop-opacity="0" />
    </radialGradient>

    <!-- Crane Plumage Gradient -->
    <linearGradient id="craneBodyGrad" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="60%" stop-color="#f0effa" />
      <stop offset="100%" stop-color="#cbcae3" />
    </linearGradient>

    <!-- Petal Soft Rose Gradient -->
    <linearGradient id="petalGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fca5a5" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#f43f5e" stop-opacity="0.6" />
    </linearGradient>

    <!-- Drop Shadow Filter for Bridge & Pagoda -->
    <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- 1. Ambient Background Glow -->
  <rect x="0" y="0" width="1600" height="620" fill="url(#twilightGlow)" />

  <!-- 2. Distant Misty Mountain Ridges -->
  <path d="M 0 360 Q 220 260 480 320 T 960 290 Q 1280 240 1600 350 L 1600 620 L 0 620 Z" fill="url(#mountainsGrad)" opacity="0.65" />
  <path d="M 0 410 Q 320 330 650 380 T 1300 360 Q 1480 340 1600 400 L 1600 620 L 0 620 Z" fill="url(#mountainsGrad)" opacity="0.45" />

  <!-- 3. Tranquil Lake Pond -->
  <rect x="0" y="440" width="1600" height="180" fill="url(#pondGrad)" />

  <!-- Water Surface Glimmer Reflections -->
  <g opacity="0.4">
    <ellipse cx="850" cy="485" rx="280" ry="4" fill="#3b1f48" class="scenery-water-wave" />
    <ellipse cx="680" cy="515" rx="190" ry="3" fill="#2d1738" class="scenery-water-wave" />
    <ellipse cx="1020" cy="535" rx="220" ry="3.5" fill="#341b40" class="scenery-water-wave" />
    <ellipse cx="780" cy="555" rx="140" ry="2.5" fill="#261230" class="scenery-water-wave" />
  </g>

  <!-- 4. Left Slope Hill (Base for the Pagoda Shrine) -->
  <path d="M -50 620 L -50 310 Q 120 200 340 230 Q 560 260 670 440 Q 730 520 800 620 Z" fill="url(#hillLeftGrad)" />
  <!-- Secondary Hill Ridge for Depth -->
  <path d="M -50 620 L -50 420 Q 80 340 260 370 Q 420 400 520 540 Q 560 590 600 620 Z" fill="url(#hillForegroundGrad)" opacity="0.8" />

  <!-- 5. Stone Steps Descending from Pagoda to Lake -->
  <g fill="#452a54" stroke="#1f1026" stroke-width="1.5">
    <polygon points="340,300 395,295 405,307 348,312" />
    <polygon points="352,318 410,312 422,326 362,332" />
    <polygon points="368,338 430,332 443,347 380,354" />
    <polygon points="386,360 452,354 466,370 399,377" />
    <polygon points="408,384 478,377 493,394 422,402" />
    <polygon points="432,410 506,403 522,422 448,430" />
    <polygon points="458,438 536,430 553,450 474,459" />
    <polygon points="486,468 568,460 586,482 503,491" />
  </g>

  <!-- 6. The Japanese Pagoda / Shrine House on the Hill -->
  <g id="scenery-pagoda">
    <!-- Balcony / Foundation Posts -->
    <rect x="225" y="255" width="12" height="45" fill="#2d1316" rx="2" />
    <rect x="270" y="260" width="12" height="42" fill="#2d1316" rx="2" />
    <rect x="315" y="255" width="12" height="45" fill="#2d1316" rx="2" />
    <rect x="355" y="250" width="12" height="48" fill="#2d1316" rx="2" />

    <!-- Verandah Floor Deck -->
    <polygon points="210,255 375,248 385,260 215,267" fill="#692424" />
    <!-- Balcony Red Railing -->
    <line x1="216" y1="244" x2="378" y2="238" stroke="#a83636" stroke-width="3" stroke-linecap="round" />
    <line x1="225" y1="244" x2="225" y2="255" stroke="#a83636" stroke-width="2" />
    <line x1="255" y1="243" x2="255" y2="255" stroke="#a83636" stroke-width="2" />
    <line x1="285" y1="242" x2="285" y2="254" stroke="#a83636" stroke-width="2" />
    <line x1="315" y1="241" x2="315" y2="253" stroke="#a83636" stroke-width="2" />
    <line x1="345" y1="240" x2="345" y2="251" stroke="#a83636" stroke-width="2" />
    <line x1="375" y1="238" x2="375" y2="249" stroke="#a83636" stroke-width="2" />

    <!-- Shrine House Main Body Walls -->
    <polygon points="230,245 365,240 360,185 235,188" fill="#221016" />

    <!-- Shrine Window / Doorway Interior Warm Firelight -->
    <rect x="268" y="195" width="58" height="45" rx="3" fill="#ffb438" opacity="0.9" class="scenery-fire-glow" />
    <!-- Doorway Amber Light Spill Ambient -->
    <ellipse cx="297" cy="225" rx="55" ry="35" fill="url(#lanternAmberGlow)" class="scenery-lantern-glow" />

    <!-- Doorway Lattice Bars (Shōji Style) -->
    <rect x="272" y="198" width="50" height="39" fill="none" stroke="#4a1818" stroke-width="1.8" />
    <line x1="297" y1="198" x2="297" y2="237" stroke="#4a1818" stroke-width="1.5" />
    <line x1="272" y1="211" x2="322" y2="211" stroke="#4a1818" stroke-width="1.2" />
    <line x1="272" y1="224" x2="322" y2="224" stroke="#4a1818" stroke-width="1.2" />

    <!-- Lower Pagoda Roof Tier -->
    <path d="M 180 195 Q 295 160 410 190 Q 425 180 415 168 Q 295 138 175 172 Q 165 185 180 195 Z" fill="url(#pagodaRoofGrad)" />
    <!-- Lower Roof Ridge Eaves Highlight -->
    <path d="M 180 195 Q 295 160 410 190" stroke="#46738f" stroke-width="2.5" fill="none" />

    <!-- Upper Shrine Walls -->
    <polygon points="255,165 340,162 335,125 260,128" fill="#1d0c12" />

    <!-- Upper Pagoda Roof Tier with Flared Tips -->
    <path d="M 215 135 Q 295 105 380 130 Q 395 120 385 108 Q 295 82 210 112 Q 200 125 215 135 Z" fill="url(#pagodaRoofGrad)" />
    <path d="M 215 135 Q 295 105 380 130" stroke="#46738f" stroke-width="2" fill="none" />

    <!-- Roof Peak Finial Spire (Hōju) -->
    <polygon points="295,80 300,105 292,105" fill="#f59e0b" />
    <circle cx="296" cy="77" r="4.5" fill="#fbbf24" />

    <!-- Left Hanging Lantern Under Roof -->
    <line x1="182" y1="190" x2="182" y2="208" stroke="#4a1818" stroke-width="1.5" />
    <!-- Ambient Lantern Halo -->
    <ellipse cx="182" cy="216" rx="30" ry="30" fill="url(#lanternAmberGlow)" class="scenery-lantern-glow" />
    <!-- Lantern Sphere Body -->
    <ellipse cx="182" cy="215" rx="7.5" ry="9" fill="#ff9924" stroke="#8c2f11" stroke-width="1.2" />
    <line x1="182" y1="224" x2="182" y2="232" stroke="#d95414" stroke-width="1.5" />

    <!-- Right Hanging Lantern Under Roof -->
    <line x1="405" y1="185" x2="405" y2="204" stroke="#4a1818" stroke-width="1.5" />
    <ellipse cx="405" cy="212" rx="30" ry="30" fill="url(#lanternAmberGlow)" class="scenery-lantern-glow" />
    <ellipse cx="405" cy="211" rx="7.5" ry="9" fill="#ff9924" stroke="#8c2f11" stroke-width="1.2" />
    <line x1="405" y1="220" x2="405" y2="228" stroke="#d95414" stroke-width="1.5" />
  </g>

  <!-- 7. The Curved Wooden Footbridge (Taiko-bashi) -->
  <g id="scenery-bridge">
    <!-- Bridge Reflection in Pond -->
    <path d="M 640 455 Q 890 530 1150 485 L 1150 500 Q 890 550 640 470 Z" fill="#2d1017" opacity="0.45" />

    <!-- Bridge Support Wooden Piles in Water -->
    <rect x="740" y="415" width="10" height="75" fill="#2c1114" rx="2" />
    <rect x="870" y="380" width="11" height="110" fill="#2c1114" rx="2" />
    <rect x="1000" y="425" width="10" height="65" fill="#2c1114" rx="2" />

    <!-- Bridge Curved Under-Stringer -->
    <path d="M 620 460 Q 870 340 1140 490 L 1140 505 Q 870 355 620 475 Z" fill="#381315" />

    <!-- Bridge Curved Main Deck (Walkway) -->
    <path d="M 610 445 Q 870 325 1150 480 L 1150 495 Q 870 340 610 460 Z" fill="url(#bridgeWoodGrad)" stroke="#22090a" stroke-width="1" />

    <!-- Deck Planks Slats (Segment Lines) -->
    <g stroke="#260b0d" stroke-width="1.8" opacity="0.65">
      <line x1="660" y1="440" x2="660" y2="455" />
      <line x1="710" y1="420" x2="710" y2="436" />
      <line x1="760" y1="400" x2="760" y2="418" />
      <line x1="815" y1="384" x2="815" y2="403" />
      <line x1="870" y1="375" x2="870" y2="395" />
      <line x1="925" y1="384" x2="925" y2="403" />
      <line x1="980" y1="400" x2="980" y2="420" />
      <line x1="1035" y1="423" x2="1035" y2="444" />
      <line x1="1090" y1="450" x2="1090" y2="470" />
    </g>

    <!-- Curved Handrail (Balustrade) -->
    <path d="M 605 405 Q 870 280 1155 440" fill="none" stroke="#8f3232" stroke-width="5" stroke-linecap="round" />
    <path d="M 605 422 Q 870 300 1155 458" fill="none" stroke="#632020" stroke-width="3.5" stroke-linecap="round" />

    <!-- Vertical Balusters with Decorative Caps (Giboshi) -->
    <g stroke="#782727" stroke-width="3" stroke-linecap="round">
      <line x1="640" y1="422" x2="640" y2="448" />
      <line x1="685" y1="398" x2="685" y2="430" />
      <line x1="735" y1="375" x2="735" y2="410" />
      <line x1="785" y1="358" x2="785" y2="395" />
      <line x1="835" y1="345" x2="835" y2="384" />
      <line x1="885" y1="345" x2="885" y2="384" />
      <line x1="935" y1="358" x2="935" y2="396" />
      <line x1="985" y1="378" x2="985" y2="415" />
      <line x1="1040" y1="405" x2="1040" y2="442" />
      <line x1="1100" y1="432" x2="1100" y2="466" />
    </g>

    <!-- Post Finial Caps (Golden Giboshi) -->
    <circle cx="640" cy="420" r="3.5" fill="#f59e0b" />
    <circle cx="735" cy="373" r="3.5" fill="#f59e0b" />
    <circle cx="835" cy="343" r="3.5" fill="#f59e0b" />
    <circle cx="885" cy="343" r="3.5" fill="#f59e0b" />
    <circle cx="985" cy="375" r="3.5" fill="#f59e0b" />
    <circle cx="1100" cy="430" r="3.5" fill="#f59e0b" />
  </g>

  <!-- 8. Right Shore Bank & Rocks -->
  <path d="M 1120 620 L 1120 500 Q 1240 450 1420 480 Q 1550 500 1650 620 Z" fill="url(#hillForegroundGrad)" />
  <path d="M 1250 620 Q 1380 490 1520 530 L 1650 620 Z" fill="#1b0a20" opacity="0.85" />

  <!-- 9. Stone Lantern (Tōrō) on Right Shore -->
  <g id="scenery-stone-lantern">
    <!-- Pedestal Base -->
    <polygon points="1350,560 1410,560 1420,575 1340,575" fill="#2d1838" />
    <rect x="1370" y="525" width="20" height="35" fill="#391e46" rx="2" />
    <!-- Middle Platform -->
    <polygon points="1355,525 1405,525 1415,515 1345,515" fill="#442454" />

    <!-- Light Chamber (Hibukuro) Amber Glow -->
    <ellipse cx="1380" cy="495" rx="38" ry="38" fill="url(#lanternAmberGlow)" class="scenery-stone-lantern-glow" />
    <rect x="1364" y="482" width="32" height="30" rx="3" fill="#ffb438" opacity="0.9" class="scenery-fire-glow" />
    <line x1="1380" y1="482" x2="1380" y2="512" stroke="#31153d" stroke-width="2" />
    <line x1="1364" y1="497" x2="1396" y2="497" stroke="#31153d" stroke-width="2" />

    <!-- Tiered Stone Roof (Kasa) -->
    <path d="M 1340 485 Q 1380 460 1420 485 Q 1430 478 1420 470 Q 1380 450 1340 470 Q 1330 478 1340 485 Z" fill="#3f214e" stroke="#1d0a26" stroke-width="1.2" />
    <!-- Stone Jewel Top (Hōju) -->
    <circle cx="1380" cy="446" r="4.5" fill="#58316c" />
    <polygon points="1376,450 1384,450 1382,458 1378,458" fill="#381b46" />
  </g>

  <!-- 10. Lake Marsh Reeds & Lotus Pads -->
  <!-- Lotus Leaves (Water Lily Pads) -->
  <g fill="#213d2a" stroke="#14261a" stroke-width="1" opacity="0.85">
    <ellipse cx="610" cy="515" rx="22" ry="7" />
    <ellipse cx="645" cy="525" rx="18" ry="6" />
    <ellipse cx="780" cy="540" rx="26" ry="8" />
    <ellipse cx="940" cy="530" rx="20" ry="6.5" />
    <ellipse cx="1060" cy="520" rx="24" ry="7.5" />
  </g>

  <!-- Tall Marsh Cattails & Reeds along Hill Base -->
  <g stroke="#3d2117" stroke-width="2" stroke-linecap="round" fill="none">
    <path d="M 520 540 Q 525 470 515 440" />
    <path d="M 530 545 Q 540 460 535 430" />
    <path d="M 542 550 Q 548 480 558 450" />
    <path d="M 555 555 Q 570 490 565 445" />
    <path d="M 570 560 Q 585 500 580 460" />
    <!-- Reed seedheads -->
    <ellipse cx="515" cy="450" rx="2.5" ry="8" fill="#693b2a" stroke="none" />
    <ellipse cx="535" cy="440" rx="2.5" ry="9" fill="#693b2a" stroke="none" />
    <ellipse cx="565" cy="455" rx="2.5" ry="7" fill="#693b2a" stroke="none" />
  </g>

  <!-- 11. The Two Ethereal White Cranes (Red-Crowned Japanese Cranes) -->
  <!-- Crane 1 (Left foreground standing tall) -->
  <g class="scenery-crane-group" id="crane-1">
    <!-- Water Ripple at Feet -->
    <ellipse cx="660" cy="532" rx="14" ry="3" fill="none" stroke="#7e6096" stroke-width="1" opacity="0.6" />
    <!-- Slender Legs -->
    <line x1="656" y1="485" x2="656" y2="532" stroke="#221124" stroke-width="2" stroke-linecap="round" />
    <line x1="664" y1="485" x2="667" y2="530" stroke="#221124" stroke-width="1.8" stroke-linecap="round" />

    <!-- Plumage & Body -->
    <!-- Tail Shadow Feathers (Black wingtips) -->
    <path d="M 640 472 Q 625 480 620 495 Q 635 490 648 480 Z" fill="#1c0f24" />
    <!-- Main White Feather Body -->
    <path d="M 642 460 Q 640 485 665 485 Q 682 485 678 465 Q 675 448 658 450 Q 645 450 642 460 Z" fill="url(#craneBodyGrad)" />
    <!-- Curved Graceful S-Neck -->
    <path d="M 655 452 Q 652 425 665 410 Q 675 398 676 385 Q 682 398 672 418 Q 662 435 664 455 Z" fill="url(#craneBodyGrad)" />
    <!-- Head & Delicate Beak -->
    <circle cx="678" cy="382" r="5" fill="#ffffff" />
    <!-- Red Crown (Tanchō crest) -->
    <path d="M 676 377 Q 680 376 682 378 Q 680 380 676 379 Z" fill="#e11d48" />
    <!-- Slender Beak -->
    <polygon points="682,381 702,386 682,385" fill="#f59e0b" />
    <!-- Eye dot -->
    <circle cx="680" cy="381" r="0.9" fill="#09030c" />
  </g>

  <!-- Crane 2 (Standing gracefully near center under bridge arch) -->
  <g class="scenery-crane-group-2" id="crane-2">
    <!-- Water Ripple -->
    <ellipse cx="805" cy="515" rx="12" ry="2.5" fill="none" stroke="#7e6096" stroke-width="0.8" opacity="0.5" />
    <!-- Legs -->
    <line x1="802" y1="472" x2="801" y2="515" stroke="#221124" stroke-width="1.8" stroke-linecap="round" />
    <line x1="808" y1="472" x2="812" y2="513" stroke="#221124" stroke-width="1.6" stroke-linecap="round" />

    <!-- Tail feathers -->
    <path d="M 822 460 Q 835 468 838 480 Q 825 476 816 468 Z" fill="#1c0f24" />
    <!-- Body -->
    <path d="M 820 450 Q 822 472 802 472 Q 788 472 790 455 Q 792 440 806 442 Q 818 442 820 450 Z" fill="url(#craneBodyGrad)" />
    <!-- Neck gracefully dipped slightly towards water -->
    <path d="M 808 444 Q 806 422 795 410 Q 786 400 782 392 Q 788 402 798 418 Q 808 430 802 446 Z" fill="url(#craneBodyGrad)" />
    <!-- Head -->
    <circle cx="780" cy="390" r="4.5" fill="#ffffff" />
    <path d="M 781 386 Q 785 385 786 388 Q 783 389 780 388 Z" fill="#e11d48" />
    <polygon points="777,390 760,396 777,393" fill="#f59e0b" />
    <circle cx="779" cy="389" r="0.8" fill="#09030c" />
  </g>

  <!-- 12. Drifting Sakura / Shadow Motes -->
  <g id="scenery-petals">
    <path d="M 320 220 Q 330 215 335 225 Q 328 232 320 220 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-1" />
    <path d="M 460 280 Q 470 274 476 284 Q 468 292 460 280 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-2" />
    <path d="M 680 340 Q 692 332 698 344 Q 689 353 680 340 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-3" />
    <path d="M 850 290 Q 860 285 866 295 Q 858 302 850 290 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-4" />
    <path d="M 1040 370 Q 1052 362 1058 374 Q 1048 382 1040 370 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-5" />
    <path d="M 1240 410 Q 1250 405 1256 414 Q 1248 422 1240 410 Z" fill="url(#petalGrad)" class="scenery-petal scenery-petal-6" />
  </g>
</svg>
`;

  let backdropEl = null;

  function injectScenery() {
    const chatColumn = document.getElementById('playground-chat-column');
    if (!chatColumn) return;

    // Check if already injected
    if (document.getElementById('playground-scenery-backdrop')) return;

    backdropEl = document.createElement('div');
    backdropEl.id = 'playground-scenery-backdrop';
    backdropEl.className = 'sunless-scenery-backdrop';
    backdropEl.setAttribute('aria-hidden', 'true');
    backdropEl.innerHTML = SCENERY_SVG_MARKUP;

    // Insert behind the chat input card and hero, inside the chat column
    chatColumn.appendChild(backdropEl);

    // Initial popup trigger
    triggerSceneryPopup();
  }

  function triggerSceneryPopup() {
    if (!backdropEl) {
      backdropEl = document.getElementById('playground-scenery-backdrop');
    }
    if (!backdropEl) return;

    // Don't pop up if there are active messages in the conversation
    const workspace = document.getElementById('playground-workspace');
    if (workspace && workspace.classList.contains('has-messages')) {
      backdropEl.classList.remove('scenery-popped');
      return;
    }

    // Smooth spring popup
    requestAnimationFrame(() => {
      setTimeout(() => {
        if (backdropEl) backdropEl.classList.add('scenery-popped');
      }, 150);
    });
  }

  function triggerSceneryDropDown() {
    if (!backdropEl) {
      backdropEl = document.getElementById('playground-scenery-backdrop');
    }
    if (backdropEl) {
      backdropEl.classList.remove('scenery-popped');
    }
  }

  // Observe conversation state changes on #playground-workspace
  function observeChatState() {
    const workspace = document.getElementById('playground-workspace');
    if (!workspace) return;

    const observer = new MutationObserver(() => {
      if (workspace.classList.contains('has-messages')) {
        triggerSceneryDropDown();
      } else {
        triggerSceneryPopup();
      }
    });

    observer.observe(workspace, { attributes: true, attributeFilter: ['class'] });

    // Also observe chat history container for child count changes
    const history = document.getElementById('chat-history');
    if (history) {
      const historyObserver = new MutationObserver(() => {
        const thread = history.querySelector('.chat-thread-container');
        const hasMessages = thread && thread.children.length > 0;
        if (hasMessages) {
          triggerSceneryDropDown();
        } else if (!workspace.classList.contains('has-messages')) {
          triggerSceneryPopup();
        }
      });
      historyObserver.observe(history, { childList: true, subtree: true });
    }
  }

  // Hook into preloader exit event
  window.addEventListener('sunless-preloader-exit', () => {
    setTimeout(triggerSceneryPopup, 200);
  });

  window.addEventListener('sunless-preloader-complete', () => {
    triggerSceneryPopup();
  });

  // Global manual controls
  window.showScenery = triggerSceneryPopup;
  window.hideScenery = triggerSceneryDropDown;

  // Initialize once DOM is ready
  function init() {
    injectScenery();
    observeChatState();

    // Check if preloader is already absent or hidden
    const preloader = document.getElementById('sunless-skiper-preloader');
    if (!preloader || preloader.classList.contains('skiper7-hidden')) {
      triggerSceneryPopup();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
