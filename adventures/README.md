# The Quiet Atlas — write in Notion

Articles: https://www.notion.so/f6f3b39feb4f4ca381da9698717358ca

Website: https://quantum-spacetime.github.io/adventures/

## One-time activation (owner only)

1. Visit https://www.notion.so/profile/integrations and create an **internal integration** named **Quiet Atlas Publisher** in the workspace containing the Articles database. Grant **Read content** only; no insert/update or user information permission is needed. Copy the internal integration secret privately.
2. Open the Articles database above. Use **••• → Connections → Add connection** and select **Quiet Atlas Publisher**. If the integration setup has an **Access** tab instead, add this database there. The database must be accessible to the integration, not just to ChatGPT's separate Notion connector. Do not publish the database to the web.
3. Open https://github.com/Quantum-Spacetime/Quantum-Spacetime.github.io/settings/secrets/actions . Choose **New repository secret**, name it exactly `NOTION_TOKEN`, paste the integration secret as its value, and save. Never put it in a file, article, chat, repository variable, or browser JavaScript.
4. Open https://github.com/Quantum-Spacetime/Quantum-Spacetime.github.io/settings/pages . Under **Build and deployment → Source**, select **GitHub Actions**. The workflow deploys the whole existing Jekyll site and preserves `/` as well as `/adventures/`.
5. Open https://github.com/Quantum-Spacetime/Quantum-Spacetime.github.io/actions/workflows/notion-publish.yml and select **Run workflow → main → Run workflow**. Expect a successful **Export published articles**, build, link check and deployment. No separate GitHub personal access token is required. If repository rules prohibit the bot from committing to main, permit this publisher through the repository's approved process; a rejected push deliberately prevents deployment.
6. For the final end-to-end check, duplicate the starter draft, write a short real article, upload a cover and inline photograph, choose a unique slug, and set Status to **published**. Run the workflow and open `/adventures/journal/your-slug/`. Verify both images. Return it to draft if you do not want to retain it. Previously published data remains in Git history.

## Everyday writing — no code

Click **New** in the Articles database or duplicate the starter draft. Write the **body inside the page**, below its properties; there is deliberately no cramped Body property. Use normal Notion formatting and drag/upload photographs into the body. Add captions for image descriptions. Fill Title, Summary, Date, Location and Category. Upload a photo to the **Cover** files property (first file wins), or use the native page cover as a fallback.

Choose a unique lowercase slug with hyphens (`a-walk-in-the-alps`). If blank, the publisher derives one from the title; explicitly setting it prevents title edits from changing the URL. Keep it stable after publishing. Renaming it changes the URL without creating a redirect.

Set Status to **draft** (or leave it empty) to keep a new article private in Notion. Set **published** to publish. Date is required for published posts, controls newest-first ordering, and does not schedule publication. The workflow checks hourly, with possible GitHub scheduling delays. Use **Run workflow** for an immediate check. Deleting, archiving or returning a published page to draft removes its current article and listing on the next successful sync. Already published content and images remain in public Git history; draft status cannot undo prior disclosure.

Supported body blocks: paragraphs, headings, bold/italic/underline/strike/code, safe links, nested lists, checkboxes, quotes, callouts, toggles, code blocks, columns, tables, dividers, bookmarks and uploaded images. Unsupported blocks stop the export with their block type; convert them to supported text/images. Videos, attachments, equations, synced blocks and child pages are not exported. External image URLs must be public HTTPS; uploading directly to Notion is the reliable path. Failed downloads stop publishing and preserve the previous deployed site. Missing covers receive a neutral field-note panel; runtime broken images show their description.

## Images and privacy

Only images referenced by published entries are downloaded. Photos become metadata-stripped WebP files, at most 2400 pixels on either dimension, quality 84, under `adventures/images/notion/`. Content hashes give stable filenames across expiring Notion signatures. Original signed URLs and Notion API responses are never saved. Files over 25 MB and unsupported formats stop publishing; upload JPEG/PNG/WebP exports for best compatibility. Keep original photographs backed up elsewhere.

Old optimized images stay in Git so previous published references remain durable. They are not automatically deleted when a post is removed. The public repository and Git history remain public. Review photos and text before setting published.

## Maintenance

The workflow uses only `NOTION_TOKEN`, scoped to the export step. GitHub's built-in token commits generated articles/photos and deploys Pages through its OIDC mechanism. Actions are pinned to commit SHAs. No pull-request workflow receives the Notion token. Permissions are scoped to the publishing job. A complete export is staged before replacing prior generated articles; build and local-link checks must pass before commit and deployment. A concurrent main-branch edit causes push rejection rather than overwriting another edit.

The data source ID is `75d45a99-5c45-4706-8855-e2255b3011b0` (not a secret). The body remains native Notion page blocks. Legacy sample entries and the banner/gallery settings are preserved. Pages CMS is superseded as the article editor; its old configuration remains for historical compatibility and does not sync Notion. Do not edit generated `notion-*` files in Pages CMS.

Validation: `PATH=/opt/homebrew/opt/ruby/bin:$PATH python3 scripts/notion/verify_build.py` exercises a full isolated fixture build (omit the PATH adjustment on other platforms). `python3 -m unittest discover -s tests -v`; `bundle exec jekyll build --strict_front_matter`; `python3 scripts/notion/check_site.py _site`. Install `requirements-notion.txt` for the exporter/tests and the Gemfile for local Jekyll builds. Live Notion authorization and uploads require activation above; fixture tests are not evidence of live sync.

Rollback: revert this integration commit and restore Pages source to **Deploy from a branch → main → /(root)**. Remove `NOTION_TOKEN` and revoke the internal integration separately if stopping the service. Reverting code does not revoke credentials or erase previously public content.

References: [Notion data-source API](https://developers.notion.com/reference/query-a-data-source), [temporary file URLs](https://developers.notion.com/reference/file-object), [GitHub custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
