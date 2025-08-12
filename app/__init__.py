#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect
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
    with connect_db() as client:
        # Get all todo things from SQ
        sql = "SELECT group, name from todo ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        todo = result.rows

        # Show them on the page
        return render_template("pages/home.jinja")
    

#-----------------------------------------------------------
# Todo page route
#-----------------------------------------------------------
@app.get("/todo/<group>")
def show_todo_details(group):
    with connect_db() as client:
        # Get the details from the DB
        sql = "SELECT group, name, priority FROM todo WHERE group "


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("//")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM things ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, price FROM things WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a todo, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_todo():
    # Get the data from the form
    group = request.form.get("group")
     
    print(group)

    # Sanitise the text inputs
    group = html.escape(group)

    with connect_db() as client:
        # Add the todo to the DB
        sql = """
            INSERT INTO todo (group) 
            VALUES (?)
        """
        params = [group]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Todo '{group}' added", "success")
        return redirect("/")
    

#-----------------------------------------------------------
# Route for adding a team, using data posted from a form
#-----------------------------------------------------------

@app.post("/add-todo")
def add_a_todo():
    # Get the data from the form
    type = request.form.get("type")
    name  = request.form.get("name")
    priority = request.form.get("priority")

    # Sanitise the text inputs
    name = html.escape(name)
    priority = html.escape(priority)

    with connect_db() as client:
        # Add the todo thing to the DB
        sql = """
            INSERT INTO things (type, name, priority)
            VALUES (?, ?, ?)
        """
        params = [type, name, priority]
        client.execute(sql,params)

        # Go back to the home page
        flash(f"Todo '{name}' added", "success")
        return redirect(f"/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")


