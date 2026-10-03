/**
 * Sunless Gateway - Scenery Component Disabled
 * Background scenery removed per configuration.
 */
(function () {
  'use strict';
  try {
    const existing = document.getElementById('playground-scenery-backdrop');
    if (existing) existing.remove();
    document.querySelectorAll('.sunless-scenery-backdrop').forEach(el => el.remove());
  } catch (e) {}
})();
