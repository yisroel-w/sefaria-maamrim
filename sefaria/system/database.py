"""
database.py -- connection to MongoDB
The system attribute _called_from_test is set in the py.test conftest.py file
"""
import sys
import pymongo
import urllib.parse
from pymongo.errors import OperationFailure, InvalidName

# Import all settings from sefaria.settings, including SEFARIA_DB, SEFARIA_DB_NAME, MONGO_REPLICASET_NAME, etc.
from sefaria.settings import *

def check_db_exists(db_name):
    """
    Checks if a database with the given name exists on the MongoDB server.
    Assumes 'client' is already defined.
    """
    # Use client.list_database_names() which requires authentication/connection
    try:
        dbnames = client.list_database_names()
        return db_name in dbnames
    except Exception as e:
        # Catch potential exceptions during list_database_names (e.g., connection issues)
        print(f"Error checking database existence for '{db_name}': {e}")
        # Re-raise the exception to indicate a problem
        raise

def connect_to_db(db_name):
    """
    Connects to the specified database on the MongoDB server.
    Assumes 'client' is already defined.
    db_name should be just the database name string, not a full URL.
    """
    # PyMongo's client[db_name] syntax handles the check for valid database names
    # and provides the database instance. The actual connection might be lazy.
    try:
        return client[db_name]
    except InvalidName as e:
        # Catch the specific InvalidName error if db_name contains invalid characters (like '.')
        print(f"Invalid database name '{db_name}'. Details: {e}")
        raise # Re-raise the specific error
    except Exception as e:
        # Catch any other potential errors when accessing the database instance
        print(f"Error accessing database '{db_name}': {e}")
        raise # Re-raise other errors

def get_test_db():
    """
    Gets the test database instance using the TEST_DB setting. Assumes client is defined.
    TEST_DB is expected to be just the database name string.
    """
    # Use the TEST_DB setting (expected to be a database name) to access the client
    return client[TEST_DB]


# --- MongoDB Client Connection ---
# This block runs when the module is imported.
# It creates the initial MongoClient instance using the full SEFARIA_DB string.
if hasattr(sys, '_doc_build'):
    # Dummy db object for documentation build
    db = ""
    # Dummy client for documentation build
    client = None # Define client to avoid NameError in ensure_indices check later
else:
    # Set the test database name. Use the SEFARIA_DB_NAME setting.
    # Original code commented out _test suffix. Let's use SEFARIA_DB_NAME for consistency.
    # TEST_DB = SEFARIA_DB + "_test" # Original example
    TEST_DB = SEFARIA_DB_NAME # Use the database name setting for the test DB name
    # Consider adding "_test" suffix here if you want a separate test database
    # TEST_DB = SEFARIA_DB_NAME + "_test"


    try:
        # Use the SEFARIA_DB string (expected to be the full MONGO_URL)
        # to instantiate the MongoClient. PyMongo handles parsing the srv:// format,
        # authentication details, replica sets (even when MONGO_REPLICASET_NAME is None
        # if the URL uses srv+), etc.
        # This replaces the old logic that used MONGO_HOST/MONGO_PORT or replica set URI construction.
        client = pymongo.MongoClient(SEFARIA_DB)

        # Optional: Add logging or print statement to confirm connection attempt parameters
        print(f"Attempting MongoDB connection with SEFARIA_DB URL: {SEFARIA_DB}")

        # Optional: Perform a quick check (like ping) to confirm the connection is active
        # This can help surface connection issues earlier during deployment
        # Note: ping requires authentication if auth is enabled on the DB
        try:
             # Attempt a simple command on the 'admin' database
             client.admin.command('ping')
             print("MongoDB connection successful (ping).")
        except Exception as ping_error:
             print(f"Warning: Ping command failed after connecting to MongoDB URL. Connection may still work, but check database access. Details: {ping_error}")


    except Exception as e:
        # Catch any exception during client instantiation or initial connection attempt
        # This is a fatal error for database connectivity.
        print(f"Fatal Error: Failed to instantiate MongoDB client using SEFARIA_DB URL '{SEFARIA_DB}'. Please check MONGO_URL environment variable and MongoDB Atlas network access. Details: {e}")
        # Re-raise the exception to halt the application startup and show the error in logs
        raise


    # --- Original logic for getting the database instance ---
    # (This part remains largely the same, but now uses SEFARIA_DB_NAME)
    # Now set the 'db' variable to point to the main Sefaria database instance from the client.
    # This uses the connect_to_db helper which expects just the database name.
    if not hasattr(sys, '_called_from_test'):
        # Use the main database name defined in settings (SEFARIA_DB_NAME)
         db = connect_to_db(SEFARIA_DB_NAME) # Use the new SEFARIA_DB_NAME setting here
         print(f"Connected to main MongoDB database: '{SEFARIA_DB_NAME}'")
    else:
        # Use the test database name (TEST_DB)
        db = connect_to_db(TEST_DB) # Use the TEST_DB setting here
        print(f"Connected to test MongoDB database: '{TEST_DB}'")


# --- Helper functions (remain unchanged, use 'client' and database names) ---

def drop_test():
    """
    Drops the test database. Assumes client is defined and TEST_DB is the database name.
    """
    global client
    # Use the TEST_DB setting (expected to be a database name)
    client.drop_database(TEST_DB)
    print(f"Dropped test MongoDB database: '{TEST_DB}'")


# Not used (refresh_test)
# def refresh_test():
#     global client
#     drop_test()
#     # copydb deprecated in 4.2.  https://docs.mongodb.com/v4.0/release-notes/4.0-compatibility/#deprecate-copydb-clone-cmds
#     client.admin.command('copydb',
#                          fromdb=SEFARIA_DB_NAME, # Use database name here
#                          todb=TEST_DB) # Use database name here


def ensure_indices(active_db=None):
    active_db = active_db or db
    # Ensure 'client' is defined and the active database is valid before attempting to create indices
    # This should be the case if startup reaches this point after successful connection and db selection.
    if 'client' in globals() and client is not None and active_db is not None:
        indices = [
            ('following', ["follower"],{}),
            ('following', ["followee"],{}),
            ('groups', ["name"], {}),
            ('groups', ["sheets"], {}),
            ('groups', ["slug"], {'unique': True}),
            ('groups', ["privateSlug"], {'unique': True}),
            ('groups', ["members"], {}),
            ('groups', ["admins"], {}),
            ('history', ["revision"],{}),
            ('history', ["method"],{}),
            ('history', [[("ref", pymongo.ASCENDING), ("version", pymongo.ASCENDING), ("language", pymongo.ASCENDING)]],{}),
            ('history', ["date"],{}),
            ('history', ["ref"],{}),
            ('history', ["user"],{}),
            ('history', ["rev_type"],{}),
            ('history', ["version"],{}),
            ('history', ["new.refs"],{}),
            ('history', ["new.ref"],{}),
            ('history', ["old.refs"],{}),
            ('history', ["old.ref"],{}),
            ('history', ["title"],{}),
            ('index', ["title"],{}),
            ('index_queue', [[("lang", pymongo.ASCENDING), ("version", pymongo.ASCENDING), ("ref", pymongo.ASCENDING)]],{'unique': True}),
            ('index', ["categories.0"], {}),
            ('index', ["order.0"], {}),
            ('index', ["order.1"], {}),
            # ('links', [[("refs.0",  1), ("refs.1", 1)]], {"unique": True}), # Note: This was commented out in original
            ('links', [[("refs", pymongo.ASCENDING), ("generated_by", pymongo.ASCENDING)]],{}),
            ('links', ["refs.0"],{}),
            ('links', ["refs.1"],{}),
            ('links', ["expandedRefs0"],{}),
            ('links', ["expandedRefs1"],{}),
            ('links', ["source_text_oid"],{}),
            ('links', ["is_first_comment"],{}),
            ('links', ["inline_citation"],{}),
            ('metrics', ["timestamp"], {'unique': True}),
            ('media', ["ref.sefaria_ref"], {}),
            ('notes', [[("owner", pymongo.ASCENDING), ("ref", pymongo.ASCENDING), ("public", pymongo.ASCENDING)]],{}),
            ('notifications', [[("uid", pymongo.ASCENDING), ("read", pymongo.ASCENDING)]],{}),
            ('notifications', ["uid"],{}),
            ('notifications', ["content.sheet_id"], {}),
            ('parshiot', ["date"],{}),
            ('place', [[("point", pymongo.GEOSPHERE)]],{}),
            ('place', [[("area", pymongo.GEOSPHERE)]],{}),
            ('person', ["key"],{}),
            ('profiles', ["slug"],{}),
            ('profiles', ["id"],{}),
            ('sheets', ["id"],{}),
            ('sheets', ["dateModified"],{}),
            ('sheets', ["sources.ref"],{}),
            ('sheets', ["includedRefs"],{}),
            ('sheets', ["expandedRefs"], {}),
            ('sheets', ["tags"],{}),
            ('sheets', ["owner"],{}),
            ('sheets', ["assignment_id"],{}),
            ('sheets', ["is_featured"],{}),
            ('sheets', ["displayedCollection"], {}),
            ('sheets', ["sheetLanguage"], {}),
            ('sheets', [[("views", pymongo.DESCENDING)]],{}),
            ('sheets', ["categories"], {}),
            ('links', [[("owner", pymongo.ASCENDING), ("date_modified", pymongo.DESCENDING)]], {}),
            ('texts', ["title"],{}),
            ('texts', [[("priority", pymongo.DESCENDING), ("_id", pymongo.ASCENDING)]],{}),
            ('texts', [[("versionTitle", pymongo.ASCENDING), ("langauge", pymongo.ASCENDING)]],{}),
            ('texts', ["actualLanguage"], {}),
            ('topics', ["titles.text"], {}),
            ('topic_links', ["class"], {}),
            ('topic_links', ["expandedRefs"], {}),
            ('topic_links', ["toTopic"], {}),
            ('topic_links', ["fromTopic"], {}),
            ('word_form', ["form"],{}),
            ('word_form', ["c_form"],{}),
            ('word_form', ["refs"], {}),
            ('term', ["titles.text"], {'unique': True}),
            ('term', ["category"],{}),
            ('lexicon_entry', [[("headword", pymongo.ASCENDING), ("parent_lexicon", pymongo.ASCENDING)]],{}),
            ('user_story', ["uid"],{}),
            ('user_story', [[("uid", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]],{}),
            ('user_story', [[("timestamp", pymongo.DESCENDING)]],{}),
            ('passage', ["ref_list"],{}),
            ('user_history', ["uid"],{}),
            ('user_history', ["sheet_id"],{}),
            ('user_history', ["datetime"],{}),
            ('user_history', ["ref"], {}),
            ('user_history', [[("time_stamp", pymongo.DESCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("server_time_stamp", pymongo.ASCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("saved", pymongo.ASCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("ref", pymongo.ASCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("book", pymongo.ASCENDING), ("last_place", pymongo.ASCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("secondary", pymongo.ASCENDING), ("last_place", pymongo.ASCENDING), ("time_stamp", pymongo.ASCENDING)]], {}),
            ('user_history', [[("uid", pymongo.ASCENDING), ("secondary", pymongo.ASCENDING), ("time_stamp", pymongo.ASCENDING)]], {}),
            ('trend', ["name"],{}),
            ('trend', ["uid"],{}),
            ('webpages', ["refs"],{}),
            ('webpages', ["expandedRefs"],{}),
            ('manuscript_pages', ['expanded_refs'], {}),
            ('manuscript_pages', [[("manuscript_slug", pymongo.ASCENDING), ("page_id", pymongo.ASCENDING)]], {'unique': True}),
            ('manuscripts', ['slug'], {}),
            ('manuscripts', ['title'], {}),
            ('messages', [[("room_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]], {}),
            ('vstate', ["title"], {}),
            ('vstate', ["flags.enComplete"], {}),
        ]

        for col, args, kwargs in indices:
            try:
                getattr(active_db, col).create_index(*args, **kwargs)
            except OperationFailure as e:
                # Specific handling for OperationFailure (e.g., permission issues)
                print("OperationFailure creating index for collection: {}, args: {}, kwargs: {}\n{}".format(col, args, kwargs, e))
            except Exception as e:
                 # Catch other potential errors during index creation
                 print(f"Error creating index for collection {col}: {e}")
    else:
        # This block should ideally not be reached in a successful startup after MongoDB connection
        print("Warning: Skipping index creation because MongoDB client or active database is not defined.")
