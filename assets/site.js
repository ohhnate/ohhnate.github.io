// Theme toggle, saved language choice, and the language menu's dismiss behavior.
// The inline script in <head> applies a saved theme before first paint; this file wires up the controls.

const root = document.documentElement;
const toggle = document.querySelector(".theme-toggle");
const themeColor = document.querySelector('meta[name="theme-color"]');
const langMenu = document.querySelector(".lang-menu");

function save(key, value) {
	try {
		localStorage.setItem(key, value);
	} catch {
		// Storage can be blocked (private modes, strict settings); the choice just won't persist.
	}
}

function applyTheme(theme) {
	root.dataset.theme = theme;
	toggle.setAttribute("aria-pressed", theme === "dark");
	themeColor.content = getComputedStyle(root).getPropertyValue("--stage").trim();
}

applyTheme(root.dataset.theme === "dark" ? "dark" : "light");
toggle.hidden = false;
toggle.addEventListener("click", () => {
	const next = root.dataset.theme === "dark" ? "light" : "dark";
	applyTheme(next);
	save("theme", next);
});

document.addEventListener("click", (event) => {
	// An explicit language pick stops the root URL from auto-detecting.
	const langLink = event.target.closest("[data-lang]");
	if (langLink) save("lang", langLink.dataset.lang);
	if (langMenu.open && !langMenu.contains(event.target)) langMenu.open = false;
});

document.addEventListener("keydown", (event) => {
	if (event.key !== "Escape" || !langMenu.open) return;
	langMenu.open = false;
	langMenu.querySelector("summary").focus();
});
