from flask import g, app
from utils import id_generator
import os

def exists(rId):
    g.cur.execute("""
    SELECT EXISTS(
      SELECT *
      FROM resources
      WHERE id=%s)
    """, rId)
    r = g.cur.fetchone()
    return True if r == 1 else False
    
def new(f, cId):
    # get existing resource ids & generate the id
    g.cur.execute("""
    SELECT resource_id
    FROM card_resources
    """)
    existing = g.cur.fetchall()
    resource_id = id_generator(size=8, existing=existing)
    
    # save the file into the resource directory
    ext = os.path.splitext(f.filename)[1]
    dest = os.path.join(app.config['RESOURCE_DIRECTORY'], resource_id, ext)
    outfile = open(dest, mode="w")
    outfile.write(f.read())
    # add the resource to the resources table
    g.cur.execute("""
    INSERT
    INTO resources(cId, resource_id, name, path)
    VALUES(%s, %s, %s, %s)""", (cId, resource_id, f.filename, dest))
    g.db.commit()
    return (g.cur.lastrowid, resource_id)

def delete(rId):
    g.cur.execute("""
    DELETE
    FROM resources
    WHERE id=%s""", rId)
    return g.cur.rowcount

    
    
