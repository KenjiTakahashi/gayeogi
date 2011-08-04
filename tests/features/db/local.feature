Feature: Local filesystem support
    In order to have some music in database
    As a music lover
    I want to get them added to the database

    Scenario: Add files to database
        Given I have an empty database
        And I have some files in "data" directory
        And ignore "System Volume Information" directory
        When I scan the directory for files
        Then they should get added to the database
