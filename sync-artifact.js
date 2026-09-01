/*
 * index.html is the source of truth (the GitHub Pages portfolio).
 * portfolio.html is the same page reshaped for a Claude Artifact preview,
 * which supplies its own <!doctype>/<html>/<head>/<body> wrapper.
 *
 * Run after editing index.html so the two never drift:
 *   node sync-artifact.js
 */
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const src = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');

const head = src.match(/<title>[\s\S]*?<\/style>/);
const body = src.match(/<body>([\s\S]*?)<\/body>/);

if (!head || !body) {
  console.error('ABORT: could not find the <title>..</style> head block or the <body> block.');
  process.exit(1);
}

const out = head[0] + '\n' + body[1].trim() + '\n';
fs.writeFileSync(path.join(dir, 'portfolio.html'), out, 'utf8');

console.log('portfolio.html regenerated from index.html (' + out.length + ' bytes)');
