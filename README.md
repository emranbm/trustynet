# safefolks
A network of who we trust

## Core Values
- Trust
- Integrity

## Components

### 🌐 Website
The main SafeFolks website showcasing the project.

### 🤖 Telegram Bot (Not Released)
A Telegram bot (`@safefolks_bot`) that records trust relationships in groups. See [`bot/README.md`](bot/README.md) for details.

## Editing the Site

The site content is now in Markdown format for easier editing:

- **Content**: Edit `index.md` to change the site content
- **Styling**: Modify `_layouts/default.html` to change the design, CSS, or JavaScript
- **Configuration**: Update `_config.yml` for site settings

The site uses Jekyll to convert Markdown to HTML. GitHub Pages will automatically build and deploy the site when changes are pushed to the `main` branch.

## Local Development

To preview the site locally:

```bash
# Install Jekyll (requires Ruby)
gem install jekyll bundler

# Build the site
jekyll build

# Or serve it locally with live reload
jekyll serve
# Visit http://localhost:4000
```
