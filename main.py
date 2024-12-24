from app import app, initialize_database

if __name__ == "__main__":
    # Initialize database before starting the server
    initialize_database()
    # Run the application
    app.run(host="0.0.0.0", port=5000)