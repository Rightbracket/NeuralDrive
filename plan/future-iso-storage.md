# Future ISO Storage: Internet Archive

When ready to distribute NeuralDrive ISOs publicly, use Internet Archive (archive.org)
as the primary download host. Many Linux distros already do this (Ubuntu, Debian, Tails,
Alpine, etc.).

## Why Internet Archive

- Free, permanent hosting with no egress fees
- Automatic torrent/magnet link generation with IA webseed fallback
- ~500GB max per file (our ~4GB ISO is well within limits)
- Software distros are a canonical use case — `mediatype:software` + `collection:opensource`

## Setup

### 1. Create an Internet Archive account

Sign up at https://archive.org/account/signup

### 2. Get S3 API keys

Go to https://archive.org/account/s3.php and note your access key and secret key.

### 3. Add GitHub secrets

In the repo: Settings → Secrets and variables → Actions → New repository secret:
- `IA_ACCESS_KEY` — your IA S3 access key
- `IA_SECRET_KEY` — your IA S3 secret key

### 4. Uncomment the upload step in `.github/workflows/build.yml`

The workflow already has a commented-out upload step. Uncomment it and it will upload
the ISO to Internet Archive on every release tag push (`v*`).

## Upload details

The `ia` CLI (from the `internetarchive` Python package) handles uploads:

```bash
pip install internetarchive

ia upload neuraldrive-v1.0.0 output/neuraldrive-2026.04.iso \
  --metadata="title:NeuralDrive v1.0.0" \
  --metadata="mediatype:software" \
  --metadata="collection:opensource" \
  --metadata="description:NeuralDrive Linux — boot a USB, get an LLM server" \
  --metadata="creator:NeuralDrive Project" \
  --metadata="subject:linux;distro;llm;inference;gpu" \
  --retries 10
```

Auth via environment variables:
```bash
export IA_ACCESS_KEY_ID="your-access-key"
export IA_SECRET_ACCESS_KEY="your-secret-key"
```

## Versioning

Internet Archive has no automatic versioning. Use a separate identifier per release:
- `neuraldrive-v1.0.0`
- `neuraldrive-v1.1.0`
- `neuraldrive-v2.0.0`

Re-uploading a file with the same name to the same identifier clobbers the old version
(backed up to `history/files/` in the item).

## Post-upload

After upload, IA runs a "derive" process that generates checksums and torrent files.
This can take minutes to hours. The item page will be live immediately but torrents
may not appear until derive completes.

Each item gets:
- Direct HTTP download: `https://archive.org/download/neuraldrive-v1.0.0/neuraldrive-2026.04.iso`
- Torrent file: `https://archive.org/download/neuraldrive-v1.0.0/neuraldrive-v1.0.0_archive.torrent`
- Item page: `https://archive.org/details/neuraldrive-v1.0.0`

## Rate limits

- Max ~4 concurrent uploads
- 503 SlowDown errors mean throttling — the `--retries` flag handles this
- ≤5,000 files/day bulk limit (not relevant for single ISO uploads)

## Important metadata fields

| Field | Value | Notes |
|-------|-------|-------|
| `mediatype` | `software` | Cannot be changed after first upload |
| `collection` | `opensource` | Public open-source software collection |
| `title` | `NeuralDrive vX.Y.Z` | Human-readable title |
| `creator` | `NeuralDrive Project` | Author/org |
| `subject` | `linux;distro;llm;inference;gpu` | Semicolon-separated tags |
| `description` | Free-text | Supports basic HTML |
