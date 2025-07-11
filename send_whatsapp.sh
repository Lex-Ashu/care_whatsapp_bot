#!/bin/bash

curl -i -X POST \
  'https://graph.facebook.com/v22.0/651347521403933/messages' \
  -H 'Authorization: Bearer EAFYi1HZB6eFQBPBIGeuwarpTvf1zzkzyK07cCJECkZCeRLNcoW6xzET7K7tYyWcWyhRPNZA6u2BIK3GCPDF4rSb4SVFxUaJaCHv8CJ5HYbJRAynTQZCog6iQze6XkvHgHHsJbpWPfLagqMfHmnMtknrwOcjsVRp2GL5ap4kCj7iPVbBYH0ssxlyzVgUHiHlPvdlOWWgIkNnUppqeTLQRtXVZA5jSzh57pcxk2OadmrDMJIgZDZD' \
  -H 'Content-Type: application/json' \
  -d '{ "messaging_product": "whatsapp", "to": "918767341918", "type": "template", "template": { "name": "hello_world", "language": { "code": "en_US" } } }'