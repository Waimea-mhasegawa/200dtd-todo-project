#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect, flash
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


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
@app.get("/")
def index():
        # Show them on the page
        return render_template("pages/home.jinja")
    

#-----------------------------------------------------------
# Groups page route - show all the groups
#-----------------------------------------------------------
@app.get("/groups")
def show_groups():
    with connect_db() as client:
        # Get the details from the DB
        sql = "SELECT id, name, colour, picture FROM groups ORDER BY name ASC "
        result = client.execute(sql)
        groups = result.rows
        return render_template("pages/groups.jinja", groups=groups)


#-----------------------------------------------------------
# Route for adding a group
#-----------------------------------------------------------
@app.post("/groups/add")
def add_group():
    name = html.escape(request.form.get("name"))
    colour = request.form.get("colour")
    picture = request.form.get("picture")

    with connect_db() as client:
        sql = "INSERT INTO groups (name, colour, picture) VALUES (?, ?, ?)"
        client.execute(sql,[name, colour, picture])

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

    flash(f"Group deleted", "success.")
    return redirect("/groups")


#-----------------------------------------------------------
# Tasks page route - Show all the tasks
#-----------------------------------------------------------
@app.get("/groups/<int:group_id>/tasks")
def show_tasks(group_id):
    with connect_db() as client:
        sql = """
            SELECT id, name, description, colour, picture, priority FROM tasks WHERE group_id=?
            ORDER BY priority DESC
            """
        result = client.execute(sql, [group_id])
        tasks = result.rows

        sql_group = "SELECT id, name FROM groups WHERE id=?"
        group_result = client.execute(sql_group, [group_id])
        group = group_result.rows[0] if group_result.rows else None

        return render_template("pages/tasks.jinja", group=group, tasks=tasks)


#-----------------------------------------------------------
# Route for adding a Task, using data posted from a form
#-----------------------------------------------------------
@app.post("/tasks/add")
def add_task():
    group_id = request.form.get("group_id")
    name = html.escape(request.form.get("name"))
    description = request.form.get("description")
    colour = request.form.get("colour")
    picture = request.form.get("picture")
    priority = request.form.get("priority")

    with connect_db() as client:
        sql = """
            INSERT INTO tasks (group_id, name, description, colour, picture, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        client.execute(sql, [group_id, name, description, colour, picture, priority])

        flash(f"Task '{name}' added", "success")
        return redirect(f"/groups/{group_id}/tasks")


#-----------------------------------------------------------
# Route for completing a task, Id given in the route
#-----------------------------------------------------------
@app.get("/complete/<int:id>")
def task_complete(id):
    with connect_db() as client:
        client.execute("UPDATE tasks SET complete=1 WHERE id=?",[id])
        flash("Task marked as complete", "success")
        return redirect(f"/groups/tasks")


#-----------------------------------------------------------
# Route for not completing a task, Id given in the route
#-----------------------------------------------------------
@app.get("/incomplete/<int:id>")
def task_incomplete(id):
    with connect_db() as client:
        client.execute("UPDATE tasks SET complete=0 WHERE id-?",[id])
        flash("Task marked as incomplete")
        return redirect(f"/groups/tasks")

#-----------------------------------------------------------
# Route for deleting a task, Id given in the route
#-----------------------------------------------------------
@app.get("/tasks<int:id>/delete")
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




