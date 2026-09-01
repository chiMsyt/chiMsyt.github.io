# chimsyt.github.io

Personal portfolio — Timothy Ting. Virtual assistant work: admin, operations
and workflow automation.

`index.html` is the whole site. No build step, no dependencies. Edit it directly.

`.nojekyll` tells GitHub Pages to serve the files as-is rather than running them
through Jekyll.

## Keeping the preview copy in sync

`sync-artifact.js` regenerates a wrapper-less copy of the page for previewing
elsewhere. Run it after editing `index.html`:

```
node sync-artifact.js
```

The generated file is gitignored.
