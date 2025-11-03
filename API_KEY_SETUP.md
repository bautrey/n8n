# n8n API Key Setup Required

## Manual Step Required

The n8n REST API requires an API key for authentication. This cannot be automated and must be created manually after the first login.

### Steps to Create API Key

1. **Access n8n UI:**
   ```
   URL: http://localhost:5678
   Username: admin
   Password: n8n_admin_pass_2025
   ```

2. **Navigate to API Settings:**
   - Click Settings (gear icon) in the bottom left
   - Select "n8n API" from the menu

3. **Create API Key:**
   - Click "Create an API key"
   - Set a label (e.g., "Claude Code Development")
   - Set expiration (recommend "Never" for development)
   - Click "Create"

4. **Copy and Save API Key:**
   - Copy the generated API key
   - Open `.env` file in this project
   - Replace `N8N_API_KEY=your_api_key_here` with your actual key
   - Save the file

5. **Verify API Access:**
   ```bash
   # Test API access
   curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
     http://localhost:5678/api/v1/workflows
   ```

   You should see a JSON response listing workflows (empty array if no workflows yet).

## Security Notes

- The API key is stored in `.env` which is gitignored
- Never commit the API key to version control
- The key grants full access to your n8n instance
- For production, use scoped keys (enterprise feature) or rotate keys regularly

## After Setup

Once the API key is configured, you can:
- Use curl commands directly for workflow management
- Use Python helper functions in `lib/n8n_api.py`
- Have Claude Code programmatically manage workflows

See `workflows/README.md` for complete API usage documentation.
