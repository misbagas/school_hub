from school_hub import create_app

# Create the app instance using the app factory pattern
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
