# Schema.org GitHub Pages

This repository hosts a GitHub Pages version of schema.org type definitions.

## GitHub Pages Setup

To enable GitHub Pages for this repository:

1. Go to Settings → Pages in your GitHub repository
2. Under "Source", select "GitHub Actions" 
3. The workflow will automatically deploy the `docs` directory to GitHub Pages

## Viewing the Site

Once deployed, the site will be available at:
`https://nlweb-ai.github.io/schemaorg/`

## Current Schema Types

- [Person](https://nlweb-ai.github.io/schemaorg/Person.html) - A person (alive, dead, undead, or fictional)

## Local Development

To test locally:
```bash
cd docs
python -m http.server 8000
```
Then visit http://localhost:8000

## Adding New Schema Types

To add a new schema type:
1. Create an HTML file in the `docs` directory
2. Follow the same structure as `Person.html`
3. Add a link to the new type in `index.html`
4. Commit and push to trigger deployment