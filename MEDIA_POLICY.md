\# Media Upload Policy



\## Objective



Define safe and consistent rules for image uploads in the mobile backend.



\## Supported Formats



\- JPEG

\- PNG

\- WebP



\## Allowed MIME Types



\- image/jpeg

\- image/png

\- image/webp



\## File Size



Maximum file size: 5 MB.



Files larger than 5 MB must be rejected.



\## Filename Rules



Original filenames must not be trusted.



The backend will generate safe unique filenames using UUID-based names.



Unsafe characters and path traversal must not be allowed.



\## Validation Strategy



Every uploaded image will be validated using:



1\. File extension

2\. MIME type

3\. Actual image content



Files failing any validation must be rejected.



\## Storage Policy



Media will be separated into:



\- Public media

\- Private media



Private media must not be exposed through unrestricted public URLs.



\## Security



The system must:



\- Require authentication for protected uploads

\- Validate file size

\- Validate MIME type

\- Validate extension

\- Validate actual image content

\- Generate safe filenames

\- Prevent path traversal

\- Avoid trusting client filenames

\- Restrict private media downloads



\## Cleanup



If database creation fails after storing a file, the stored file must be removed.



When a media record is deleted, its associated file should also be cleaned up.



\## Mobile Upload



Mobile clients will use:



`multipart/form-data`



Example:



```text

image=<binary image file>

