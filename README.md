# PWA Builder

**PWA Builder** is a low-code tool for building Progressive Web Apps on top of your Frappe site. Connect a site, drag and drop fields from your DocTypes into app screens with a live phone preview, and publish the generated Frappe app to GitHub in one click.

This is a project by the developers at Aerele Technologies. Feel free to reach out to us via issues.

## Features

- **Dashboard** with a projects gallery, screen templates and a getting-started checklist.
- **Visual builder**: three-pane editor (field palette, canvas, live phone preview) with undo/redo, validation and keyboard shortcuts.
- **Screen templates**: start a screen from required fields, all fields or a blank canvas.
- **Flow**: order screens into the app's navigation with drag and drop.
- **Connections**: build for the current site (no credentials) or connect another Frappe site.
- **One-click publish**: exports your project as a Frappe app and pushes it to your GitHub repository, with a live progress timeline.
- **Desk workspace** for quick navigation to projects, screens and GitHub settings.
- Dark mode, offline indicator and a desk-free UI built with frappe-ui.

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/aerele/pwa-builder.git
bench --site <your-site> install-app pwa_builder
bench build --app pwa_builder
```

Then open `https://<your-site>/pwa-builder` to use the builder, or open the **PWA Builder** workspace in the desk.

## Usage

1. Create a project: build for **this site**, or connect **another site** with its URL and credentials.
2. Add the DocTypes you want to build screens for.
3. Design screens in the builder: drag fields from the palette, tweak them in the inspector, and watch the live phone preview.
4. Arrange the screen order in **Flow**.
5. Set your GitHub username and token in **Settings**, then hit **Publish**. The generated Frappe app is pushed to your repository.
6. Install the generated app on your site and access the PWA at `https://<your-site-name>/<your-pwa-project-name>`.

## Development

```bash
cd apps/pwa_builder/frontend
yarn install
yarn dev        # vite dev server
yarn build      # production build into pwa_builder/public/frontend
```

The frontend is a Vue 3 + frappe-ui SPA served at `/pwa-builder`. Built assets are not tracked in git; run `bench build --app pwa_builder` after pulling.

#### License

MIT
