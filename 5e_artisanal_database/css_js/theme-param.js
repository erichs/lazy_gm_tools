// ?theme=light | dark | system: show a page in a palette other than the system's.
// Include it right after theme.css; data-default sets the page's own default
// (system when absent):
//   <script src="../../css_js/theme-param.js" data-default="light"></script>
// Exposes the theme in use as window.pageTheme, so links can pass it on.
(function () {
    const me = document.currentScript;
    const asked = new URLSearchParams(location.search).get('theme');
    const theme = ['light', 'dark', 'system'].includes(asked) ? asked : (me.dataset.default || 'system');
    const css = { light: 'light-pin.css', dark: 'dark.css' }[theme];
    if (css) document.write(`<link rel="stylesheet" href="${new URL(css, me.src).href}">`);  // during parsing: no flash
    window.pageTheme = theme;
})();
