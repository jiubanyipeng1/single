from oauth2client.service_account import ServiceAccountCredentials
import httplib2


## 网络问题，过不去，有时间再写

SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE = "谷歌验证.json"
credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)

http = credentials.authorize(httplib2.Http())

# Define contents here as a JSON string.
# This example shows a simple update request.
# Other types of requests are described in the next step.

content = {
  "url": "https://www.jiubanyipeng.com/689.html",
  "type": "URL_UPDATED"
}

response, content = http.request(ENDPOINT, method="POST", body=content)

print(response)