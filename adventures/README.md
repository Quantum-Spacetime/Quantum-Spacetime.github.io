# The Quiet Atlas — Adventure Journal

A minimalist photography-first adventure journal built using HTML, CSS and a little JavaScript. No subscription, build system, database or hosting charges.

## Visit

When GitHub Pages is enabled and published from the repository root, the journal will appear at:

https://quantum-spacetime.github.io/adventures/

This site is intentionally placed under `/adventures/` so it does not overwrite the existing personal homepage.

## How to publish your first real story

1. Open [adventures/index.html](./index.html) on GitHub and click the pencil-shaped **Edit** button.
2. Locate one of the three `<article class="story">` blocks inside `<div class="story-grid">`.
3. Replace its title in `<h3>`, short summary in the first `<p>`, and story paragraphs inside `<div class="prose">`.
4. Replace the category and `SAMPLE ENTRY` text in the adjacent `story-meta` with your real location and date.
5. Update the `src` URL of that story's `<img>` to your own photo and update its accessible `alt` description.
6. Remove the example-text warning box `<div class="note">` once the story is real.
7. Click **Commit changes**. GitHub Pages will publish the new version once deployment succeeds.

To add a fourth story, copy an existing `<article class="story"> ... </article>` block and paste it before the closing `</div>` of `story-grid`.

## How to add your own photography

Upload JPG or WebP files into `adventures/images/` on GitHub, then use paths such as `images/alps-morning.webp` in image `src` attributes.

The homepage's large background images are configured with `background:url(...)` in `adventures/index.html`, inside the `<style>` block. Replace those URLs as well. The photo gallery also contains three editable `<img>` elements.

Photos currently used in this demo are remote Unsplash images. Their use is illustrative and they are not being represented as your photographs. Remote images require a working connection to Unsplash.

## Design and structure

- Journal name: **The Quiet Atlas**
- Style: contemporary editorial / quiet forest colors / immersive nature photography
- Sections: Hero, introduction, stories, landscape interlude, gallery, about, footer
- Responsive mobile layout and accessible image descriptions
- The expandable sample stories use native HTML `<details>` and require no backend.
- The site is in a single file, `adventures/index.html`, for beginner-friendly editing.

## Enable GitHub Pages (if not already enabled)

Repository → **Settings** → **Pages** → under **Build and deployment** select **Deploy from a branch** → branch **main**, folder **/(root)** → **Save**.

Official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

The account's existing root `index.html` remains unchanged.

## Editing the title or author name

Search for `THE QUIET ATLAS` and `Liam` in `adventures/index.html`. Change the visible labels and the `<title>` and `description` in the page `<head>`.

**Tip:** Keep your original photographs backed up outside GitHub, as your public site and its images can be viewed by anyone.
