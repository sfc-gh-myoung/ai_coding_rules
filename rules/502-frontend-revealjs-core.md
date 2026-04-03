# Reveal.js Presentation Framework Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-04-01
**Keywords:** Reveal.js, revealjs, presentation, slides, HTML presentation, slide deck, code highlighting, speaker notes, Markdown slides, fragments, vertical slides, reveal themes, presentation framework, auto-animate
**TokenBudget:** ~4400
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Best practices for building HTML presentations with Reveal.js 6.0.0, covering project setup (npm/ESM), slide markup patterns (horizontal/vertical slides, fragments, Markdown), configuration options, built-in plugin usage (Highlight, Markdown, Notes, Math, Search, Zoom), syntax-highlighted code blocks with step-by-step line highlights, and theming via built-in themes or CSS custom properties.

**When to Load This Rule:**
- Creating or modifying Reveal.js presentations
- Setting up a new Reveal.js project from scratch
- Adding code highlighting, Markdown content, or speaker notes to slides
- Customizing presentation themes or transitions
- Troubleshooting Reveal.js rendering, navigation, or plugin issues

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **420-javascript-core.md** - ESM and modern JavaScript standards (load if writing custom Reveal.js plugins or extensive JS logic)
- **501-frontend-browser-globals-collisions.md** - Relevant when embedding Reveal.js alongside other frontend libraries

### External Documentation

**Official Documentation:**
- [Reveal.js Documentation](https://revealjs.com/) - Official framework documentation
- [Reveal.js GitHub Repository](https://github.com/hakimel/reveal.js) - Source code and releases
- [Reveal.js Installation Guide](https://revealjs.com/installation/) - Setup methods (basic, full, npm)
- [Reveal.js Configuration Options](https://revealjs.com/config/) - Complete configuration reference
- [Reveal.js Plugins](https://revealjs.com/plugins/) - Built-in and custom plugin system
- [Reveal.js Themes](https://revealjs.com/themes/) - Built-in themes and custom theme creation

## Contract

### Inputs and Prerequisites

- Node.js 20+ (for npm-based setup)
- Package manager (npm, pnpm, or yarn)
- Web browser for viewing presentations
- Basic HTML/CSS/JavaScript knowledge
- Reveal.js 6.0.0 (preferred version)

### Mandatory

- **[Version]** Reveal.js 6.0.0 MUST be the preferred version; older versions (4.x, 5.x) MUST NOT be used for new projects
- **[ESM]** Use ES module imports when installing via npm: `import Reveal from 'reveal.js'`
- **[Markup]** Follow `.reveal > .slides > section` hierarchy for all slide content
- **[Plugins]** Register plugins via the `plugins` array in `Reveal.initialize()`, NOT via the deprecated `dependencies` array
- **[Code]** Use `data-trim` on all `<code>` elements to strip whitespace; specify language class (`language-python`, `language-sql`) explicitly
- **[Themes]** Include exactly one theme stylesheet; use CSS custom properties for overrides instead of modifying theme source files

### Forbidden

- Reveal.js versions older than 6.0.0 for new projects
- The deprecated `dependencies` array for plugin loading (removed in Reveal.js 4.0.0+)
- Mutating Reveal.js source files directly; use configuration, CSS overrides, or plugins instead
- Inline `<style>` blocks that override `.reveal` selectors without scoping (use `data-state` classes or custom theme files)
- Using `eval()` or dynamically constructing slide HTML from untrusted input

### Execution Steps

1. **Install Reveal.js 6.0.0:** Run `npm install reveal.js@6.0.0` or clone the repository and check out the v6.0.0 tag
2. **Create HTML boilerplate:** Set up `index.html` with required CSS imports (`reveal.css` + one theme), the `.reveal > .slides` container, and the Reveal.js script
3. **Configure initialization:** Call `Reveal.initialize()` with desired options (controls, progress, transition, hash, etc.)
4. **Register plugins:** Import and register only the plugins you need (Highlight, Markdown, Notes, Math, Search, Zoom)
5. **Add slide content:** Create `<section>` elements for horizontal slides; nest `<section>` within `<section>` for vertical slides
6. **Add code blocks:** Use `<pre><code>` with `data-trim`, `data-line-numbers`, and language classes for syntax highlighting
7. **Apply theming:** Choose a built-in theme or create a custom theme using CSS custom properties on `:root`
8. **Test presentation:** Open in browser, verify navigation (arrow keys, space), speaker notes (press `S`), and PDF export

### Output Format

An HTML file (typically `index.html`) containing:
- DOCTYPE declaration and `<html>` element
- `<head>` with Reveal.js CSS and theme stylesheet
- `<body>` with `.reveal > .slides > section` structure
- `<script>` tags importing Reveal.js and plugins with `Reveal.initialize()` call

**NPM/ESM project alternative:**
- `package.json` with `reveal.js@6.0.0` dependency and `"type": "module"`
- JavaScript entry point importing Reveal and plugins via ESM

### Validation

**Pre-Task-Completion Checks:**
- Reveal.js version is 6.0.0 (check `package.json` or CDN URL)
- `.reveal > .slides > section` hierarchy is correct in HTML
- No deprecated `dependencies` array in initialization
- All `<code>` blocks have `data-trim` attribute
- Exactly one theme stylesheet is loaded
- All registered plugins are imported before initialization

**Success Criteria:**
- Presentation loads without console errors
- Arrow key navigation works for all slides (horizontal and vertical)
- Code blocks render with syntax highlighting and line numbers (if specified)
- Speaker notes view opens with `S` key
- Fragments animate in correct order
- PDF export produces readable output (print to PDF or `?print-pdf` query parameter)

**Negative Tests:**
- Missing `.reveal` wrapper causes slides to not render
- Registering a plugin without importing its script causes `ReferenceError`
- Using `dependencies` array with Reveal.js 6.0.0 logs a deprecation warning or fails silently
- Missing `data-trim` causes unwanted whitespace in code blocks

### Design Principles

- **Version Pinning:** Always target Reveal.js 6.0.0 to ensure consistent behavior and access to latest features
- **Progressive Enhancement:** Start with minimal configuration; add plugins and features as needed
- **Separation of Concerns:** Keep slide content in HTML/Markdown, styling in CSS themes, and behavior in initialization config
- **Accessibility:** Use semantic HTML within slides; provide text alternatives for visual content
- **Performance:** Load only required plugins; use `data-src` for lazy-loading iframes and media

### Post-Execution Checklist

- [ ] Reveal.js version is 6.0.0 (not an older release)
- [ ] HTML follows `.reveal > .slides > section` hierarchy
- [ ] Plugins registered via `plugins` array (not deprecated `dependencies`)
- [ ] Code blocks use `data-trim` and explicit language classes
- [ ] One theme stylesheet loaded (not multiple conflicting themes)
- [ ] Speaker notes work (press `S`)
- [ ] Navigation works (arrows, space, overview with `O`)
- [ ] No console errors on presentation load

## Project Setup

### NPM Installation (Recommended)

```bash
npm install reveal.js@6.0.0
```

### ESM Entry Point

```javascript
import Reveal from 'reveal.js';
import Markdown from 'reveal.js/plugin/markdown';
import Highlight from 'reveal.js/plugin/highlight';
import Notes from 'reveal.js/plugin/notes';

import 'reveal.js/dist/reveal.css';
import 'reveal.js/dist/theme/black.css';

const deck = new Reveal({
  plugins: [Markdown, Highlight, Notes],
  hash: true,
  transition: 'slide',
});
deck.initialize();
```

### Standalone HTML Boilerplate

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="dist/reveal.css" />
    <link rel="stylesheet" href="dist/theme/white.css" />
    <link rel="stylesheet" href="dist/plugin/highlight/monokai.css" />
  </head>
  <body>
    <div class="reveal">
      <div class="slides">
        <section>Slide 1</section>
        <section>Slide 2</section>
      </div>
    </div>
    <script src="dist/reveal.js"></script>
    <script src="dist/plugin/markdown.js"></script>
    <script src="dist/plugin/highlight.js"></script>
    <script src="dist/plugin/notes.js"></script>
    <script>
      Reveal.initialize({
        plugins: [RevealMarkdown, RevealHighlight, RevealNotes],
        hash: true,
      });
    </script>
  </body>
</html>
```

## Slide Markup Patterns

### Horizontal and Vertical Slides

```html
<div class="reveal">
  <div class="slides">
    <section>Horizontal Slide 1</section>
    <section>
      <section>Vertical Slide 1 (root)</section>
      <section>Vertical Slide 2</section>
      <section>Vertical Slide 3</section>
    </section>
    <section>Horizontal Slide 3</section>
  </div>
</div>
```

Vertical slides are nested `<section>` elements inside a parent `<section>`. The first child is the root and appears in the horizontal sequence.

### Fragments

```html
<section>
  <p class="fragment">Appears first</p>
  <p class="fragment">Appears second</p>
  <p class="fragment fade-up">Fades up third</p>
</section>
```

Available fragment animations: `fade-in` (default), `fade-out`, `fade-up`, `fade-down`, `fade-left`, `fade-right`, `fade-in-then-out`, `fade-in-then-semi-out`, `grow`, `shrink`, `strike`, `highlight-red`, `highlight-green`, `highlight-blue`, `highlight-current-red`, `highlight-current-green`, `highlight-current-blue`.

Control fragment order with `data-fragment-index`:

```html
<p class="fragment" data-fragment-index="2">Second</p>
<p class="fragment" data-fragment-index="1">First</p>
```

### Markdown Slides

```html
<section data-markdown>
  <textarea data-template>
    ## Slide Title
    A paragraph with **bold** and a [link](https://example.com).
    ---
    ## Next Slide
    - Bullet one
    - Bullet two
  </textarea>
</section>
```

Markdown slides require the Markdown plugin. Use `---` (newline-bounded horizontal rule) to separate horizontal slides. Use `data-separator-vertical` for vertical slide separators.

### External Markdown

```html
<section
  data-markdown="slides.md"
  data-separator="^\n\n\n"
  data-separator-vertical="^\n\n"
  data-separator-notes="^Note:"
></section>
```

External Markdown requires a local web server (use `npm start` from the Reveal.js full setup).

### Slide States and Backgrounds

```html
<section data-state="dim-background" data-background-color="#1a1a2e">
  <h2>Custom Background</h2>
</section>

<section data-background-image="image.jpg" data-background-size="cover">
  <h2>Image Background</h2>
</section>
```

### Auto-Animate

```html
<section data-auto-animate>
  <h1>Step 1</h1>
</section>
<section data-auto-animate>
  <h1 style="color: red;">Step 1</h1>
  <p>New content appears</p>
</section>
```

Elements with matching content or `data-id` attributes animate between slides automatically.

## Configuration Reference

### Recommended Defaults

```javascript
Reveal.initialize({
  controls: true,
  progress: true,
  center: true,
  hash: true,
  transition: 'slide',
  slideNumber: 'c/t',
  plugins: [RevealHighlight, RevealMarkdown, RevealNotes],
});
```

### Key Configuration Options

- **`hash: true`** - Enables URL-based slide navigation (bookmarkable slide positions)
- **`history: true`** - Pushes slide changes to browser history (implies `hash: true`)
- **`transition`** - Slide transition style: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`
- **`slideNumber`** - Display format: `true`, `'h.v'`, `'h/v'`, `'c'`, `'c/t'`
- **`autoSlide`** - Auto-advance interval in milliseconds (`0` = disabled)
- **`center: true`** - Vertically center slide content
- **`controls: true`** - Show navigation arrows
- **`loop: false`** - Loop the presentation back to the first slide

### Runtime Reconfiguration

```javascript
Reveal.configure({ autoSlide: 5000 });
Reveal.configure({ transition: 'fade' });
```

## Plugin System

### Built-in Plugins

- **RevealHighlight** - Syntax highlighting for code blocks (powered by highlight.js)
- **RevealMarkdown** - Write slides in Markdown using `data-markdown` attribute
- **RevealNotes** - Speaker notes view (press `S` to open)
- **RevealMath** - Render LaTeX equations via MathJax or KaTeX
- **RevealSearch** - Search slide content (Ctrl+Shift+F)
- **RevealZoom** - Alt+click to zoom into elements

### Plugin Registration (ESM)

```javascript
import Reveal from 'reveal.js';
import Highlight from 'reveal.js/plugin/highlight';
import Markdown from 'reveal.js/plugin/markdown';
import Notes from 'reveal.js/plugin/notes';
import Math from 'reveal.js/plugin/math';

const deck = new Reveal({
  plugins: [Highlight, Markdown, Notes, Math],
});
deck.initialize();
```

### Plugin API

```javascript
Reveal.hasPlugin('highlight');
Reveal.getPlugin('highlight');
Reveal.getPlugins();
```

## Code Highlighting

### Basic Syntax Highlighting

```html
<section>
  <pre><code data-trim class="language-python">
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
  </code></pre>
</section>
```

Always include:
- `data-trim` to remove surrounding whitespace
- Explicit `class="language-*"` for reliable detection (do not rely on auto-detection)

### Line Numbers and Highlights

```html
<pre><code data-trim data-line-numbers="3,8-10" class="language-sql">
SELECT
    customer_id,
    customer_name,
    order_date,
    total_amount
FROM orders
WHERE order_date >= '2026-01-01'
  AND total_amount > 100
  AND status = 'completed'
ORDER BY total_amount DESC;
</code></pre>
```

### Step-by-Step Line Highlights

Use `|` to separate highlight steps:

```html
<pre><code data-trim data-line-numbers="1-2|4-6|8-10" class="language-javascript">
const apiUrl = 'https://api.example.com';
const headers = { 'Content-Type': 'application/json' };

const response = await fetch(apiUrl, {
  method: 'POST',
  headers,
});

const data = await response.json();
console.log(data);
</code></pre>
```

### Line Number Offset

Start line numbers from a specific value:

```html
<pre><code data-trim data-line-numbers data-ln-start-from="42" class="language-python">
def process_record(record):
    validated = validate(record)
    return transform(validated)
</code></pre>
```

### HTML Entity Escaping

Wrap code containing `<` and `>` in `<script type="text/template">` to avoid manual escaping:

```html
<pre><code data-trim class="language-html"><script type="text/template">
<div class="container">
  <p>HTML content with <strong>tags</strong></p>
</div>
</script></code></pre>
```

## Theming

### Built-in Themes

Available themes: `black` (default), `white`, `league`, `beige`, `night`, `serif`, `simple`, `solarized`, `moon`, `dracula`, `sky`, `blood`.

Apply a theme by including its stylesheet:

```html
<link rel="stylesheet" href="dist/theme/dracula.css" />
```

### CSS Custom Property Overrides

All themes expose CSS custom properties. Override them without modifying source files:

```css
:root {
  --r-main-font: 'Inter', sans-serif;
  --r-heading-font: 'Inter', sans-serif;
  --r-main-font-size: 38px;
  --r-main-color: #333;
  --r-heading-color: #1a1a2e;
  --r-link-color: #2563eb;
  --r-link-color-hover: #1d4ed8;
  --r-background-color: #ffffff;
  --r-code-font: 'Fira Code', monospace;
}
```

### Highlight.js Theme for Code

Include a highlight.js theme stylesheet for code block styling:

```html
<link rel="stylesheet" href="dist/plugin/highlight/monokai.css" />
```

Available themes at [highlightjs.org/demo](https://highlightjs.org/demo/).

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using the deprecated `dependencies` array**

```javascript
Reveal.initialize({
  dependencies: [
    { src: 'plugin/markdown.js' },
    { src: 'plugin/highlight.js', async: true },
  ],
});
```

**Problem:** The `dependencies` array was deprecated in Reveal.js 4.0.0. It may fail silently or produce unexpected behavior in 6.0.0.

**Correct Pattern:**
```javascript
Reveal.initialize({
  plugins: [RevealMarkdown, RevealHighlight],
});
```

**Anti-Pattern 2: Missing `data-trim` on code blocks**

```html
<pre><code>
    def hello():
        print("world")
</code></pre>
```

**Problem:** Without `data-trim`, the leading/trailing whitespace and indentation from the HTML source is preserved in the rendered code, causing misaligned output.

**Correct Pattern:**
```html
<pre><code data-trim class="language-python">
def hello():
    print("world")
</code></pre>
```

**Anti-Pattern 3: Loading multiple theme stylesheets**

```html
<link rel="stylesheet" href="dist/theme/black.css" />
<link rel="stylesheet" href="dist/theme/white.css" />
```

**Problem:** Themes define conflicting CSS custom properties and base styles. The last loaded theme wins but may produce visual inconsistencies with partial overrides from earlier themes.

**Correct Pattern:** Load exactly one theme stylesheet and use CSS custom property overrides for customization.

**Anti-Pattern 4: Relying on auto-detection for code language**

```html
<pre><code data-trim>
SELECT * FROM users WHERE id = 1;
</code></pre>
```

**Problem:** highlight.js auto-detection can misidentify the language, producing incorrect highlighting. SQL is frequently confused with other languages.

**Correct Pattern:**
```html
<pre><code data-trim class="language-sql">
SELECT * FROM users WHERE id = 1;
</code></pre>
```

**Anti-Pattern 5: Breaking the `.reveal > .slides > section` hierarchy**

```html
<div class="reveal">
  <div class="slides">
    <div>Slide 1</div>
    <section>Slide 2</section>
  </div>
</div>
```

**Problem:** Non-`<section>` elements inside `.slides` are ignored by Reveal.js. Content inside `<div>` will not be navigable as a slide.

**Correct Pattern:** Every slide must be a `<section>` element directly inside `.slides`.
