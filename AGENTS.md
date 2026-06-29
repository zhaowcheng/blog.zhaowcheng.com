# Repository Guidelines

## Project Structure & Module Organization

This repository is a Jekyll blog using the `jekyll-theme-chirpy` theme. Site configuration lives in `_config.yml`; keep global settings, SEO metadata, analytics, and deployment-related values there. Blog posts live under `_posts/`, grouped by topic directories such as `_posts/postgresql/`, `_posts/claude/`, and `_posts/python-tutorial/`. Use dated Markdown filenames like `2025-04-02-postgresql-configuration.md`; draft or placeholder articles currently use `9999-01-01-...`.

Static and supporting assets live in `assets/`: styles in `assets/css/`, images in `assets/img/<topic>/`, and helper code in `assets/code/`. Navigation tabs are in `_tabs/`, data files in `_data/`, includes in `_includes/`, and custom Jekyll hooks in `_plugins/`. `_site/` is generated output and should not be edited by hand.

## Build, Test, and Development Commands

Enter the development shell with:

```sh
nix develop
```

The shell installs Ruby dependencies into `.gem/` via Bundler. To run the local site with live reload:

```sh
bash tools/run.sh
```

Use `bash tools/run.sh -p` to serve with `JEKYLL_ENV=production`, or `-H 0.0.0.0` when binding outside localhost. Build and validate the site with:

```sh
bash tools/test.sh
```

This removes `_site/`, runs a production Jekyll build, then runs `htmlproofer` with external links disabled.

## Coding Style & Naming Conventions

Follow `.editorconfig`: UTF-8, LF line endings, final newline, two-space indentation, and trimmed trailing whitespace except in Markdown. Use single quotes in CSS/SCSS/JS and double quotes in YAML. Markdown posts should include Chirpy front matter with `title`, `date`, `categories`, and `tags`. Keep category names consistent with existing topic folders.

## Testing Guidelines

There is no separate unit test suite. Treat `bash tools/test.sh` as the required validation before publishing or opening a pull request. For content changes, check that internal anchors, image paths, and generated pages pass `htmlproofer`.

## Commit & Pull Request Guidelines

Recent commits use short Chinese summaries focused on the changed article, for example `修正《PostgreSQL 配置说明》中的几处错误`. Keep commits concise and content-specific. Pull requests should describe the article or site behavior changed, mention any new assets, and include screenshots when layout, images, or navigation are affected.

## Agent-Specific Instructions

Do not edit generated files in `_site/` directly. Prefer changing source Markdown, config, assets, or helper scripts, then rebuild. Avoid committing local caches such as `.gem/` and `.jekyll-cache/`.
