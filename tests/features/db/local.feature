Feature: Managing local files
    In order to have some music in database
    As a music lover
    I want to get them added to the database

    Scenario: Add files to database
        Given I have some files in "data" directory
        And ignore "System Volume Information" directory
        And I have an empty database
        When I scan the directory for files
        Then they should get added to the database

    Scenario: Add some more files to database
        # Given I have existing database from previous scenario
        When I add some more files to the directory
        And I scan the directory for files again
        Then they should get added to the database

    Scenario: Rename an file
        # Given I have existing database from previous scenarios
        When I rename file "clockwork_test.mp3" to "sweet_hommie.mp3"
        And I scan the directory for files again
        Then they should be updated in the database

    Scenario: Change file tags without changing it's name
        # Given I have existing database from previous scenarios
        When I change tags for file "second_test.flac"
        And I scan the directory for files again
        Then they should be updated in the database
