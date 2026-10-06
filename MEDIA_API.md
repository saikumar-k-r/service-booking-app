\# Media API Documentation



\## Overview



The Media API provides secure image upload, validation, storage, access control, download, and cleanup for mobile applications.



\## Supported Formats



\- JPEG / JPG

\- PNG

\- WEBP



\## File Limits



\- Maximum file size: 5 MB

\- MIME type and extension are validated.

\- Invalid or corrupted images are rejected.

\- Filenames are generated safely using UUIDs.



\## Authentication



All media APIs require JWT/Bearer authentication.



Header:



Authorization: Bearer <access\_token>



\## Upload Media



Endpoint:



POST /api/v1/media/upload/



Content-Type:



multipart/form-data



Form fields:



file = image file

visibility = private or public



Example:



file: profile.png

visibility: private



Successful response:



```json

{

&#x20; "id": "media-uuid",

&#x20; "original\_filename": "profile.png",

&#x20; "mime\_type": "image/png",

&#x20; "file\_size": 12345,

&#x20; "visibility": "private",

&#x20; "created\_at": "2026-10-06T00:00:00Z"

}

