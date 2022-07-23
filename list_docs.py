import google_api

def ids():
    drive = google_api.connect("drive","v3")

    folderID = "1b71gdPxtsRUwp3ZW_x0_1QWKmY8mFa06"
    query = f"parents = '{folderID}'"

    response = drive.files().list(q=query).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive.files().list(q=query,pageToken=nextPageToken).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')
    
    id_list = []
    for file in files:
        id_list.append(file['id'])
    return id_list
