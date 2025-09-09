#===========================================================
# Family To-Do
# Mirai Hasegawa
#-----------------------------------------------------------
# To-Do list......
#===========================================================

from flask import Flask, render_template, request, flash, redirect, flash
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now
from app.helpers.images  import image_file


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
# @app.get("/")
# def index():
#         # Show them on the page
#     with connect_db() as client:
#         groups = client.execute("SELECT id, name, colour, picture FROM groups ORDER BY name ASC").rows
#         return render_template("pages/home.jinja")
    

#-----------------------------------------------------------
# Groups page route - show all the groups
#-----------------------------------------------------------
@app.get("/groups")
def show_groups():
    with connect_db() as client:
        # Get the details from the DB
        sql = "SELECT id, name, colour, picture_type FROM groups ORDER BY name ASC "
        result = client.execute(sql)
        groups = result.rows
        return render_template("pages/groups.jinja", groups=groups)


@app.get("/group/<int:id>/image")
def show_group_image(id):
    with connect_db() as client:
        sql = "SELECT picture_data, picture_type FROM groups WHERE id=? "
        result = client.execute(sql, [id])
    
        return image_file(result, "picture_data", "picture_type")


#-----------------------------------------------------------
# Route for adding a group
#-----------------------------------------------------------
@app.get("/groups/add")
def show_add_group():
    return render_template("pages/add-group.jinja")

@app.post("/groups/add")
def add_group():
    name = html.escape(request.form.get("name"))
    colour = request.form.get("colour")
    picture = request.files.get("picture")

    if picture:
        picture_data = picture.read()
        picture_type = picture.mimetype
    else:
        picture_data =  None

    with connect_db() as client:
        sql = "INSERT INTO groups (name, colour, picture_data, picture_type) VALUES (?, ?, ?, ?)"
        values = [name, colour, picture_data, picture_type]
        client.execute(sql, values)

    flash(f"group '{name}' added", "success.")
    return redirect("/groups")




#-----------------------------------------------------------
# Route for deleting a group, Id given in the route
#-----------------------------------------------------------
@app.get("/groups/<int:id>/delete")
def delete_group(id):
    with connect_db() as client:
        # Delete the tasks first
        client.execute("DELETE FROM tasks WHERE group_id=?", [id])
        client.execute("DELETE FROM groups WHERE id=?", [id])

    flash(f"Group deleted", "warning")
    return redirect("/groups")


#-----------------------------------------------------------
# Tasks page route - Show all the tasks
#-----------------------------------------------------------
@app.get("/groups/<int:group_id>/tasks")
def show_tasks(group_id):
    with connect_db() as client:
        sql = """
            SELECT id, name, description, colour, picture_type, priority FROM tasks WHERE group_id=?
            ORDER BY priority DESC
            """
        result = client.execute(sql, [group_id])
        tasks = result.rows

        sql_group = "SELECT id, name FROM groups WHERE id=?"
        group_result = client.execute(sql_group, [group_id])
        group = group_result.rows[0] if group_result.rows else None

        return render_template("pages/tasks.jinja", group=group, tasks=tasks)


@app.get("/group/<int:id>/tasks/image")
def show_task_image(id):
    with connect_db() as client:
        sql = "SELECT picture_data, picture_type FROM groups WHERE id=? "
        result = client.execute(sql, [id])
    
        return image_file(result, "picture_data", "picture_type")

#-----------------------------------------------------------
# Route for adding a Task, using data posted from a form
#-----------------------------------------------------------
@app.get("/tasks/add/<int:group_id>")
def show_add_task(group_id):
    return render_template("pages/add-task.jinja", group_id=group_id)

@app.post("/tasks/add")
def add_task(group_id):
    group_id = request.form.get("group_id")
    name = html.escape(request.form.get("name"))
    description = request.form.get("description")
    colour = request.form.get("colour")
    picture = request.files.get("picture")
    priority = request.form.get("priority")

    if picture:
        picture_data = picture.read()
        picture_type = picture.mimetype
    else:
        picture_data =  None

    with connect_db() as client:
        sql = """
            INSERT INTO tasks (group_id, name, description, colour, picture_data, picture_type, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        values = [group_id, name, description, colour, picture_data, picture_type, priority]
        client.execute(sql, values)

        flash(f"Task '{name}' added", "success")
        return redirect(f"/groups/{group_id}/tasks")
    

#-----------------------------------------------------------
# Route for editing a group
#-----------------------------------------------------------
@app.get("/groups/<int:id>/edit")
def show_edit_group(id):
    with connect_db() as client:
        group = client.execute("SELECT * FROM groups WHERE id=?", [id]).rows[0]
    return render_template("pages/edit-group.jinja", group=group)

@app.post("/groups/<int:id>/edit")
def edit_group(id):
    name = html.escape(request.form.get("name"))
    colour = request.form.get("colour")
    picture = request.form.get("picture")
    with connect_db() as client:
        client.execute(
            "UPDATE groups SET name=?, colour=?, picture=? WHERE id=?",
            [name, colour, picture, id]
        )
    flash(f"Group '{name}' updated", "success")
    return redirect("/groups")


#-----------------------------------------------------------
# Route for editing a task
#-----------------------------------------------------------
@app.get("/tasks/<int:id>/edit")
def show_edit_task(id):
    with connect_db() as client:
        task = client.execute("SELECT * FROM tasks WHERE id=?", [id]).rows[0]
    return render_template("pages/edit-task.jinja", task=task)

@app.post("/tasks/<int:id>/edit")
def edit_task(id):
    group_id = request.form.get("group_id")
    name = html.escape(request.form.get("name"))
    description = request.form.get("description")
    priority = int(request.form.get("priority"))
    colour = request.form.get("colour")
    picture = request.form.get("picture")
    with connect_db() as client:
        client.execute(
            "UPDATE tasks SET name=?, description=?, priority=?, colour=?, picture=? WHERE id=?",
            [name, description, priority, colour, picture, id]
        )
    flash(f"Task '{name}' updated", "success")
    return redirect(f"/groups/{group_id}/tasks")


#-----------------------------------------------------------
# Route for completing a task, Id given in the route
#-----------------------------------------------------------
@app.get("/complete/<int:id>")
def task_complete(id):
    with connect_db() as client:
        client.execute("UPDATE tasks SET complete=1 WHERE id=?",[id])
        group_id = client.execute("SELECT group_id FROM tasks WHERE id-?", [id]).rows[0]["group_id"]
    flash("Task marked as complete", "success")
    return redirect(f"/groups/{ group_id }/tasks")


#-----------------------------------------------------------
# Route for not completing a task, Id given in the route
#-----------------------------------------------------------
@app.get("/incomplete/<int:id>")
def task_incomplete(id):
    with connect_db() as client:
        client.execute("UPDATE tasks SET complete=0 WHERE id-?",[id])
        group_id = client.execute("SELECT group_id FROM tasks WHERE id-?", [id]).rows[0]["group_id"]
    flash("Task marked as incomplete")
    return redirect(f"/groups/{ group_id }/tasks")

#-----------------------------------------------------------
# Route for deleting a task, Id given in the route
#-----------------------------------------------------------
@app.get("/tasks/<int:id>/delete")
def delete_task(id):
    with connect_db() as client:
        group_id = client.execute("SELECT group_id FROM tasks WHERE id=?", [id]).rows[0]["group_id"]
        client.execute("DELETE FROM tasks WHERE id=?", [id])

    flash(f"Task deleted", "success.")
    return redirect(f"/groups/{group_id}/tasks")

#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")




