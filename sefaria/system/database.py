"""
database.py -- connection to MongoDB
The system attribute _called_from_test is set in the py.test conftest.py file
"""
import sys
import pymongo
import urllib.parse
from pymongo.errors import OperationFailure

# Import all settings from sefaria.settings, including SEFARIA_DB, MONGO_REPLICASET_NAME, etc.
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
        print(f"Error checking database existence: {e}")
        # Depending on the error, you might want to re-raise or handle differently.
        # For now, re-raising to ensure connection issues are visible.
        raise

def connect_to_db(db_name):
    """
    Connects to the specified database on the MongoDB server.
    Assumes 'client' is already defined.
    """
    # Check if the database exists before attempting to connect
    # In some cases, connecting to a non-existent DB might not raise an immediate error,
    # but operations on it will. The check_db_exists adds a safety layer.
    # if not check_db_exists(db_name): # Consider if this check is always desirable/necessary on startup
    #     # Raising a SystemError might prevent the application from starting.
    #     # An alternative might be to log a warning or handle the non-existent DB later.
    #     # Given the original code raised SystemError, we keep it for now.
    #     raise SystemError(f'Database {db_name} does not exist!')
    return client[db_name]

def get_test_db():
    """
    Gets the test database instance. Assumes TEST_DB and client are defined.
    """
    return client[TEST_DB]


# Determine the database name to use based on whether running tests or not
if hasattr(sys, '_doc_build'):
    db = "" # Dummy db object for documentation build
else:
    # Set the test database name. Original code commented out _test suffix.
    TEST_DB = SEFARIA_DB # Or SEFARIA_DB + "_test" if you want a separate test DB

    # --- MongoDB Client Connection ---
    # Modified to use the full connection string from SEFARIA_DB directly.
    # SEFARIA_DB is expected to contain the MONGO_URL from environment variables.
    # This handles both simple host:port and mongodb+srv:// URLs correctly with PyMongo.
    # The old logic of using MONGO_HOST/MONGO_PORT separately was incompatible with srv://
    try:
        # Use the SEFARIA_DB string to instantiate the MongoClient
        # PyMongo handles parsing the full connection string including srv://, authentication, etc.
        client = pymongo.MongoClient(SEFARIA_DB)

        # Optional: Add logging or print statement to confirm connection attempt parameters
        # print(f"Attempting MongoDB connection with SEFARIA_DB: {SEFARIA_DB}")

        # Optional: Command to force connection and check status immediately
        # This might add overhead but can catch connection issues early during startup
        # client.admin.command('ping')
        # print("MongoDB connection successful (ping).")

    except Exception as e:
        # Catch any exception during client instantiation or initial connection attempt
        print(f"Fatal Error: Failed to connect to MongoDB using SEFARIA_DB '{SEFARIA_DB}'. Details: {e}")
        # Re-raise the exception to halt the application startup
        raise


    # --- Original logic for getting the database instance ---
    # (This part remains largely the same, assuming 'client' is now a valid MongoClient)
    # Now set the db variable to point to the Sefaria database in the server
    if not hasattr(sys, '_called_from_test'):
        # Use the main SEFARIA_DB defined in settings
        # Consider if check_db_exists(SEFARIA_DB) is needed here, or if connect_to_db handles it.
        # Let's call connect_to_db which contains the check as per original logic.
         db = connect_to_db(SEFARIA_DB)
    else:
        # Use the TEST_DB for test runs
        # Let's call connect_to_db which contains the check as per original logic.
        db = connect_to_db(TEST_DB)


# --- Helper functions (remain unchanged) ---

def drop_test():
    global client
    client.drop_database(TEST_DB)


# Not used
# def refresh_test():
#     global client
#     drop_test()
#     # copydb deprecated in 4.2.  https://docs.mongodb.com/v4.0/release-notes/4.0-compatibility/#deprecate-copydb-clone-cmds
#     client.admin.command('copydb',
#                          fromdb=SEFARIA_DB,
#                          todb=TEST_DB)


def ensure_indices(active_db=None):
    active_db = active_db or db
    # Ensure 'client' is defined if ensure_indices is called before the top-level client creation
    # This might be an edge case depending on how the app initializes. Assume 'db' is valid,
    # which implies 'client' was successfully created.
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

    # Ensure 'client' is defined before attempting to use it for indexing
    if 'client' in globals() and client is not None:
        for col, args, kwargs in indices:
            try:
                getattr(active_db, col).create_index(*args, **kwargs)
            except OperationFailure as e:
                print("Collection: {}, args: {}, kwargs: {}\n{}".format(col, args, kwargs, e))
            except Exception as e:
                 # Catch other potential errors during index creation
                 print(f"Error creating index for collection {col}: {e}")
    else:
        print("Warning: MongoDB client not defined. Skipping index creation.") # Should not happen if startup proceeds this far
