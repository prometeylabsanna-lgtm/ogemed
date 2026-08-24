(function () {
  'use strict';

  function setLang(root, lang) {
    root.classList.remove('cms-lang-mode-uk', 'cms-lang-mode-ru');
    root.classList.add('cms-lang-mode-' + lang);
    root.querySelectorAll('[data-cms-lang]').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.getAttribute('data-cms-lang') === lang);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var editor = document.querySelector('.site-content-editor');
    if (!editor) {
      return;
    }
    setLang(editor, 'uk');
    editor.querySelectorAll('[data-cms-lang]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setLang(editor, btn.getAttribute('data-cms-lang') || 'uk');
      });
    });
  });
})();
