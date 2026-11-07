# The Quiet Atlas — visual editing guide

The adventure journal keeps its original design. Stories and photographs are now edited in **Pages CMS**, a hosted visual editor connected to this repository. The personal homepage at `/` is unchanged.

- Journal: https://quantum-spacetime.github.io/adventures/
- Editor entrance: https://quantum-spacetime.github.io/adventures/admin/
- Visual editor: https://app.pagescms.org/
- GitHub Pages settings: https://github.com/Quantum-Spacetime/Quantum-Spacetime.github.io/settings/pages

## One-time activation (no code)

1. Sign in to https://app.pagescms.org/ with the GitHub account that can write to this repository.
2. Follow **Install the GitHub App**. Choose the owning account **Quantum-Spacetime**, choose **Only select repositories**, and select **Quantum-Spacetime.github.io**. Review the requested permissions. Do not grant access to unrelated repositories. Organization-owned copies may require an organization administrator.
3. Open **Quantum-Spacetime / Quantum-Spacetime.github.io** and branch **main**. The editor reads the existing `.pages.yml`; do not replace it with a starter configuration.
4. You should see **Journal stories**, **Banner images and photography gallery**, and the media library. If prompted to create a configuration, check that you selected the right repository and branch and that the CMS integration has been merged.
5. In GitHub Pages settings, retain **Deploy from a branch → main → /(root)**. This integration uses GitHub's native Jekyll build; no custom deployment workflow, OAuth server, database, or secret is required. The current repository uses this publishing source.
6. Open an existing sample story. Change a small piece of text, save it, and wait for **pages build and deployment** to finish at https://github.com/Quantum-Spacetime/Quantum-Spacetime.github.io/actions . Refresh the journal. This is the final account-specific activation check.

Only the owner can authorize the Pages CMS installation. Installing it is separate from adding the site's configuration. The signed-in save/upload workflow cannot be certified until that installation is complete.

## Write, edit, publish and delete

- **Create:** open **Journal stories**, use the new-entry control, add title, date, category/place, summary, cover photograph, image description, and story. The story editor has formatting and image controls; no HTML or Markdown editing is needed.
- **Publish:** turn on **Show on the website**, leave **Mark as an example story** off, and save. Save commits content to the selected branch; GitHub Pages rebuilds the site. The date controls sorting, newest first; it does not schedule publication.
- **Edit:** select an existing entry, change its fields or formatted body, and save. Native expandable stories remain on the journal page; this migration does not add separate article URLs.
- **Hide:** turn off **Show on the website** and save. A new story defaults to hidden. Hidden stories do not appear in the built journal, but their source remains public in this public repository. Never put private drafts or private photos here.
- **Delete:** use the entry's delete control. Deletion is a Git commit and can be recovered through Git history. It removes the story after the next deployment; it does not erase repository history or automatically remove its photographs.
- **Replace a cover:** choose/upload another photograph in **Cover photograph**, update its description, and save the story. A new unique filename avoids stale browser caches.
- **Inline photos:** use the image control in the story toolbar. Add a useful description where the editor supports it.
- **Banner/gallery:** open **Banner images and photography gallery**. Replace the main banner or quotation photograph, edit the gallery list, or drag list items to reorder. The first gallery photo retains its large placement. Remove the placeholder notices once you replace the examples.
- **Delete a photo:** first replace/remove every cover, banner, gallery and story reference to it, then delete the file in the media library. There is no automatic reference tracking/garbage collection.

Keep `main` selected for normal publishing. Saving to a different branch does not update the live site. A successful save is not a successful deployment: check the Actions page if changes do not appear. Browser caching can also delay a replacement; prefer new filenames.

## Why Pages CMS

| Option | Authentication and maintenance | Fit here |
| --- | --- | --- |
| Hosted Pages CMS | GitHub sign-in and a repository-scoped GitHub App; hosted service handles credentials | Selected: free/open source, visual story editor and media uploads, no custom authentication backend |
| Decap CMS + GitHub | Visual editing is good, but standard GitHub setup needs an OAuth provider/backend; hosted Decap Turbo is another option whose terms/limits should be checked | More infrastructure or another service configuration to maintain; no advantage for this small journal |
| Self-hosted CMS | Control over hosting, upgrades, database and authentication | Reasonable later if hosted-service dependence becomes unacceptable; unnecessary operational burden now |

Pages CMS is a third-party service you authorize to write repository contents. It is not a password screen hosted by this site, and its field configuration is not a GitHub security boundary. Repository permissions still govern who can change files. Install only on this repository, grant write access only to trusted editors, use GitHub account protection, and revoke the app in GitHub settings if you stop using it. No collaborator invitation or extra app grant is made by this code change.

The `/adventures/admin/` page is only an editor doorway. It contains no token, client secret, custom login handler or publicly writable upload endpoint. There is no access token stored in this site's source, browser storage, or deployment configuration by this integration. Actual login credentials are handled by GitHub and Pages CMS.

## Can GitHub store photos?

Yes. The configured media library uploads JPG/JPEG, PNG, WebP or AVIF into `adventures/images/` and writes public URLs under `/adventures/images/`. Random upload names reduce accidental overwrites. The journal ships no new third-party photo account requirement. Existing Unsplash demonstration images are preserved until you replace them.

For a modest journal, this is the easiest one-editor workflow. Export web-sized copies before uploading: a practical target is 1,600–2,400 pixels on the long edge, roughly 200–500 KB where quality allows. These are recommendations, not enforced upload limits. Keep original files backed up elsewhere. Remove location/EXIF metadata before publishing if you do not want it public; this integration does not strip metadata.

| Storage | Published limits checked 7 November 2026 | Trade-off |
| --- | --- | --- |
| GitHub Pages | Source repository recommended ≤1 GB; published site ≤1 GB; soft bandwidth limit 100 GB/month. Regular Git warns above 50 MiB and blocks above 100 MiB per file. CMS/API upload limits may be lower. | Simplest built-in upload flow; no automatic image optimization; binary replacements accumulate in Git history. Git LFS is not supported for Pages sites. |
| Cloudinary Free | 25 monthly credits shared across storage, delivery and transformations; not 25 GB of each resource | Strong image optimization/CDN and media dashboard; another account and quota model |
| ImageKit Forever Free | 3 GB media storage and 20 GB monthly bandwidth | Useful optimization/CDN and media library; another account and quota |

At 300 KB each, 1,000 photos are about 300 MB before history and other assets. Repeatedly replacing photos can make the repository much larger even after deleting current files.

**Recommendation:** start with compressed GitHub-hosted photographs. Move to an image CDN when the library or traffic warrants it. Cloudinary/ImageKit are evaluated alternatives, not integrated upload destinations in this implementation. Their dashboards can provide public delivery URLs, but a seamless authenticated external picker/uploader would need a separate integration. Never put their API secrets into this static site or enable unrestricted anonymous uploads just to avoid authentication.

## Maintenance and verification

- `.pages.yml`: visual editor schema and allowed media folder.
- `_stories/*.md`: per-story metadata plus an HTML body produced by the visual editor. The `.md` extension is an implementation detail; editors do not edit Markdown.
- `_data/adventures.json`: banner photographs, notes and gallery list.
- `adventures/index.html`: original design with Jekyll content loops. No JavaScript content-fetching dependency.
- `_config.yml`: non-output story collection. Jekyll includes published content in the journal and does not emit story source files.

For maintainers: use Ruby 3.x, run `bundle install`, then `python3 scripts/verify.py`. The integration check uses isolated builds to exercise create/edit/delete, hidden stories, ordering, photo replacement, gallery changes, escaping and empty state, and checks that the built root homepage is byte-identical. `bundle exec jekyll build --strict_front_matter` performs a normal build. Account authorization and actual CMS uploads require the one-time activation above.

Rollback: revert the CMS integration commit/merge in GitHub. Story/photo edits remain recoverable through repository history. If removing the CMS entirely, revoke its GitHub App access separately; reverting files does not revoke permissions.

## Official references

- Pages CMS setup: https://pagescms.org/docs/quick-start/
- Configuration: https://pagescms.org/docs/configuration/
- Media paths: https://pagescms.org/docs/configuration/media/
- Visual HTML editor: https://pagescms.org/docs/configuration/fields/rich-text/
- Decap GitHub authentication: https://decapcms.org/docs/github-backend/
- Pages publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Git file limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Git LFS limitations: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
- Cloudinary pricing: https://cloudinary.com/pricing
- ImageKit pricing: https://imagekit.io/plans/
