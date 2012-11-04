REST API
********

GET /docs
    returns the latest 20 docs
    start: start at {start}
    batch_size: return {batch_size} items

GET /docs/{ID}
    returns the doc with id {ID}

PUT /docs
    add a new doc

POST /docs/{ID}
    update whatever attributes you want

DELETE /docs/{ID}
    delete the document with id {ID}

GET /docsdelete/{ID}
    delete the document with id {ID}

