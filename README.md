# Google Home CLI

Broadcast messages to your Google Home/Nest speakers from the command line.

## Installation

```bash
pip install google-home-cli
# or from source
pip install -e .
```

## Setup

### 1. Create Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select an existing one
3. Enable the [Google Assistant API](https://console.cloud.google.com/apis/library/embeddedassistant.googleapis.com)
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth client ID**
6. Select **Desktop app** as the application type
7. Download the JSON file

### 2. Initialize and Authenticate

```bash
# Copy your credentials
ghome auth init ~/Downloads/client_secret_XXX.json

# Complete OAuth flow
ghome auth login
```

## Usage

### Single Broadcast

```bash
ghome broadcast "Dinner is ready!"
ghome broadcast "The package has arrived"
```

### Interactive Mode

```bash
ghome broadcast --interactive
> Dinner is ready
Broadcast sent.
> Kids come downstairs
Broadcast sent.
> quit
```

### Check Auth Status

```bash
ghome auth status
```

## Troubleshooting

**"Not authenticated" error:**
Run `ghome auth login` to complete the OAuth flow.

**"Client secret not found" error:**
Run `ghome auth init <path-to-your-client-secret.json>` first.

**Broadcast not reaching devices:**
- Ensure your Google Home devices are on the same Google account
- Check that the Google Assistant API is enabled in your project

## License

MIT
