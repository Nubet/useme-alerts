## How to create a release

This project use `bump-my-version` to automatically update the version number, create a git commit, and generate a git tag.

1. **Bump the version**
   - For a small bugfix: `uvx bump-my-version bump patch` (e.g., 0.1.0 -> 0.1.1)
   - For a new feature: `uvx bump-my-version bump minor` (e.g., 0.1.0 -> 0.2.0)
   - For a major change: `uvx bump-my-version bump major` (e.g., 0.1.0 -> 1.0.0)

2. **Push the release to GitHub**
   ```bash
   git push --follow-tags
   ```

## What happens next?

1. GitHub Actions detects the new tag.
2. It builds the new Docker image automatically.
3. It pushes the image to GitHub Container Registry.
4. It creates a new Release page on repository.
